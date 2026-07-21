import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# ==========================================
# 사용자 설정 영역
# ==========================================
MAX_PAGES = 10  # 크롤링할 최대 페이지 수
BASE_URL = "https://www.coupang.com/np/categories/115673?listSize=60&filterType=rocket&rating=0&isPriceRange=false&minPrice=&maxPrice=&component=&sorter=bestAsc&brand=&offerCondition=&filter=&fromComponent=N&channel=user&selectedPlpKeepFilter=" 

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # [추가됨] 봇 차단을 우회하기 위해 일반 PC 브라우저인 척 속이는 User-Agent 설정
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options) 
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
        # [수정됨] 쿠팡 URL 양식에 맞게 &page=숫자 형태로 결합
        page_url = f"{BASE_URL}&page={page}"
        driver.get(page_url)
        time.sleep(3) # 쿠팡은 로딩 대기 시간을 넉넉히 주는 것이 좋습니다.

        # 1. 현재 페이지의 모든 상품 링크 수집
        # [수정됨] 1번째 상품의 이미지가 아니라, 리스트 전체의 링크(a 태그)를 가져오도록 수정
        item_elements = driver.find_elements(By.CSS_SELECTOR, '#product-list > li > a')
        item_urls = [elem.get_attribute('href') for elem in item_elements if elem.get_attribute('href')]

        print(f"{page}페이지에서 {len(item_urls)}개의 상품 링크를 발견했습니다.")

        # 2. 각 상품 페이지로 이동하여 데이터 추출
        for url in item_urls:
            driver.get(url)
            time.sleep(2) # 랜딩페이지 로딩 대기

            # 상세 페이지 CSS 선택자는 그대로 유지합니다.
            product_name = get_text_safe(driver, 'body > div:nth-child(5) > div > div.twc-flex.twc-max-w-full > main > div.prod-atf.twc-block.md\:twc-flex.twc-relative > div.prod-atf-contents.twc-relative.twc-flex-1.twc-min-w-0 > div.product-buy-header.product-buy-header-v2 > div.twc-flex.twc-justify-between.twc-items-start > div:nth-child(1) > h1 > span')
            seller_name = get_text_safe(driver, '#sdpEtc > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)')
            contact = get_text_safe(driver, '#sdpEtc > div > div:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)')
            email = get_text_safe(driver, '#sdpEtc > div > div:nth-child(2) > div > table > tbody > tr:nth-child(3) > td:nth-child(2)')

            all_data.append({
                '상품명': product_name,
                '판매자명': seller_name,
                '연락처': contact,
                '이메일': email,
                '상품URL': url
            })
            
            # 진행 상황을 깃허브 로그에서 바로 확인할 수 있도록 출력
            print(f"수집 시도: {url[:50]}... / 찾은 상품명: {product_name[:10]}")

    driver.quit()

    # 3. 수집된 데이터를 엑셀로 저장
    df = pd.DataFrame(all_data)
    excel_filename = 'customer_database.xlsx'
    df.to_excel(excel_filename, index=False)
    print(f"크롤링 완료. {excel_filename} 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
