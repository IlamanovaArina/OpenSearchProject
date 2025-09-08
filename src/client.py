import os
import logging
import time

from opensearchpy import OpenSearch


logging.basicConfig(
    filename='app.log',               # путь к файлу
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    filemode='a',                     # 'a' — добавлять, 'w' — перезаписывать
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
# HOST = os.getenv("HOST")
# PORT = os.getenv("PORT")
# INDEX = os.getenv("INDEX")

HOST = "opensearch"
PORT = 9200
INDEX = "my_index"
ADMIN_PASSWORD = "ArinA_ArinA1"


def create_opensearch_client():
    """Создает и возвращает OpenSearch client на основе конфигурации.

    Поддерживается базовая HTTP-аутентификация (user/password).
    """
    client = OpenSearch(
        hosts=[{"host": "opensearch", "port": 9200, "scheme": "https"}],
        http_auth=("admin", "ADMIN_PASSWORD"),
        use_ssl=True,
        verify_certs=False,     # только для локальной отладки
        ssl_show_warn=False,
        timeout=30
    )

    # client = OpenSearch(
    #     hosts=[{"host": "opensearch", "port": 9200, "scheme": "http"}],
    #     http_auth=None,  # если нет auth
    #     use_ssl=False,
    #     timeout=30
    # )
    logger.info("Клиент создан")
    return client

def wait_for_es(client, timeout=120, interval=2):
    """
    Ждём, пока OpenSearch начнёт отвечать на ping().
    Возвращает True, если доступен, иначе False.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            if client.ping():
                logger.info("OpenSearch is available.")
                return True
        except Exception as e:
            # Логируем на уровне DEBUG/INFO, чтобы видеть прогресс при необходимости
            logger.debug("OpenSearch ping failed (will retry): %s", e)
        time.sleep(interval)
    logger.error("OpenSearch did not become available within %s seconds.", timeout)
    return False
