name: Run Scraper

# 수동으로 실행 버튼을 누를 때 작동하도록 설정 (필요시 cron으로 예약 실행 가능)
on: 
  workflow_dispatch:

jobs:
  scrape-data:
    runs-on: ubuntu-latest

    steps:
      # 1. 깃허브 저장소의 코드 불러오기
      - name: Checkout Repository
        uses: actions/checkout@v4

      # 2. 파이썬 환경 세팅
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # 3. 필요한 라이브러리 설치
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # 4. 크롤링 파이썬 스크립트 실행
      - name: Run scraper script
        run: python scraper.py

      # 5. 생성된 엑셀 파일을 깃허브에서 다운받을 수 있도록 업로드
      - name: Upload Excel file as Artifact
        uses: actions/upload-artifact@v4
        with:
          name: Crawled-Data
          path: customer_database.xlsx
          retention-days: 7 # 7일 후 파일 자동 삭제
