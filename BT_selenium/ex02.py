from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd

# Đường dẫn đến file thực thi geckodriver (Đã bị loại bỏ nếu dùng PATH)
# gecko_path = r"D:/MaNguonMo/PracticeGeckoDriver/geckodriver-v0.35.0-win64/geckodriver.exe"

# Khởi tởi đối tượng dịch vụ với đường geckodriver (Đã bị loại bỏ nếu dùng PATH)
# ser = Service(gecko_path)

# Tạo tùy chọn (Bắt buộc phải có trước khi khởi tạo driver)
options = webdriver.firefox.options.Options();
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
# Thiết lập firefox chỉ hiện thị giao diện
options.headless = False

# Khởi tạo driver
# Sử dụng Biến Môi trường PATH (Đã bỏ service=ser)
driver = webdriver.Firefox(options=options)

# Tạo url
url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'

# Truy cập
driver.get(url)

# Tạm dừng khoảng 2 giây
time.sleep(1)

# Tìm phần tử body của trang để gửi phím mũi tên xuống
body = driver.find_element(By.TAG_NAME, "body")
time.sleep(3)

for k in range(10):
    try:
        # Lấy tất cả các button trên trang
        buttons = driver.find_elements(By.TAG_NAME, "button")

        # Duyệt qua từng button
        for button in buttons:
            # Kiểm tra nếu nội dung của button chứa "Xem thêm" và "sản phẩm"
            if "Xem thêm" in button.text and "sản phẩm" in button.text:
                # Di chuyển tới button và click

                # Sử dụng JavaScript click (ổn định hơn)
                driver.execute_script("arguments[0].click();", button)
                # button.click()

                time.sleep(2)  # Chờ nội dung mới tải
                break  # Thoát khỏi vòng lặp nếu đã click thành công

            # Nếu không tìm thấy button nào trong lần lặp này
        else:
            print(f"Lần lặp {k + 1}: Không tìm thấy nút 'Xem thêm'. Dừng lặp.")
            break

    except Exception as e:
        print(f"Lỗi: {e}")
        break

# Nhấn phím mũi tên xuống nhiều lần để cuộn xuống từ từ
for i in range(50):  # Lặp 50 lần, mỗi lần cuộn xuống một ít
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.01)  # Tạm dừng 0.01 giây giữa mỗi lần cuộn để trang tải nội dung

# Tạm dừng thêm vài giây để trang tải hết nội dung ở cuối trang
time.sleep(1)

# Tao cac list
stt = []
ten_san_pham = []
gia_ban = []
hinh_anh = []

# Tìm tất cả các button có nội dung là "Chọn mua"
buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")

print(f"Tổng số nút 'Chọn mua' tìm thấy: {len(buttons)}")

# lay tung san pham
for i, bt in enumerate(buttons, 1):
    # Quay ngược 3 lần để tìm div cha
    parent_div = bt
    # Cần tìm container cha chứa toàn bộ thông tin sản phẩm
    try:
        # Giả định container sản phẩm là cha thứ 3 của nút "Chọn mua"
        for _ in range(3):
            parent_div = parent_div.find_element(By.XPATH, "./..")  # Quay ngược 1 lần

        sp = parent_div

        # Lat ten sp
        try:
            tsp = sp.find_element(By.TAG_NAME, 'h3').text
        except NoSuchElementException:
            tsp = ''

        # Lat gia sp
        try:
            gsp = sp.find_element(By.CLASS_NAME, 'text-blue-5').text
        except NoSuchElementException:
            gsp = ''

        # Lat hinh anh
        try:
            ha = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except NoSuchElementException:
            ha = ''

        # Chi them vao ds neu co ten sp
        if (len(tsp) > 0):
            stt.append(i)
            ten_san_pham.append(tsp)
            gia_ban.append(gsp)
            hinh_anh.append(ha)

    except NoSuchElementException:
        # Bỏ qua nếu không tìm được div cha thứ 3 (cấu trúc HTML đã thay đổi)
        continue

# Tạo df
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_san_pham,
    "Giá bán": gia_ban,
    "Hình ảnh": hinh_anh

})

df.to_excel('danh_sach_sp_3.xlsx', index=False)
print(f"Đã thu thập và xuất thành công {len(stt)} sản phẩm ra file 'danh_sach_sp_3.xlsx'.")

# Đóng driver
driver.quit()