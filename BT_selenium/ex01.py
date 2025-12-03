from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# Đường dẫn đến GeckoDriver của bạn
gecko_path = r"D:/MaNguonMo/PracticeGeckoDriver/geckodriver-v0.35.0-win64/geckodriver.exe"
ser = Service(gecko_path)

options = webdriver.firefox.options.Options()


options.binary_location = r"C:/Program Files/Mozilla Firefox/firefox.exe"

options.headless = False

# Khởi tạo WebDriver
driver = webdriver.Firefox(options=options)
url = 'http://pythonscraping.com/pages/javascript/ajaxDemo.html'
driver.get(url)

print("Before: \n")
print(driver.page_source)

time.sleep(3)

print("\n\n\n\nAfter: \n")
print(driver.page_source)

driver.quit()
