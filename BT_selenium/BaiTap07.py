

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# CẤU HÌNH DRIVER
chrome_options = Options()
# Khôi phục các cột cần thiết, bao gồm Link Wikipedia
df = pd.DataFrame(columns=['University Name', 'Code/Acronym', 'Wikipedia Link'])
base_url = 'https://vi.wikipedia.org'

url = 'https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_t%E1%BA%A1i_Vi%E1%BB%87t_Nam'

print(f"BẮT ĐẦU CÀO DỮ LIỆU TÊN, MÃ TRƯỜNG, VÀ LINK: {url}...")

# --- KHỞI TẠO DRIVER VÀ TẢI TRANG ---
try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "wikitable")))
    print("Đã tải trang thành công.")
except Exception as e:
    print(f"Lỗi khi khởi tạo hoặc tải trang: {e}")
    exit()

# --- CÀO DỮ LIỆU TỪ TẤT CẢ CÁC BẢNG ---
total_scraped_count = 0
try:
    all_tables = driver.find_elements(By.CLASS_NAME, 'wikitable')

    if not all_tables:
        print("Không tìm thấy bảng dữ liệu (wikitable).")
        exit()

    for table_index, table in enumerate(all_tables):

        if len(table.find_elements(By.TAG_NAME, 'tr')) < 3:
            continue

        print(f"\n--- Xử lý Bảng #{table_index + 1} ---")

        rows = table.find_elements(By.TAG_NAME, 'tr')
        data_rows = rows[1:]

        for i, row in enumerate(data_rows):
            cells = row.find_elements(By.XPATH, './td | ./th')

            # Yêu cầu TỐI THIỂU 3 cột (STT, Tên, Mã)
            if len(cells) < 3:
                continue

            # --- TRÍCH XUẤT DỮ LIỆU CỐT LÕI (Tên và Link) ---
            name = ""
            link = ""

            try:
                # 1. Tên trường và Link Wikipedia (Cột 2, index 1)
                name_cell = cells[1]
                name_tag = name_cell.find_element(By.TAG_NAME, 'a')

                # Tên trường
                raw_name = name_tag.text.strip()
                name = re.sub(r'(\(TP\.\s*HCM\)|\(Đắk Lắk\)|\([A-Z]+\))', '', raw_name).strip()
                name = re.sub(r'\s{2,}', ' ', name).strip()

                # Link Wikipedia (FIXED: Đảm bảo xây dựng link đúng)
                link_href = name_tag.get_attribute('href')
                link = base_url + link_href if link_href and link_href.startswith('/wiki/') else ""

            except NoSuchElementException:
                # Nếu không phải là trường, bỏ qua hàng này
                continue

            # --- TRÍCH XUẤT DỮ LIỆU THỨ CẤP ---
            try:
                # 2. Mã trường/Tên tắt (Cột 3, index 2)
                code_name = cells[2].text.strip().split('\n')[0].replace(',', '').strip()



                # Thêm vào DataFrame (chỉ khi tìm thấy Tên trường từ thẻ <a>)
                if len(name) > 10:
                    new_row = pd.DataFrame([{
                        'University Name': name,
                        'Code/Acronym': code_name,
                        'Wikipedia Link': link
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)

                    print(f"Đã cào: {name} | Link: {link}")
                    total_scraped_count += 1

            except Exception as e:
                # Lỗi trong quá trình trích xuất Mã trường
                continue

except Exception as e:
    print(f"Lỗi lớn khi tìm và xử lý bảng: {e}")

finally:
    driver.quit()

# --- XUẤT KẾT QUẢ ---
print("\nHOÀN TẤT! Đã cào xong danh sách trường đại học Việt Nam.")
print(f"Tổng cộng: {len(df)} trường.")

output_file = "Vietnamese_Universities_Data.xlsx"
df.to_excel(output_file, index=False)
print(f"Đã lưu dữ liệu vào file: {output_file}")

print("\n10 dòng dữ liệu mẫu:")
print(df.head(10))