import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

APP_URL = os.environ.get("APP_URL", "http://100.50.10.159:32500")


def test_frontend_sentiment():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(APP_URL)
        time.sleep(3)

        text_input = driver.find_element(By.ID, "text-input")
        submit_btn = driver.find_element(By.ID, "submit-btn")

        text_input.send_keys("The cinematography was breathtaking and the performances were outstanding")
        submit_btn.click()

        # Wait for result to be non-empty
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: d.find_element(By.ID, "result-output").text.strip() != "")

        result_text = driver.find_element(By.ID, "result-output").text
        assert result_text != "", "Result output is empty"
        assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"]), \
            f"Result does not contain expected keywords: {result_text}"
    finally:
        driver.quit()
