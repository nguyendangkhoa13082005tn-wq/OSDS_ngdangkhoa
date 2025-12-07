import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os
import random


## I. Cấu hình và Chuẩn bị Database


DB_FILE = 'Painters_Data_Limited.db'
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
    try:
        if driver:
            driver.quit()
    except:
        pass



# II. Lấy Đường dẫn (URLs) cho A đến Z (GIỚI HẠN 100)


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


# III. Cào thông tin & LƯU TRỮ TỨC THỜI


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


# IV. Phân tích Dữ liệu và Đóng kết nối
DB_NAME = "Painters_Data_Limited.db"
TABLE = "painters_infor"

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("\n NHÓM 1: KIỂM TRA DỮ LIỆU BAN ĐẦU ")

    # 1. Đếm tổng số họa sĩ
    print("\n1. Tổng số họa sĩ trong bảng:")
    cursor.execute(f"""
        SELECT COUNT(name) AS So_hoa_sy
        FROM {TABLE}
    """)
    total_painters = cursor.fetchone()[0]
    print("→ Tổng số họa sĩ:", total_painters)

    # 2. Hiển thị 5 dòng đầu tiên
    print("\n2. 5 dòng dữ liệu đầu tiên:")
    cursor.execute(f"""
        SELECT * FROM {TABLE}
        LIMIT 5
    """)
    df_head = pd.DataFrame(cursor.fetchall(), columns=["name", "birth", "death", "nationality"])
    print(df_head)

    # 3. Quốc tịch duy nhất
    print("\n3. Các quốc tịch duy nhất:")
    cursor.execute(f"""
        SELECT DISTINCT nationality
        FROM {TABLE}
        WHERE nationality IS NOT NULL AND nationality != ''
    """)
    unique_nat = [row[0] for row in cursor.fetchall()]
    print(unique_nat)

    print("\n NHÓM 2: LỌC & TÌM KIẾM ")

    # 4. Tên họa sĩ bắt đầu bằng 'F'
    print("\n4. Họa sĩ có tên bắt đầu bằng chữ 'F':")
    cursor.execute(f"""
        SELECT name 
        FROM {TABLE}
        WHERE name LIKE 'F%'
    """)
    painters_F = cursor.fetchall()
    print(painters_F[:10], "... (hiển thị 10 dòng đầu)")

    # 5. Quốc tịch chứa từ 'French'
    print("\n5. Họa sĩ có quốc tịch chứa 'French':")
    cursor.execute(f"""
        SELECT name, nationality
        FROM {TABLE}
        WHERE nationality LIKE '%French%'
    """)
    df_french = pd.DataFrame(cursor.fetchall(), columns=["name", "nationality"])
    print(df_french)

    # 6. Họa sĩ không có thông tin quốc tịch
    print("\n6. Họa sĩ không có quốc tịch:")
    cursor.execute(f"""
        SELECT name
        FROM {TABLE}
        WHERE nationality IS NULL OR nationality = ''
    """)
    missing_nat = cursor.fetchall()
    print("→ Số lượng:", len(missing_nat))
    print(missing_nat[:10])

    # 7. Họa sĩ có đủ birth + death
    print("\n7. Họa sĩ có cả ngày sinh và ngày mất:")
    cursor.execute(f"""
        SELECT name
        FROM {TABLE}
        WHERE birth IS NOT NULL AND birth != ''
          AND death IS NOT NULL AND death != ''
    """)
    both_dates = cursor.fetchall()
    print("→ Số lượng:", len(both_dates))
    print(both_dates[:10])

    # 8. Họa sĩ có tên chứa 'Fales'
    print("\n8. Họa sĩ có tên chứa 'Fales':")
    cursor.execute(f"""
        SELECT *
        FROM {TABLE}
        WHERE name LIKE '%Fales%'
    """)
    df_fales = pd.DataFrame(cursor.fetchall(), columns=["name", "birth", "death", "nationality"])
    print(df_fales)

    print("\n NHÓM 3: NHÓM & SẮP XẾP ")

    # 9. Sắp xếp tên theo A-Z
    print("\n9. Danh sách họa sĩ (A → Z):")
    cursor.execute(f"""
        SELECT name
        FROM {TABLE}
        ORDER BY name ASC
    """)
    df_sorted = pd.DataFrame(cursor.fetchall(), columns=["name"])
    print(df_sorted.head(20))

    # 10. Nhóm theo quốc tịch
    print("\n10. Thống kê số lượng họa sĩ theo quốc tịch:")
    cursor.execute(f"""
        SELECT nationality, COUNT(*) AS so_luong
        FROM {TABLE}
        WHERE nationality IS NOT NULL AND nationality != ''
        GROUP BY nationality
        ORDER BY so_luong DESC
    """)
    df_nat_count = pd.DataFrame(cursor.fetchall(), columns=["nationality", "so_luong"])
    print(df_nat_count)

except Exception as e:
    print("Lỗi khi truy vấn dữ liệu:", e)

finally:
    if conn:
        conn.close()
        print("\nĐã đóng kết nối CSDL.")

# Đóng kết nối cuối cùng
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")