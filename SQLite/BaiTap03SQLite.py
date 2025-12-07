
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import sqlite3
import re

options = Options()
options.binary_location = r"C:/Program Files/Mozilla Firefox/firefox.exe"
options.headless = False

driver = webdriver.Firefox(options=options)
driver.maximize_window()

driver.get("https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat")
time.sleep(5)

# BƯỚC 1: NHẤN HẾT NÚT "XEM THÊM"
print("Bước 1: Nhấn hết nút Xem thêm...")
for k in range(50):
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
            break
    except Exception as e:
        print(f"   Lỗi nhấn nút: {e}")
        break

# BƯỚC 2: CUỘN XUỐNG CUỐI ĐỂ LOAD HẾT
print("Bước 2: Cuộn xuống cuối trang.")
body = driver.find_element(By.TAG_NAME, "body")
for i in range(100):
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.05)
time.sleep(2)

print("Đã cuộn xong – chuẩn bị thu thập!\n")

# BƯỚC 3: THU THẬP DỮ LIỆU
print("Bắt đầu thu thập dữ liệu...")
data = []

buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Chọn mua')]")
print(f"Đã phát hiện {len(buttons)} sản phẩm trên trang\n")

for i, bt in enumerate(buttons, 1):
    try:
        # Lên 3 cấp parent để lấy card sản phẩm
        parent_div = bt
        for _ in range(3):
            parent_div = parent_div.find_element(By.XPATH, "./..")
        sp = parent_div

        # 1. Tên sản phẩm
        try:
            product_name = sp.find_element(By.TAG_NAME, 'h3').text.strip()
        except:
            product_name = ""

        # 2. Link sản phẩm (từ thẻ a trong card)
        try:
            link_elem = sp.find_element(By.TAG_NAME, "a")
            product_url = link_elem.get_attribute('href')
        except:
            product_url = ""

        # 3. Giá bán (text → số)
        try:
            gsp = sp.find_element(By.CLASS_NAME, 'text-blue-5').text.strip()
            price_vnd = int(re.sub(r"[^\d]", "", gsp)) if gsp else None
        except:
            price_vnd = None

        # 4. Đơn vị tính – cải thiện regex + lấy từ thẻ nhỏ
        unit = ""
        try:
            # Lấy thẻ mô tả nhỏ dưới tên (nếu có)
            unit_elem = sp.find_element(By.XPATH, ".//p[contains(@class,'text-xs') or contains(@class,'text-gray')]")
            unit = unit_elem.text.strip()
            unit = re.sub(r"^\d+\s*", "", unit)  # bỏ số đầu
            unit = unit.split("\n")[0].strip()
            if len(unit) > 60 or "giảm" in unit.lower() or "mua" in unit.lower():
                unit = ""
        except:
            pass

        # Nếu không có → trích từ tên sản phẩm (chính xác cao)
        if not unit:
            patterns = [
                r"(hộp|lọ|chai|vỉ|tuýp|gói|hũ|ống|túi)\s*[\d\.,]+\s*(viên|ml|g|tablet|que|viên nang|viên nén)",
                r"[\d\.,]+\s*(viên|ml|g|ống|que|hộp|chai|lọ|vỉ|tablet)\b",
                r"\b[\d\.,]+\s*(viên|ml|g|ống|hộp|chai|lọ|vỉ)"
            ]
            for p in patterns:
                match = re.search(p, product_name, re.I)
                if match:
                    unit = match.group(0).strip()
                    break

        if not unit:
            unit = None

        # Chỉ thêm nếu có tên
        if len(product_name) > 0:
            data.append({
                "id": i,
                "product_name": product_name,
                "price_vnd": price_vnd,
                "unit": unit,
                "product_url": product_url
            })

        if i % 50 == 0:
            print(f"   Đã xử lý {i}/{len(buttons)} sản phẩm...")

    except Exception as e:
        print(f"   Lỗi tại sản phẩm {i}: {e}")
        continue

driver.quit()

# XỬ LÝ CUỐI & KIỂM TRA AN TOÀN
if not data:
    print("Không thu thập được sản phẩm nào!")
else:
    df = pd.DataFrame(data)

    # Loại bỏ trùng lặp theo URL
    if len(df) > 0:
        df.drop_duplicates(subset=["product_url"], keep="first", inplace=True)
        df.reset_index(drop=True, inplace=True)
        df["id"] = df.index + 1

        # Kiểm tra cột tồn tại trước khi sắp xếp
        required_cols = ["id", "product_name", "price_vnd", "unit", "product_url"]
        existing_cols = [col for col in required_cols if col in df.columns]
        df = df[existing_cols]

    print(f"\nHOÀN TẤT THU THẬP: {len(df)} sản phẩm duy nhất")
    print(f"   Có giá bán      : {df['price_vnd'].notna().sum() if 'price_vnd' in df.columns else 0}")
    print(f"   Có đơn vị tính  : {df['unit'].notna().sum() if 'unit' in df.columns else 0}")

    # In 15 dòng đầu để kiểm tra
    print("\n15 sản phẩm đầu tiên:")
    print(df.head(15)[["id", "product_name", "price_vnd", "unit"]].to_string(index=False))

    # Lưu database
    DB_NAME = "longchau_vitamin.db"
    conn = sqlite3.connect(DB_NAME)
    df.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()

    print(f"\nĐÃ LƯU {len(df)} SẢN PHẨM VÀO FILE: {DB_NAME}")

DB_NAME = "longchau_vitamin.db"
TABLE = "products"

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("\nNHÓM 1: KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (BẮT BUỘC)")

    # 1. Kiểm tra trùng lặp dựa trên product_url hoặc product_name
    print("\n1. Trùng lặp dựa trên product_url:")
    cursor.execute(f"""
        SELECT product_url, COUNT(*) AS so_luong
        FROM {TABLE}
        GROUP BY product_url
        HAVING COUNT(*) > 1;
    """)
    df_duplicates_url = pd.DataFrame(cursor.fetchall(), columns=["product_url", "so_luong"])
    print(df_duplicates_url if not df_duplicates_url.empty else "Không có trùng lặp.")

    print("\nTrùng lặp dựa trên product_name:")
    cursor.execute(f"""
        SELECT product_name, COUNT(*) AS so_luong
        FROM {TABLE}
        GROUP BY product_name
        HAVING COUNT(*) > 1;
    """)
    df_duplicates_name = pd.DataFrame(cursor.fetchall(), columns=["product_name", "so_luong"])
    print(df_duplicates_name if not df_duplicates_name.empty else "Không có trùng lặp.")

    # 2. Đếm sản phẩm thiếu giá (price_vnd NULL hoặc 0)
    cursor.execute(f"""
        SELECT COUNT(*) FROM {TABLE}
        WHERE price_vnd IS NULL OR price_vnd = 0;
    """)
    missing_price = cursor.fetchone()[0]
    print("\n2. Số sản phẩm thiếu giá bán:", missing_price)


    # 3. Liệt kê unit duy nhất
    cursor.execute(f"""
        SELECT DISTINCT unit FROM {TABLE}
        WHERE unit IS NOT NULL AND unit != ''
    """)
    unique_units = [row[0] for row in cursor.fetchall()]
    print("\n3. Unit duy nhất:", unique_units)

    # 4. Tổng số bản ghi
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE};")
    total = cursor.fetchone()[0]
    print("\n4. Tổng số sản phẩm:", total)

    print("\nNHÓM 2: KHẢO SÁT VÀ PHÂN TÍCH ")

    # 5. 10 sản phẩm giảm giá lớn nhất (bỏ qua vì không có original_price)
    print("\n5. 10 sản phẩm giảm giá lớn nhất: Không có original_price")

    # 6. Sản phẩm đắt nhất
    cursor.execute(f"""
        SELECT product_name, price_vnd FROM {TABLE}
        WHERE price_vnd IS NOT NULL
        ORDER BY price_vnd DESC LIMIT 1
    """)
    expensive = cursor.fetchone()
    print("\n6. Sản phẩm đắt nhất:", expensive)

    # 7. Đếm số lượng theo unit
    cursor.execute(f"""
        SELECT unit, COUNT(*) AS so_luong FROM {TABLE}
        GROUP BY unit
        ORDER BY so_luong DESC
    """)
    df_unit_counts = pd.DataFrame(cursor.fetchall(), columns=["unit", "so_luong"])
    print("\n7. Thống kê theo unit:")
    print(df_unit_counts)

    # 8. Sản phẩm chứa "Vitamin C"
    cursor.execute(f"""
        SELECT * FROM {TABLE}
        WHERE product_name LIKE '%Vitamin C%'
    """)
    vitamin_c = cursor.fetchall()
    print("\n8. Sản phẩm chứa 'Vitamin C':", len(vitamin_c), "sản phẩm")
    print(vitamin_c[:5])  # In 5 đầu tiên để ví dụ

    # 9. Lọc theo giá 100.000 - 200.000 VNĐ
    cursor.execute(f"""
        SELECT product_name, price_vnd FROM {TABLE}
        WHERE price_vnd BETWEEN 100000 AND 200000
        ORDER BY price_vnd ASC
    """)
    price_range = cursor.fetchall()
    print("\n9. Sản phẩm giá 100k - 200k:", len(price_range), "sản phẩm")
    print(price_range[:5])  # In 5 đầu

    print("\nNHÓM 3: TRUY VẤN NÂNG CAO")

    # 10. Sắp xếp theo giá từ thấp đến cao
    cursor.execute(f"""
        SELECT product_name, price_vnd FROM {TABLE}
        WHERE price_vnd IS NOT NULL
        ORDER BY price_vnd ASC
    """)
    sorted_low_to_high = cursor.fetchall()
    print("\n10. Sắp xếp giá thấp đến cao (10 đầu tiên):")
    print(sorted_low_to_high[:10])

    # 11. Phần trăm giảm giá (bỏ qua vì không có original_price)
    print("\n11. 5 sản phẩm % giảm cao nhất: Không có original_price → Bỏ qua.")

    # 12. Xóa bản ghi trùng lặp (dựa trên product_url, giữ id nhỏ nhất)
    cursor.execute(f"""
        DELETE FROM {TABLE}
        WHERE id NOT IN (
            SELECT MIN(id) FROM {TABLE}
            GROUP BY product_url
        )
    """)
    conn.commit()
    print("\n12. Đã xóa trùng lặp dựa trên product_url (nếu có).")

    # 13. Phân tích nhóm giá
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN price_vnd < 50000 THEN 'Dưới 50k'
                WHEN price_vnd BETWEEN 50000 AND 100000 THEN '50k - 100k'
                ELSE 'Trên 100k'
            END AS nhom_gia,
            COUNT(*) AS so_luong
        FROM {TABLE}
        WHERE price_vnd IS NOT NULL
        GROUP BY nhom_gia
    """)
    df_price_groups = pd.DataFrame(cursor.fetchall(), columns=["nhom_gia", "so_luong"])
    print("\n13. Thống kê nhóm giá:")
    print(df_price_groups)

    # 14. URL không hợp lệ
    cursor.execute(f"""
        SELECT id, product_name FROM {TABLE}
        WHERE product_url IS NULL OR product_url = ''
        LIMIT 5
    """)
    invalid_urls = cursor.fetchall()
    print("\n14. Bản ghi URL không hợp lệ:", invalid_urls if invalid_urls else "Không có.")

except sqlite3.Error as e:
    print(f"Lỗi kết nối/truy vấn: {e}")

finally:
    if conn:
        conn.close()
    print("\nHOÀN TẤT PHÂN TÍCH DỮ LIỆU!")
