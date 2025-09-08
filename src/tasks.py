import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(
    filename='src.log',
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
INDEX = os.getenv("INDEX")


def create_index(client):
    """
    Создаёт индекс с базовой настройкой и mapping'ом, если индекс ещё не существует.

    Поведение:
    - number_of_shards = 1, number_of_replicas = 0 (подходящее для локальной разработки)
    - mapping для полей: title (text + keyword multi-field), content (text), content_type (keyword)
    - игнорирует ошибку 400 (index already exists)
    """
    body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "content": {"type": "text"},
                "content_type": {"type": "keyword"}
            }
        }
    }
    print(ADMIN_PASSWORD, HOST, PORT, INDEX)
    # indices.create возвращает ответ сервера — здесь мы игнорируем статус 400 (уже существует).
    client.indices.create(index=INDEX, body=body, ignore=400)
    logger.info("Index '%s' created (or already exists).", INDEX)


def index_samples(client):
    """
    Индексирует несколько тестовых документов в индекс.

    Логика:
    - Проверяем наличие документа по id с помощью client.exists(index, id)
    - Если документ отсутствует — индексируем его (client.index)
    - Для production/больших объёмов использовать client.bulk()
    """
    docs = [
        {"title": "Обзор OpenSearch", "content": "OpenSearch — открытый движок поиска.", "content_type": "article"},
        {"title": "Python и OpenSearch", "content": "В python есть библиотека для работы с OpenSearch — opensearch-py",
         "content_type": "article"},
        {"title": "Новости проекта", "content": "Вышел новый релиз OpenSearch.", "content_type": "news"},
        {"title": "Блог пост", "content": "Как настроить индекс в OpenSearch.", "content_type": "blog"}
    ]

    counter = 0
    for i, doc in enumerate(docs, start=1):
        # client.exists — быстрый способ проверить наличие документа по id
        if not client.exists(index=INDEX, id=i):
            # refresh=True сразу делает документ видимым для поиска — удобен в демо, но замедляет индексирование.
            client.index(index=INDEX, id=i, body=doc, refresh=True)
            logger.info('Added a document: %s', doc["title"])
            counter += 1
        else:
            logger.debug('Document id=%s already exists, skipping.', i)

    logger.info("Documents submitted for indexing: %d", len(docs))
    logger.info("Documents indexed: %d", counter)


def search_by_word(client, keyword, content_type=None, size=10):
    """
    Выполняет поиск по keyword в полях 'title' и 'content'.
    Если content_type задан (например 'article'|'news'|'blog'|'other'), возвращает только такие документы.
    Возвращаемый формат: [{'title': ..., 'snippet': ...}, ...]
    """
    # Базовый запрос: ищем в title и content
    must_clause = {
        'multi_match': {
            'query': keyword,
            'fields': ['title^2', 'content'],
            "type": "best_fields"
        }

    }

    bool_query = {"must": [must_clause]}

    # Добавляем фильтр по content_type, если указан
    if content_type:
        bool_query["filter"] = [{"term": {"content_type": content_type}}]

    query = {
        "query": {"bool": bool_query},
        "_source": ["title", "content"],
        "size": size
    }

    result = client.search(index=INDEX, body=query)
    hits = result.get("hits", {}).get("hits", [])

    results = []
    for hit in hits:
        src = hit.get("_source", {})
        title = src.get("title", "")
        content = src.get("content", "") or ""
        snippet = content[:50]  # первые 50 символов
        results.append({"title": title, "snippet": snippet})

    if results:
        logger.info("Response to your request: %s", results)
        return results
    else:
        logger.info("Nothing was found for your query.")
        return []
