import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("Запуск скрапинга")

url = "https://www.airlineratings.com/airlines"
driver = webdriver.Chrome()
driver.get(url)

records = []
page = 1

try:
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for row in soup.select("table tbody tr"):
            cols = [td.get_text(strip=True) for td in row.select("td")]
            if len(cols) >= 5:
                records.append(tuple(cols[:5]))

        logging.info(f"Страница {page} обработана (всего {len(records)})")

        next_btn = driver.find_element(By.CSS_SELECTOR, 'li[data-slot="next"]')
        if next_btn.get_attribute("aria-disabled") == "true":
            break

        driver.execute_script("arguments[0].click();", next_btn)
        page += 1
        time.sleep(2)

except Exception as e:
    logging.error(f"Ошибка: {e}")

finally:
    driver.quit()

df = pd.DataFrame(records, columns=[
    "Name", "Country", "Passenger Rating", "Product Rating", "Safety Rating"
])
df.to_csv("airlines_full.csv", index=False, encoding="utf-8-sig")

logging.info(f"Собрано {len(df)} записей с {page} страниц.")
logging.info("=== Скрапинг завершён ===")