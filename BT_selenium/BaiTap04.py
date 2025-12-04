from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Khởi tạo WebDriver
driver = webdriver.Chrome()

for i in range(65, 91):
    url = f"https:\\en.wikipedia.org/wiki/list of painters by name beginning with %22{chr(i)}%22"
    try:
        # Mở trang
        driver.get(url)

        # Đợi chút để trang tải
        time.sleep(2)

        # Lấy ra tất cả các thẻ <ul>
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        print(len(ul_tags))

        # Chọn thẻ <ul> chứa danh sách họa sĩ
        ul_painters = ul_tags[20]

        # Lấy ra tất cả các thẻ <li> thuộc ul_painters
        li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

        # Tạo danh sách tiêu đề (title)
        titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title") for tag in li_tags]

        # In ra tiêu đề
        for title in titles:
            print(title)
    except Exception as e:
        print(f"Error: {e}")

# Đóng webdriver
driver.quit()


