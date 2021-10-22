from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
import time
import requests
import chardet

driver = webdriver.Chrome(executable_path="C:\chromedriver_win32\chromedriver.exe")
driver.implicitly_wait(3)

# Login Page
print("네이버 로그인")
driver.get('https://nid.naver.com/nidlogin.login')
id = '아이디'
pw = '비밀번호'

driver.execute_script("document.getElementsByName('id')[0].value=\'" + id + "\'")
time.sleep(1)
driver.execute_script("document.getElementsByName('pw')[0].value=\'" + pw + "\'")
time.sleep(1)
driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()  # 엔터 없이 바로 연결

# cafe main page url
cafe_url = "https://cafe.naver.com/dokchi?iframe_url=/MyCafeIntro.nhn%3Fclubid=16996348"  # 여기 url 쓰기
driver.get(cafe_url)
time.sleep(1)

# 카페 목록 출력 페이지 지정, 옵션 설정
pages = 47  # 여기에 max page 쓰기
count = 0
scafe = []
stitle = []  # 게시글 제목
scontent = []  # 게시글 내용
dates = []
content_tags = []
board_url = 'https://cafe.naver.com/bebettergirls?iframe_url=/ArticleSearchList.nhn%3Fsearch.clubid=25158488%26search.media=0%26search.searchdate=2019-10-162019-10-30%26search.defaultValue=1%26search.exact=%26search.include=%26userDisplay=50%26search.exclude=%26search.option=0%26search.sortBy=date%26search.searchBy=0%26search.includeAll=%26search.query=%C3%EB%BE%F7%26search.viewtype=title%26search.page='
driver.get(board_url)
time.sleep(1)
driver.switch_to.frame("cafe_main")

for i in range(1, pages + 1):
    count = i
    # urls=[]
    url = board_url + str(i)
    driver.get(url)
    time.sleep(1)

    iframe = driver.find_element_by_id('cafe_main')
    driver.switch_to.frame(iframe)

    # Selenium 제목 링크추출
    links = driver.find_elements_by_css_selector('div.board-list a.article')
    urls = [i.get_attribute('href') for i in links]

    print("게시글 크롤링 시작 Page = ", count)

    # Beautifulsoup 활용 제목, 내용 크롤링
    for conurl in urls:
        try:
            try:  # 게시글이 삭제되었을 경우가 있기 때문에 try-exception
                driver.get(conurl)
                time.sleep(1)
                # content 글내용도 switch_to_frame이 필수
                driver.switch_to.frame('cafe_main')
                soup = bs(driver.page_source, 'html.parser')
                try:  # <------------------------ 여기 수정
                    title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "title_text"))
                    )
                    print(title.text)
                    stitle.append(title.text)

                    date = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "date"))
                    )
                    print(date.text)
                    dates.append(date.text)

                    # contentrenderer
                    content_tags = soup.select('div.ContentRenderer')[0].select('p')
                    content = ' '.join([tags.get_text() for tags in content_tags])
                    print(content)
                    scontent.append(content)


                except TimeoutException:
                    print("해당 페이지에 app을 가진 ID를 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.")

                # cframe = driver.find_element_by_id('cafe_main')
                # driver.switch_to_frame(cframe)
                # contentSource = driver.page_source
                # soup = bs(contentSource, 'html.parser')

                # 제목 검색
                # [수정]2018.5.9 css tag 빈공간 에러발생
                # "span[class='b m-tcol-c']" → 'div.fl span.b'

                print([pages, count, len(stitle)])  # page로는 진행상황, cnt로는 몇개의 데이터


            except:  # chrome alert창 처리해줌
                driver.switch_to_alert.accpet()
                driver.switch_to_alert
                driver.switch_to_alert.accpet()
        except:
            pass

    time.sleep(1)

    print("제목 내용 날짜 크롤링 완료")

    #####################################
    print("title lengh=", len(stitle))

    ### DataFrame 으로 변환하기위한 리스트저장 ###
    # 게시글 제목,닉네임,네이버ID,링크,내용
    ##[수정] 2018.5.8
    # for 문 사용대신 DataFrame에서 전치행렬로 변환가능
    # tranposed matrix 명령어
    # scafe = pd.DataFrame([stitle, snickname, surl, scontent, naverIDs])
    # scafe = scafe.T
    ##[수정.끝]...

scafe = pd.DataFrame([stitle, scontent, dates])
scafe = scafe.T
scafe = pd.DataFrame(scafe)
scafe.to_csv('취업대학교_19년도_1016_1030.csv', encoding='utf-8-sig', index=True)

# PhantomJS Browser Close
driver.close()