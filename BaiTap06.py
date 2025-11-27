from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

# I. Tạo danh sách link + DataFrame rỗng
all_links = []
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# II. Lấy links A → Z (chỉ lấy đủ 10 link)
for i in range(65, 91):  # A → Z

    if len(all_links) >= 10:
        break

    driver = webdriver.Chrome()
    url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{chr(i)}%22"
    driver.get(url)

    try:
        time.sleep(2)

        content_div = driver.find_element(By.ID, "mw-content-text")
        all_uls = content_div.find_elements(By.TAG_NAME, "ul")

        # Chọn UL có nhiều li nhất
        max_ul = max(all_uls, key=lambda ul: len(ul.find_elements(By.TAG_NAME, "li")))
        li_tags = max_ul.find_elements(By.TAG_NAME, "li")

        # Lấy link
        for tag in li_tags:
            if len(all_links) >= 10:
                break
            try:
                a_tag = tag.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")
                if href and "/wiki/" in href:
                    all_links.append(href)
            except:
                pass

        print(f"Chữ {chr(i)}: lấy được {len(li_tags)} họa sĩ")

    except Exception as e:
        print(f"Lỗi khi lấy chữ {chr(i)}: {e}")

    driver.quit()

print(f"\nTỔNG LINK THU THẬP: {len(all_links)} (GIỚI HẠN 10 LINK)\n")

# III. Crawl thông tin của 10 họa sĩ
count = 0

for link in all_links:
    if count >= 10:
        break

    count += 1
    print(f"[{count}/10] Crawling: {link}")

    driver = webdriver.Chrome()
    try:
        driver.get(link)
        time.sleep(1.5)

        # Lấy tên
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # Lấy năm sinh
        birth = ""
        try:
            birth_text = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td").text
            birth_matches = re.findall(r"(\d{4})", birth_text)
            birth = birth_matches[0] if birth_matches else ""
        except:
            pass

        # Lấy năm mất
        death = ""
        try:
            death_text = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td").text
            death_matches = re.findall(r"(\d{4})", death_text)
            death = death_matches[0] if death_matches else ""
        except:
            pass

        # Lấy quốc tịch
        nationality = ""
        try:
            nationality = driver.find_element(
                By.XPATH, "//th[text()='Nationality']/following-sibling::td"
            ).text.split("\n")[0].strip()
        except:
            try:
                nationality = driver.find_element(
                    By.XPATH, "//th[contains(text(),'Nationality')]/following-sibling::td"
                ).text.split("\n")[0].strip()
            except:
                pass

        # Ghi vào DataFrame
        painter = {'name': name, 'birth': birth, 'death': death, 'nationality': nationality}
        d = pd.concat([d, pd.DataFrame([painter])], ignore_index=True)

        print(f"Đã lấy: {name}")

    except Exception as e:
        print(f"Lỗi khi crawl trang này: {e}")

    finally:
        driver.quit()

# IV. Xuất kết quả
print("\nDONE! Crawl được 10 họa sĩ.")
print(d)

d.to_excel("Painters_10.xlsx", index=False)
print("Đã lưu file Painter_10.xlsx")
