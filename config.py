import logging

# Конфигурация
PROXY = None  # 'ip:port' или 'user:pass@ip:port' если нужно использовать прокси
HEADLESS = False  # Если нужно отключаем headless для отладки
SCREENSHOT_PATH = 'final_screen.png'  # Путь для сохранения скриншота
TARGET_URL = 'https://www.saucedemo.com/'

# Учетные данные
DEFAULT_USERNAME = 'standard_user'
DEFAULT_PASSWORD = 'secret_sauce'


# Настройка логирования (INFO, DEBUG, ERROR)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
