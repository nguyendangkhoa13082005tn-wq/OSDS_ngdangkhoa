from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

# Tạo dataframe rỗng
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# Khởi tạo WebDriver
driver = webdriver.Chrome()

# Mở trang
url = "https://en.wikipedia.org/wiki/Edvard_Munch"
driver.get(url)

# Đợi trang tải
time.sleep(2)

# Lấy tên họa sĩ
try:
    name = driver.find_element(By.TAG_NAME, "h1").text
except:
    name = ""


# Lấy ngày sinh

try:
    birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
    birth_text = birth_element.text

    # Regex lấy năm hoặc ngày/tháng/năm
    birth = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4}", birth_text)[0]
except:
    birth = ""

# Lấy ngày mất
try:
    death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
    death_text = death_element.text

    death = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4}", death_text)[0]
except:
    death = ""

# Lấy quốc tịch
try:
    nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
    nationality = nationality_element.text
except:
    nationality = ""

# Tạo dictionary thông tin của họa sĩ
painter = {
    'name': name,
    'birth': birth,
    'death': death,
    'nationality': nationality
}

# Chuyển dictionary thành DataFrame
painter_df = pd.DataFrame([painter])

# Thêm vào DF chính
d = pd.concat([d, painter_df], ignore_index=True)

# In kết quả
print(d)

# Đóng WebDriver
driver.quit()
