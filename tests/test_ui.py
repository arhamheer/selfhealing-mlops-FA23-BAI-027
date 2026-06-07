import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

APP_URL = "http://100.50.10.159:32500"


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
        time.sleep(2)

        # Find elements by their fixed IDs
        text_input = driver.find_element(By.ID, "text-input")
        submit_btn = driver.find_element(By.ID, "submit-btn")

        # Send test sentence
        text_input.send_keys("The cinematography was breathtaking and the performances were outstanding")

        # Click submit
        submit_btn.click()

        # Wait for result
        wait = WebDriverWait(driver, 15)
        result_element = wait.until(
            EC.presence_of_element_located((By.ID, "result-output"))
        )
        time.sleep(3)

        result_text = result_element.text

        # Assert non-empty and contains expected keywords
        assert result_text != "", "Result output is empty"
        assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"]), \
            f"Result does not contain expected keywords: {result_text}"
    finally:
        driver.quit()
