import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# ==========================================
# 사용자 설정 영역
# ==========================================
MAX_PAGES = 3  # 크롤링할 최대 페이지 수
BASE_URL = "https://example.com/category?page="  # 실제 타겟 카테고리 URL로 변경하세요.

def setup_driver():
    options = Options()
    options.add_argument('--headless') # 깃허브 환경에서는 화면이 없으므로 백그라운드 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    return driver

def get_text_safe(driver, css_selector):
    """요소가 없으면 빈 문자열을 반환하는 안전한 텍스트 추출 함수"""
    try:
        return driver.find_element(By.CSS_SELECTOR, css_selector).text
    except NoSuchElementException:
        return ""

def main():
    driver = setup_driver()
    all_data = []

    for page in range(1, MAX_PAGES + 1):
        print(f"=== {page}페이지 크롤링 시작 ===")
        page_url = f"{BASE_URL}{page}"
        driver.get(page_url)
        time.sleep(2) # 페이지 로딩 대기

        # 1. 현재 페이지의 모든 상품 링크 수집
        # [수정 필요] 상품 클릭 링크에 해당하는 CSS 선택자를 넣으세요.
        item_elements = driver.find_elements(By.CSS_SELECTOR, '.item-list > a.product-link')
        item_urls = [elem.get_attribute('href') for elem in item_elements if elem.get_attribute('href')]

        print(f"{page}페이지에서 {len(item_urls)}개의 상품을 발견했습니다.")

        # 2. 각 상품 페이지로 이동하여 데이터 추출
        for url in item_urls:
            driver.get(url)
            time.sleep(1.5) # 랜딩페이지 로딩 대기

            # [수정 필요] 각 데이터에 맞는 CSS 선택자를 넣으세요.
            product_name = get_text_safe(driver, '.product-title')
            seller_name = get_text_safe(driver, '.seller-info .name')
            contact = get_text_safe(driver, '.seller-info .phone')
            email = get_text_safe(driver, '.seller-info .email')

            all_data.append({
                '상품명': product_name,
                '판매자명': seller_name,
                '연락처': contact,
                '이메일': email,
                '상품URL': url
            })
            
            print(f"수집 완료: {product_name} / {seller_name}")

    driver.quit()

    # 3. 수집된 데이터를 엑셀로 저장
    df = pd.DataFrame(all_data)
    excel_filename = 'customer_database.xlsx'
    df.to_excel(excel_filename, index=False)
    print(f"크롤링 완료. {excel_filename} 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
