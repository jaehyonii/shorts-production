import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 각 모듈의 최상단에서 자신의 이름으로 로거를 가져옵니다.
logger = logging.getLogger(__name__)

##### 기사 크롤링 #####
def crawl_naver_news(url: str):
	"""
	주어진 URL의 네이버 뉴스 기사를 크롤링합니다.
	:param url: 크롤링할 네이버 뉴스 기사의 URL
	:return: 크롤링된 데이터를 담은 딕셔너리, 실패 시 None
	"""
	try:
		# 사이트가 차단하는 것을 막기 위해 'User-Agent' 헤더를 추가합니다.
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
		
		# GET 요청을 보냅니다.
		response = requests.get(url, headers=headers)
		
		# 요청이 성공했는지 확인합니다. (상태 코드가 200이 아니면 에러 발생)
		response.raise_for_status()
		
		# BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
		soup = BeautifulSoup(response.text, 'lxml')
		
		# --- 데이터 추출 ---
		# ※ HTML 구조는 언제든지 변경될 수 있으므로, 셀렉터(selector)는 주기적으로 확인해야 합니다.
		
		# 1. 언론사 추출
		media_company_element = soup.select_one('a.media_end_head_top_logo img')
		media_company = media_company_element['title'] if media_company_element else "언론사 없음"

		# 2. 기사 제목 추출
		title_element = soup.select_one('#title_area span')
		#title_element = soup.select_one('#ct > .media_end_head > .media_end_head_headline')
		title = title_element.get_text(strip=True) if title_element else "제목 없음"
		
		# 3. 기사 입력 시간 추출
		timestamp_element = soup.select_one('#ct > .media_end_head > .media_end_head_info > .media_end_head_info_datestamp > .media_end_head_info_datestamp_bunch span')
		timestamp = timestamp_element['data-date-time'] if timestamp_element else "시간 정보 없음"
		timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
		timestamp = datetime.strftime(timestamp, '%Y-%m-%dT%H:%M:%S')
		
		# 4. 기사 본문 추출
		content_element = soup.select_one('#dic_area')
		
		# 본문 내용에서 불필요한 태그(광고 등) 제거
		if content_element:
			# 기자 정보 등 필요 없는 부분 제거
			for el in content_element.select('em.img_desc, .img_desc, .reporter_area, div.vod_player, a'):
				el.decompose()
			
			content = content_element.get_text(separator='\n', strip=True)
		else:
			content = "본문 없음"

		return {
			'media_company': media_company,
			'title': title,
			'timestamp': timestamp,
			'content': content,
			'url': url
		}

	except requests.exceptions.RequestException as e:
		logger.error(f"Error fetching URL: {e}")
		raise
	except Exception as e:
		logger.error(f"An error occurred: {e}")
		raise