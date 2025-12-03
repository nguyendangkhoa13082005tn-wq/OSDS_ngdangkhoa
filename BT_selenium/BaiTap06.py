

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re

# CẤU HÌNH
# (Tùy chọn: chạy ẩn để nhanh hơn, bỏ comment 2 dòng bên dưới nếu muốn)
# chrome_options = Options()
# chrome_options.add_argument("--headless")

all_links = []
df = pd.DataFrame(columns=['name', 'birth', 'death', 'nationality'])

print("Bắt đầu cào danh sách họa sĩ bắt đầu bằng chữ 'F'...")

# . LẤY TOÀN BỘ LINK CHỮ F
driver = webdriver.Chrome()  # chrome_options=chrome_options nếu dùng headless
url = 'https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_"F"'
driver.get(url)
time.sleep(3)

try:
    # Tìm khối nội dung chính
    content = driver.find_element(By.ID, "mw-content-text")
    all_uls = content.find_elements(By.TAG_NAME, "ul")

    # Tìm <ul> có nhiều <li> nhất → thường là danh sách họa sĩ chính
    main_ul = max(all_uls, key=lambda ul: len(ul.find_elements(By.TAG_NAME, "li")))
    li_tags = main_ul.find_elements(By.TAG_NAME, "li")

    for li in li_tags:
        try:
            a_tag = li.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            if href and "/wiki/" in href and "List_of_painters" not in href:
                all_links.append(href)
        except:
            continue

    print(f"Đã thu thập được {len(all_links)} link họa sĩ bắt đầu bằng chữ F.")

except Exception as e:
    print("Lỗi khi lấy danh sách link:", e)
finally:
    driver.quit()

# II. CÀO THÔNG TIN TỪ TỪNG TRANG
print("\nBắt đầu cào thông tin chi tiết...\n")

count = 0
total = len(all_links)

for link in all_links:
    count += 1
    print(f"[{count}/{total}] Đang xử lý: {link}")

    driver = webdriver.Chrome()  # chrome_options=chrome_options nếu dùng headless
    try:
        driver.get(link)
        time.sleep(2)

        # 1. Tên họa sĩ
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            name = ""

        # 2. Ngày sinh (lấy ngày đầy đủ: 12 June 1900)
        birth = ""
        try:
            born_cell = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            born_text = born_cell.text
            match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', born_text)
            birth = match.group(1) if match else ""
        except:
            pass

        # 3. Ngày mất
        death = ""
        try:
            died_cell = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            died_text = died_cell.text
            match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', died_text)
            death = match.group(1) if match else ""
        except:
            pass

        # 4. Quốc tịch
        nationality = ""
        try:
            nat_cell = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nat_cell.text.split("\n")[0].strip()
        except:
            try:
                # Một số trang dùng "Nationality" có khoảng trắng hoặc chữ hoa/thường khác
                nat_cell = driver.find_element(By.XPATH, "//th[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'nationality')]/following-sibling::td")
                nationality = nat_cell.text.split("\n")[0].strip()
            except:
                pass

        # Thêm vào DataFrame
        new_row = pd.DataFrame([{
            'name': name,
            'birth': birth,
            'death': death,
            'nationality': nationality
        }])
        df = pd.concat([df, new_row], ignore_index=True)

        print(f"Đã lưu: {name} | Sinh: {birth} | Mất: {death} | Quốc tịch: {nationality}")

    except Exception as e:
        print(f"Lỗi khi cào {link}: {e}")
    finally:
        driver.quit()

    # Nghỉ ngẫu nhiên để tránh bị Wikipedia chặn
    time.sleep(1)

# III. XUẤT KẾT QUẢ
print("\nHOÀN TẤT! Đã cào xong toàn bộ họa sĩ chữ F.")
print(f"Tổng cộng: {len(df)} họa sĩ.")

# Lưu ra Excel
output_file = "Painters_F.xlsx"
df.to_excel(output_file, index=False)
print(f"Đã lưu dữ liệu vào file: {output_file}")

# Hiển thị 10 dòng đầu tiên
print("\n10 dòng dữ liệu mẫu:")
print(df.head(10))
