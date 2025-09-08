import logging
import os
import sys
import argparse

from src.client import create_opensearch_client, wait_for_es
from tasks import create_index, index_samples, search_by_word

logging.basicConfig(
    filename='app.log',               # путь к файлу
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def run():
    client = create_opensearch_client()
    # Ждём готовности кластера перед выполнением операций
    if not wait_for_es(client, timeout=120, interval=2):
        # Не удалось дождаться — прекращаем работу, чтобы избежать исключений на create/index
        logger.critical("Exiting: OpenSearch is not reachable.")
    create_index(client)
    index_samples(client)
    # keyword = input("Enter the search word:") # К примеру: OpenSearch
    # logger.info(f"The user made a request: {keyword}")
    # content_type = input("Enter content type:") # К примеру: article | news | blog
    # logger.info(f"The user made a request: {content_type}")
    result = search_by_word(client, keyword="OpenSearch", content_type="article")

    if len(result) == 0:
        print("Nothing was found for your query.")
    else:
        print("Search result:")
        for res in result:
            print(f"\ntitle:\n  {res.get('title')}\nsnippet:\n  {res.get('snippet')}")


def cli():
    # если нужен простой CLI с аргументами
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.once:
        run()
    else:
        # цикл/демон/планировщик по необходимости
        run()

if __name__ == "__main__":
    cli()


# def prompt_keyword(default=None):
#     """Запрашивает ключевое слово у пользователя только если есть TTY.
#     Иначе возвращает default."""
#     if sys.stdin is None or not sys.stdin.isatty():
#         return default
#     try:
#         kw = input("Enter the search word (press Enter to use default): ").strip()
#         return kw if kw else default
#     except EOFError:
#         return default
#
#
# def prompt_content_type(default=None):
#     """Запрашивает content_type у пользователя только если есть TTY.
#     Иначе возвращает default."""
#     if sys.stdin is None or not sys.stdin.isatty():
#         return default
#     try:
#         ct = input("Enter the content type (press Enter to use default): ").strip()
#         return ct if ct else default
#     except EOFError:
#         return default
#
#
# def run(keyword=None, content_type=None, interactive=False):
#     client = create_opensearch_client()
#
#     if not wait_for_es(client, timeout=120, interval=2):
#         logger.critical("Exiting: OpenSearch is not reachable.")
#         return
#
#     create_index(client)
#     index_samples(client)
#
#     # Если режим интерактивный (и TTY доступен) — принудительно спрашиваем оба значения.
#     if interactive and sys.stdin is not None and sys.stdin.isatty():
#         keyword = prompt_keyword(default=keyword or os.environ.get("KEYWORD") or "OpenSearch")
#         content_type = prompt_content_type(default=content_type or os.environ.get("CONTENT_TYPE") or "article")
#     else:
#         # Обычное поведение: используем аргументы -> env -> интерактив (если TTY и значение не задано)
#         if not keyword:
#             keyword = prompt_keyword(default=os.environ.get("KEYWORD")) or "OpenSearch"
#         if not content_type:
#             content_type = prompt_content_type(default=os.environ.get("CONTENT_TYPE")) or "article"
#
#     result = search_by_word(client, keyword=keyword, content_type=content_type)
#
#     if len(result) == 0:
#         print("Nothing was found for your query.")
#     else:
#         print("Search result:")
#         for res in result:
#             print(f"\ntitle:\n  {res.get('title')}\nsnippet:\n  {res.get('snippet')}")
#
#
# def cli():
#     parser = argparse.ArgumentParser(description="App for demo search")
#     parser.add_argument("--keyword", "-k", help="Keyword for search (overrides env KEYWORD)")
#     parser.add_argument("--content-type", "-t", help="Content type filter (overrides env CONTENT_TYPE)")
#     parser.add_argument("--interactive", "-i", action="store_true",
#                         help="Force interactive prompts (prompts for both keyword and content_type if TTY available)")
#     parser.add_argument("--once", action="store_true", help="Run once and exit")
#     args = parser.parse_args()
#
#     if args.once:
#         run(keyword=args.keyword, content_type=args.content_type, interactive=args.interactive)
#     else:
#         # пока просто запускаем один раз; можно добавить цикл/таймер при необходимости
#         run(keyword=args.keyword, content_type=args.content_type, interactive=args.interactive)
#
#
# if __name__ == "__main__":
#     cli()
