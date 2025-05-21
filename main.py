import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *

def setup_driver():
    #Настройка драйвера с опциями
    try:
        chrome_options = Options()
        
        if HEADLESS:
            chrome_options.add_argument('--headless')
        
        if PROXY:
            chrome_options.add_argument(f'--proxy-server=http://{PROXY}')
        
        # Базовые настройки
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        
        # Отключение уведомлений и менеджера паролей
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument("--guest")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('--user-data-dir=/tmp/chrome-temp-profile')

      
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5) 
        return driver
    except Exception as e:
        logger.error(f"Ошибка при инициализации драйвера: {str(e)}")
        raise


def human_like_delay(min_sec=1, max_sec=3):
    #Случайная задержка между действиями для имитации поведения человека
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def move_to_element(driver, element):
    #Плавное перемещение курсора к элементу
    try:
        action = ActionChains(driver)
        action.move_to_element(element).perform()
        delay = human_like_delay()
        logger.debug(f"Перемещение к элементу, задержка {delay:.2f} сек")
        return True
    except Exception as e:
        logger.warning(f"Не удалось переместиться к элементу: {str(e)}")
        return False

def human_like_scroll(driver):
    #Имитация человеческого скролла
    try:
        scroll_actions = random.randint(2, 5)
        logger.debug(f"Начало скролла ({scroll_actions} действий)")
        for _ in range(scroll_actions):
            if random.choice([True, False]):
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                logger.debug("Скролл вниз")
            else:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                logger.debug("Скролл вверх")
            human_like_delay(0.5, 1.5)
        return True
    except Exception as e:
        logger.warning(f"Ошибка при скролле: {str(e)}")
        return False


def login_user(driver):
    #Авторизация пользователя из config.py
    try:
        logger.info("Начало авторизации пользователя")
        driver.get(TARGET_URL)
        
        # Ввод логина
        username = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'user-name'))
        )
        move_to_element(driver, username)
        username.clear()
        username.send_keys(DEFAULT_USERNAME)
        logger.debug(f"Введен логин: {DEFAULT_USERNAME}")
        human_like_delay()
        
        # Ввод пароля
        password = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        move_to_element(driver, password)
        password.clear()
        password.send_keys(DEFAULT_PASSWORD)
        logger.debug("Введен пароль")
        human_like_delay()
        
        # Клик по кнопке входа
        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'login-button'))
        )
        move_to_element(driver, login_btn)
        login_btn.click()
        logger.info("Успешный вход в систему")
 
        # Дополнительная проверка на всплывающие окна
        try:
            driver.execute_script("document.querySelector('button.error-button').click()")
            logger.info("Закрыто окно через JS")
        except:
            logger.debug("Не удалось закрыть окно через JS")

        # Проверка успешного входа
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'inventory_list'))
        )
        logger.debug("Страница продуктов загружена")
        return True
    except Exception as e:
        logger.error(f"Ошибка при авторизации: {str(e)}")
        driver.save_screenshot('login_error.png')
        return False

def simulate_user_behavior(driver):
    # Имитация поведения пользователя после входа
    try:
        logger.info("Начало имитации пользовательского поведения")

        # Скролл страницы
        human_like_scroll(driver)

        # Просмотр товаров
        items = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'inventory_item'))
        )
        logger.debug(f"Найдено {len(items)} товаров")

        if items:
            random_item = random.choice(items)

            # Перемещение к товару
            if move_to_element(driver, random_item):
                # Извлечение и логирование названия товара
                item_name_el = random_item.find_element(By.CLASS_NAME, 'inventory_item_name')
                item_name = item_name_el.text
                logger.info(f"Просмотр товара: {item_name}")
                human_like_delay()

                # Клик по имени товара (ссылке)
                move_to_element(driver, item_name_el)
                item_name_el.click()
                logger.info("Переход на страницу товара")
                human_like_delay()

                # Ждём загрузки страницы товара
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'inventory_details_name'))
                )
                logger.info("Страница товара успешно загружена")

        return True

    except Exception as e:
        logger.error(f"Ошибка при имитации поведения: {str(e)}", exc_info=True)
        driver.save_screenshot('behavior_error.png')
        return False

    
def main():
    driver = None
    try:
        driver = setup_driver()
        logger.info("Драйвер успешно инициализирован")
        
        # Авторизация
        if login_user(driver):
            # Имитация поведения пользователя
            simulate_user_behavior(driver)
            
            # Сохранение скриншота
            driver.save_screenshot(SCREENSHOT_PATH)
            logger.info(f"Скриншот сохранен как {SCREENSHOT_PATH}")
        else:
            logger.error("Не удалось выполнить авторизацию")
    except Exception as e:
        logger.error(f"Произошла критическая ошибка: {str(e)}", exc_info=True)
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Драйвер закрыт")
            except Exception as e:
                logger.warning(f"Ошибка при закрытии драйвера: {str(e)}")

if __name__ == "__main__":
    main()