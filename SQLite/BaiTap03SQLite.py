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
import sqlite3

# Tạo tùy chọn Firefox
options = webdriver.firefox.options.Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
options.headless = False   # Hiện giao diện

# Khởi tạo driver (đã dùng PATH)
driver = webdriver.Firefox(options=options)

# URL
url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'
driver.get(url)
time.sleep(1)

body = driver.find_element(By.TAG_NAME, "body")
time.sleep(3)

# Nhấn nút Xem thêm
for k in range(10):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        found = False
        for button in buttons:
            if "Xem thêm" in button.text and "sản phẩm" in button.text:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                found = True
                break

        if not found:
            print(f"Lần lặp {k+1}: Không tìm thấy nút.")
            break

    except Exception as e:
        print("Lỗi:", e)
        break

# Cuộn xuống
for i in range(50):
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.01)

time.sleep(1)

# Thu thập dữ liệu
stt = []
ten_san_pham = []
gia_ban = []
hinh_anh = []

buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")
print("Tổng số sản phẩm tìm thấy:", len(buttons))

for i, bt in enumerate(buttons, 1):
    parent_div = bt
    try:
        for _ in range(3):
            parent_div = parent_div.find_element(By.XPATH, "./..")

        sp = parent_div

        # Tên sản phẩm
        try:
            tsp = sp.find_element(By.TAG_NAME, 'h3').text
        except:
            tsp = ''

        # Giá bán
        try:
            gsp = sp.find_element(By.CLASS_NAME, 'text-blue-5').text
        except:
            gsp = ''

        # Hình ảnh
        try:
            ha = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except:
            ha = ''

        if len(tsp) > 0:
            stt.append(i)
            ten_san_pham.append(tsp)
            gia_ban.append(gsp)
            hinh_anh.append(ha)

    except:
        continue

driver.quit()

# Tạo DataFrame
df = pd.DataFrame({
    "id": stt,
    "name": ten_san_pham,
    "price": gia_ban,
    "image": hinh_anh
})

print("Thu thập xong:", len(df), "sản phẩm")



# II. LƯU VÀO DATABASE SQLITE

conn = sqlite3.connect("longchau_products.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER,
    name TEXT,
    price TEXT,
    image TEXT
)
""")

df.to_sql("products", conn, if_exists="replace", index=False)

conn.commit()
print("Đã lưu vào SQLite: longchau_products.db")



# III. TRUY VẤN SQL MẪU

DATABASE_NAME = "longchau_products.db"
TABLE = "products"
# Chuỗi SQL để chuyển đổi giá từ text (ví dụ: '110.000 VNĐ') sang số (REAL)
PRICE_CLEAN_SQL = "CAST(REPLACE(REPLACE(price, '.', ''), ' VNĐ', '') AS REAL)"

try:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    print("\nA. Thống kê & Toàn cục")

    # 1. Tổng số sản phẩm
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE};")
    print("1. Tổng số sản phẩm:", cursor.fetchone()[0])

    # 2. 5 sản phẩm đầu
    print("\n2. 5 sản phẩm đầu tiên:")
    cursor.execute(f"SELECT * FROM {TABLE} LIMIT 5;")
    # Chú ý: Cần thêm xử lý nếu không có dữ liệu
    try:
        df_top5 = pd.DataFrame(cursor.fetchall(), columns=["ID", "Name", "Price", "Image"])
        print(df_top5)
    except:
        print("Không có dữ liệu trong bảng.")

    # 3. 10 giá bán khác nhau
    print("\n3. 10 giá bán khác nhau:")
    cursor.execute(f"""
        SELECT DISTINCT price
        FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        LIMIT 10;
    """)
    print([row[0] for row in cursor.fetchall()])

    print("\nB. Lọc & Tìm kiếm")

    # 4. Sản phẩm bắt đầu bằng chữ 'V'
    cursor.execute(f"""
        SELECT name FROM {TABLE}
        WHERE name LIKE 'V%'
        LIMIT 5;
    """)
    print("\n4. Sản phẩm bắt đầu bằng V:", [row[0] for row in cursor.fetchall()])

    # 5. Sản phẩm có chữ 'Vitamin'
    cursor.execute(f"""
        SELECT name, price FROM {TABLE}
        WHERE name LIKE '%Vitamin%';
    """)
    print("\n5. Sản phẩm chứa 'Vitamin':")
    print(cursor.fetchall())

    # 6. Sản phẩm không có giá
    cursor.execute(f"""
        SELECT name FROM {TABLE}
        WHERE price IS NULL OR price = ''
        LIMIT 5;
    """)
    print("\n6. Sản phẩm không có giá:", [row[0] for row in cursor.fetchall()])

    # --------------------------------------------------------------------------------------------------------------------
    print("\n--- PHẦN TIẾP THEO ---")
    print("\nC. Phân tích Giá (Sử dụng chuyển đổi giá sang số)")

    # 7. Sản phẩm rẻ nhất
    cursor.execute(f"""
        SELECT name, price FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        ORDER BY {PRICE_CLEAN_SQL} ASC
        LIMIT 1;
    """)
    print("\n7. Sản phẩm RẺ NHẤT:", cursor.fetchone())

    # 8. Sản phẩm đắt nhất
    cursor.execute(f"""
        SELECT name, price FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        ORDER BY {PRICE_CLEAN_SQL} DESC
        LIMIT 1;
    """)
    print("\n8. Sản phẩm ĐẮT NHẤT:", cursor.fetchone())

    # 9. Giá bán trung bình
    cursor.execute(f"""
        SELECT AVG({PRICE_CLEAN_SQL}) FROM {TABLE}
        WHERE price IS NOT NULL AND price != '';
    """)
    avg_price = cursor.fetchone()[0]
    print(f"\n9. Giá bán Trung bình: {avg_price:,.0f} VNĐ")

    # 10. Đếm số lượng sản phẩm theo nhóm giá (Dưới 50k, 50k-100k, Trên 100k)
    print("\n10. Thống kê theo Nhóm giá:")
    cursor.execute(f"""
        SELECT
            CASE
                WHEN {PRICE_CLEAN_SQL} < 50000 THEN '1. Dưới 50K'
                WHEN {PRICE_CLEAN_SQL} BETWEEN 50000 AND 100000 THEN '2. 50K - 100K'
                ELSE '3. Trên 100K'
            END AS nhom_gia,
            COUNT(*) AS so_luong
        FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        GROUP BY nhom_gia
        ORDER BY nhom_gia;
    """)
    df_price_groups = pd.DataFrame(cursor.fetchall(), columns=["Nhóm Giá", "Số Lượng"])
    print(df_price_groups)

    print("\nD. Sắp xếp & Trích xuất Dữ liệu")

    # 11. 5 sản phẩm đắt nhất (chi tiết)
    print("\n11. 5 sản phẩm ĐẮT NHẤT (chi tiết):")
    cursor.execute(f"""
        SELECT id, name, price FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        ORDER BY {PRICE_CLEAN_SQL} DESC
        LIMIT 5;
    """)
    df_top5_expensive = pd.DataFrame(cursor.fetchall(), columns=["ID", "Name", "Price"])
    print(df_top5_expensive)

    # 12. Sắp xếp 5 sản phẩm rẻ nhất
    print("\n12. 5 sản phẩm RẺ NHẤT (sắp xếp):")
    cursor.execute(f"""
        SELECT name, price FROM {TABLE}
        WHERE price IS NOT NULL AND price != ''
        ORDER BY {PRICE_CLEAN_SQL} ASC
        LIMIT 5;
    """)
    print(cursor.fetchall())

    # 13. Sản phẩm có tên chứa 'viên'
    cursor.execute(f"""
        SELECT name, price FROM {TABLE}
        WHERE name LIKE '%viên%';
    """)
    print("\n13. Sản phẩm có chứa 'viên':")
    print(cursor.fetchall())

    # 14. Đếm số lượng sản phẩm thiếu URL hình ảnh
    cursor.execute(f"""
        SELECT COUNT(*) FROM {TABLE}
        WHERE image IS NULL OR image = '';
    """)
    print("\n14. Số sản phẩm thiếu URL hình ảnh:", cursor.fetchone()[0])

    # 15. Liệt kê sản phẩm trùng lặp (nếu có)
    print("\n15. Liệt kê sản phẩm trùng lặp:")
    cursor.execute(f"""
        SELECT name, COUNT(*) AS so_luong_trung_lap
        FROM {TABLE}
        GROUP BY name
        HAVING COUNT(*) > 1;
    """)
    df_duplicates = pd.DataFrame(cursor.fetchall(), columns=["Name", "Count"])
    print(df_duplicates)


except sqlite3.Error as e:
    print(f"\nLỖI KẾT NỐI/TRUY VẤN DATABASE: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("\nHOÀN TẤT TOÀN BỘ!")


















