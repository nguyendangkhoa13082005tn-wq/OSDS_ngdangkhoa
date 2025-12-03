from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# CẤU HÌNH
# Sử dụng cấu hình Biến Môi trường PATH
options = webdriver.firefox.options.Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.headless = False

# Thông tin đăng nhập
USERNAME_OR_EMAIL = "........"
PASSWORD = "................"
URL = "https://apps.lms.hutech.edu.vn/authn/login"

# KHỞI TẠO DRIVER
try:
    print("Đang khởi động trình duyệt...")
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)  # Thiết lập chờ tối đa 10 giây
except Exception as e:
    print(f"LỖI: Không tìm thấy GeckoDriver hoặc Firefox. Lỗi: {e}")
    exit()

# 1. TRUY CẬP TRANG WEB
print(f"Truy cập: {URL}")
driver.get(URL)
time.sleep(3)

# 2. TÌM VÀ ĐIỀN THÔNG TIN
try:
    # 2a. Tìm ô Mã số sinh viên/Email
    # ID: emailOrUsername
    username_field = wait.until(
        EC.presence_of_element_located((By.ID, "emailOrUsername"))
    )
    username_field.send_keys(USERNAME_OR_EMAIL)
    print("Đã điền Mã số sinh viên/Email.")

    # 2b. Tìm ô Mật khẩu
    # ID: password
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(PASSWORD)
    print("Đã điền Mật khẩu.")

    time.sleep(2)

    # 2c. Tìm nút Đăng nhập
    # ID: sign-in
    login_button = driver.find_element(By.ID, "sign-in")

    # 2d. Click nút Đăng nhập
    login_button.click()
    print("Đang cố gắng đăng nhập...")

except NoSuchElementException as e:
    print(f"LỖI: Không tìm thấy phần tử đăng nhập. Kiểm tra lại ID. Lỗi chi tiết: {e}")
except TimeoutException:
    print("LỖI: Thời gian chờ tải trang quá lâu.")

# 3. KIỂM TRA KẾT QUẢ
time.sleep(5)
print("Hoàn thành quá trình tương tác.")

