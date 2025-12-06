import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os
import random

######################################################
## I. Cấu hình và Chuẩn bị Database
######################################################

DB_FILE = 'Painters_Data_Limited.db'  # Đổi tên file để phân biệt
TABLE_NAME = 'painters_infor'
all_links = []
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Xóa file DB cũ nếu muốn
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY,
    birth TEXT,
    death TEXT,
    nationality TEXT
);
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")


def safe_quit_driver(driver):
    """Hàm đóng driver an toàn."""
    try:
        if driver:
            driver.quit()
    except:
        pass


######################################################
## II. Lấy Đường dẫn (URLs) cho A đến Z (GIỚI HẠN 100)
######################################################

LIMIT_PER_CHAR = 100  # Giới hạn tối đa 100 họa sĩ cho mỗi chữ cái
print(f"\n--- Bắt đầu Lấy Đường dẫn (A-Z, Giới hạn {LIMIT_PER_CHAR} người/ký tự) ---")
driver_link = None

try:
    driver_link = webdriver.Chrome(options=chrome_options)
    base_url = 'https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22'

    # Lặp qua ký tự 'A' (65) đến 'Z' (90)
    for i in range(65, 91):
        char = chr(i)
        url = base_url + char + '%22'
        driver_link.get(url)
        time.sleep(2)

        print(f"Đang xử lý ký tự: {char}")

        content = driver_link.find_element(By.ID, "mw-content-text")
        all_uls = content.find_elements(By.TAG_NAME, "ul")

        if all_uls:
            main_ul = max(all_uls, key=lambda ul: len(ul.find_elements(By.TAG_NAME, "li")))
            li_tags = main_ul.find_elements(By.TAG_NAME, "li")

            links = []
            for li in li_tags:
                try:
                    a_tag = li.find_element(By.TAG_NAME, "a")
                    href = a_tag.get_attribute("href")
                    if href and "/wiki/" in href and "List_of_painters" not in href:
                        if href.startswith('/wiki/'):
                            href = 'https://en.wikipedia.org' + href
                        links.append(href)
                except:
                    continue

            # ÁP DỤNG GIỚI HẠN SỐ LƯỢNG (100)
            links_to_add = links[:LIMIT_PER_CHAR]
            all_links.extend(links_to_add)
            print(f"  -> Đã thêm {len(links_to_add)} link.")

        time.sleep(random.uniform(1, 3))

except Exception as e:
    print(f"Lỗi khi lấy links: {e}")
finally:
    safe_quit_driver(driver_link)

print(f"\nHoàn tất lấy đường dẫn. Tổng cộng {len(all_links)} links đã tìm thấy.")

######################################################
## III. Cào thông tin & LƯU TRỮ TỨC THỜI
######################################################

print("\n--- Bắt đầu Cào và Lưu Trữ Dữ liệu Họa sĩ ---")
count = 0
total = len(all_links)
driver_scrape = None

try:
    # Khởi tạo driver CHỈ MỘT LẦN cho phần cào chi tiết
    driver_scrape = webdriver.Chrome(options=chrome_options)

    for link in all_links:
        count += 1
        print(f"[{count}/{total}] Đang xử lý: {link}")

        driver_scrape.get(link)
        time.sleep(random.uniform(0.5, 1.5))  # Độ trễ ngẫu nhiên

        # 1. Lấy tên họa sĩ
        try:
            name = driver_scrape.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            name = ""

        # 2. Lấy ngày sinh (Born)
        try:
            birth_element = driver_scrape.find_element(By.XPATH,
                                                       "//th[contains(translate(text(),'BORN','born'),'born')]/following-sibling::td")
            birth = birth_element.text
            birth_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""

        # 3. Lấy ngày mất (Died)
        try:
            death_element = driver_scrape.find_element(By.XPATH,
                                                       "//th[contains(translate(text(),'DIED','died'),'died')]/following-sibling::td")
            death = death_element.text
            death_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death)
            death = death_match[0] if death_match else ""
        except:
            death = ""

        # 4. Lấy quốc tịch (Nationality)
        try:
            nationality_element = driver_scrape.find_element(By.XPATH,
                                                             "//th[contains(translate(text(),'NATIONALITY','nationality'),'nationality')]/following-sibling::td")
            nationality = nationality_element.text.split('\n')[0].strip()
        except:
            nationality = ""

        # 5. LƯU TỨC THỜI VÀO SQLITE
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) 
        VALUES (?, ?, ?, ?);
        """
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()
        print(f"  --> Đã lưu thành công: {name}")

except Exception as e:
    print(f"Lỗi khi xử lý hoặc lưu họa sĩ {link}: {e}")
finally:
    safe_quit_driver(driver_scrape)

print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")

######################################################
## IV. Phân tích Dữ liệu và Đóng kết nối
######################################################

# Đóng kết nối cuối cùng
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")