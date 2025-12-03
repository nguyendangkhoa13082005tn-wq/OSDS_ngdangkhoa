from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# 1. CẤU HÌNH TRÌNH DUYỆT



options = webdriver.firefox.options.Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.headless = False

try:
    print("Đang khởi động trình duyệt...")
    # Khởi tạo driver KHÔNG CÓ THAM SỐ service
    driver = webdriver.Firefox(options=options)
except Exception as e:
    print("LỖI: Không tìm thấy GeckoDriver hoặc Firefox. Vui lòng kiểm tra PATH.")
    print(e)
    exit()

wait = WebDriverWait(driver, 10)

# 2. TRUY CẬP GOCHEK
url = 'https://gochek.vn/collections/all'
driver.get(url)
print("Đang truy cập Gochek...")
time.sleep(3)

# 3. TẮT POPUP
try:
    close_btn = driver.find_element(By.CSS_SELECTOR,
                                    "#close-popup, .modal-close, button.close-window, .popup-close, .close")
    driver.execute_script("arguments[0].click();", close_btn)
    print("Đã đóng popup quảng cáo.")
    time.sleep(1)
except:
    pass

# --- 4. CUỘN TRANG (Quan trọng để tải ảnh) ---
print("Đang cuộn trang để tải ảnh...")
body = driver.find_element(By.TAG_NAME, "body")
for i in range(15):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.3)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(1)

# 5. LẤY DỮ LIỆU
stt = []
ten_san_pham = []
gia_ban = []
hinh_anh = []

product_cards = driver.find_elements(By.CLASS_NAME, "product-block")
print(f"Tìm thấy {len(product_cards)} sản phẩm.")

for i, card in enumerate(product_cards, 1):
    try:
        # Lấy Tên
        try:
            tsp = card.find_element(By.CSS_SELECTOR, "h3.pro-name a").text.strip()
        except:
            tsp = ''

        # Lấy Giá (FIXED: Chỉ lấy giá hiện tại)
        try:
            gsp_element = card.find_element(By.CSS_SELECTOR, ".box-pro-prices .pro-price.highlight")

            # Chỉ lấy SPAN đầu tiên (chứa giá hiện tại)
            try:
                gsp = gsp_element.find_element(By.TAG_NAME, 'span').text.strip()
            except:
                gsp = gsp_element.text.strip()

            # Làm sạch dữ liệu: loại bỏ ký tự thừa
            gsp = gsp.split('==')[0].strip()
            gsp = re.sub(r'\s+', ' ', gsp).strip()

        except:
            gsp = 'Liên hệ'

        # Lấy Ảnh (FIXED: Ưu tiên src/data-src)
        try:
            img_tag = card.find_element(By.CSS_SELECTOR, ".box-pro-img img")

            ha = None

            # 1. Ưu tiên lấy 'src' (link đã tải đầy đủ)
            if img_tag.get_attribute('src'):
                ha = img_tag.get_attribute('src')
            # 2. Nếu không có 'src', thử lấy 'data-src'
            elif img_tag.get_attribute('data-src'):
                ha = img_tag.get_attribute('data-src')

            # 3. Xử lý link thiếu https://
            if ha and ha.startswith("//"):
                ha = "https:" + ha
            elif ha and not ha.startswith("http"):
                ha = "https://gochek.vn" + ha

                # Làm sạch nếu link là base64
            if ha and "base64" in ha:
                ha = ''

        except:
            ha = ''

        if tsp:
            stt.append(i)
            ten_san_pham.append(tsp)
            gia_ban.append(gsp)
            hinh_anh.append(ha)
            print(f"Đã lấy: {tsp} - Giá: {gsp} - Ảnh: {ha[:50]}...")

    except:
        continue

# 6. XUẤT EXCEL
if len(stt) > 0:
    df = pd.DataFrame({
        "STT": stt,
        "Tên sản phẩm": ten_san_pham,
        "Giá bán": gia_ban,
        "Hình ảnh": hinh_anh
    })
    df.to_excel('products_gochek.xlsx', index=False)
    print("Hoàn thành! File excel đã được tạo.")
else:
    print("Không lấy được sản phẩm nào. Kiểm tra lại web.")

