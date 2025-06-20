import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 2. os.getenv()를 사용하여 환경 변수에서 API 키를 가져옵니다.
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 3. (선택사항) API 키가 제대로 로드되었는지 확인합니다.
if not gemini_api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일에 GOOGLE_API_KEY를 설정해주세요.")

# 4. 가져온 API 키로 Gemini를 설정합니다.
client = genai.Client(api_key=gemini_api_key)

##### 기사 크롤링 #####
import requests
from bs4 import BeautifulSoup
import time

def crawl_naver_news(save_path: str, url: str):
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
		title_element = soup.select_one('#ct > .media_end_head > .media_end_head_headline')
		title = title_element.get_text(strip=True) if title_element else "제목 없음"
		
		# 3. 기사 입력 시간 추출
		timestamp_element = soup.select_one('#ct > .media_end_head > .media_end_head_info > .media_end_head_info_datestamp > .media_end_head_info_datestamp_time')
		timestamp = timestamp_element['data-date-time'] if timestamp_element else "시간 정보 없음"
		
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

		with open(save_path, 'w', encoding='utf-8') as fw:
			fw.write(content)

		return {
			'media_company': media_company,
			'title': title,
			'timestamp': timestamp,
			'content': content,
			'url': url
		}

	except requests.exceptions.RequestException as e:
		print(f"Error fetching URL: {e}")
		return None
	except Exception as e:
		print(f"An error occurred: {e}")
		return None

##### 기사 요약 #####
def summary_article(save_path: str, article: str):
	try:
		prompt = f'''
유튜브 쇼츠 영상 대본 생성 프롬프트

# 역할
당신은 최고의 유튜브 쇼츠 영상 기획자입니다.

# 임무
아래에 제공된 [뉴스 기사]를 분석하여, 1분 미만의 유튜브 쇼츠 영상에 최적화된 대본을 생성합니다. 대본은 시청자의 흥미를 유발할 수 있도록 핵심 내용만 간결하게 요약해야 합니다. 각 문장마다 타임라인과 함께 장면에 어울리는 이미지나 영상 클립 아이디어를 구체적으로 제안해야 합니다.

# 지시사항
핵심 요약: 뉴스 기사의 내용을 3~5개의 핵심 문장으로 요약합니다.
간결한 문장: 각 문장은 시청자가 쉽게 이해할 수 있도록 짧고 명확하게 작성합니다.
시간 배분: 전체 영상 길이가 40초에서 55초 사이가 되도록 각 문장의 시간을 배분합니다.
이미지 제안: 각 문장에 맞는 이미지를 제안합니다. 이미지는 역동적인 애니메이션, 상징적인 그래픽, 또는 구체적인 장면 묘사 형식으로 제안해주세요.
출력 형식 준수: 아래 [출력 형식]을 반드시 지켜서 결과물을 생성해주세요.

[뉴스 기사]
{article}

[출력 형식]
문장 1
[00:00 - 00:08]
(제안 이미지: [문장 1의 내용과 분위기를 가장 잘 나타내는 이미지나 영상 클립에 대한 구체적인 묘사])
기사의 핵심을 관통하는 첫 번째 요약 문장

문장 2
[00:08 - 00:18]
(제안 이미지: [문장 2의 구체적인 상황이나 정보를 시각적으로 보여주는 이미지 묘사])
기사의 구체적인 사실이나 사건을 설명하는 두 번째 요약 문장

문장 3
[00:18 - 00:29]
(제안 이미지: [문장 3의 원인, 배경 또는 추가 정보를 설명하는 상징적인 그래픽/애니메이션 묘사])
사건의 배경이나 원인을 설명하는 세 번째 요약 문장

문장 4
[00:29 - 00:40]
(제안 이미지: [문장 4의 영향이나 전문가 의견을 보여주는 인포그래픽/인터뷰 장면 묘사])
사건의 영향이나 전문가의 의견을 담은 네 번째 요약 문장

문장 5
[00:40 - 00:52]
(제안 이미지: [영상의 결론이나 미래 전망을 암시하는 긍정적/경고적 이미지 묘사])
영상의 결론 또는 미래 전망을 제시하는 다섯 번째 요약 문장
  '''
  
		response = client.models.generate_content(
			model="gemini-2.5-flash",
			contents=prompt,
			config=types.GenerateContentConfig(
				thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
			),
		)
		print(f'summary:\n{response.text}')

	except Exception as e:
		print(f"오류가 발생했습니다: {e}")
		raise

	with open(save_path, 'w', encoding='utf-8') as fw:
		fw.write(response.text)


##### 이미지 생성 #####
from PIL import Image
from io import BytesIO
from datetime import datetime

def generate_image(save_path: str, description: str):
	response = client.models.generate_images(
		model='imagen-3.0-generate-002',
		prompt=description,
		config=types.GenerateImagesConfig(
			number_of_images= 1,
		)
	)

	# 응답이 있고, 생성된 이미지가 있는지 확인
	if response and response.generated_images:
		# 리스트의 첫 번째(그리고 유일한) 이미지를 가져옵니다.
		generated_image = response.generated_images[0]
		
		# 이미지 데이터를 PIL Image 객체로 엽니다.
		image_bytes = generated_image.image.image_bytes
		image = Image.open(BytesIO(image_bytes))
		
		# 저장할 폴더 생성 (없으면)
		os.makedirs(save_path, exist_ok=True)
		
		# 파일 이름 생성 (예: '20250620_160042.png')
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		save_path = os.path.join(save_path, f"{timestamp}.png")
		
		# 이미지를 파일로 저장
		image.save(save_path)
		
		print(f"이미지 생성이 완료되었습니다: '{save_path}'")
		
		# 저장된 이미지 바로 보기 (선택 사항)
		# image.show()
	else:
		print("API로부터 이미지를 생성하지 못했습니다.")


##### TTS #####
import wave

# Set up the wave file to save the output:
def wave_file(save_path, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(save_path, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def generate_audio(save_path: str, transciption: str):
	response = client.models.generate_content(
		model="gemini-2.5-flash-preview-tts",
		contents=transciption,
		config=types.GenerateContentConfig(
			response_modalities=["AUDIO"],
			speech_config=types.SpeechConfig(
				voice_config=types.VoiceConfig(
					prebuilt_voice_config=types.PrebuiltVoiceConfig(
						voice_name='Kore',
					)
				)
			),
		)
	)

	data = response.candidates[0].content.parts[0].inline_data.data

	wave_file(save_path, data) # Saves the file to current directory