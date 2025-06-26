import os
import sys
import logging
import json
from datetime import datetime
from crawl_naver_news import crawl_naver_news
from summary_article import summary_article
from generate_audio import generate_audio, wave_file
from generate_image import generate_image
from make_video import make_video

# --- 메인 실행 부분 ---
if __name__ == "__main__":
	# 로그 파일을 저장할 디렉토리 생성
	log_dir = './logs'
	os.makedirs(log_dir, exist_ok=True)

	# 기본 로깅 설정
	logging.basicConfig(
		level=logging.INFO,  # 로그 레벨 설정 (이 레벨 이상의 로그만 기록됨)
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 메시지 형식
		filename=f"{log_dir}/app.log",  # 로그를 저장할 파일명
		encoding='utf-8'
	)

	main_logger = logging.getLogger(__name__)
	main_logger.info("프로그램이 시작되었습니다.")

	print(f"로그가 '{log_dir}/app.log' 파일에 저장되었습니다.")

	current_time = datetime.now()
	formatted_time = current_time.strftime("%Y%m%d%H%M%S")
	save_dir = formatted_time
	os.makedirs(save_dir, exist_ok=True)
	os.chdir(save_dir)
	os.makedirs('images', exist_ok=True)
	os.makedirs('audios', exist_ok=True)

	# 크롤링할 네이버 뉴스 URL
	target_url = input('URL을 입력하세요: ') # URL 입력
 
	###### 기사 크롤링 #####
	print('article crawling')
	try:
		news_data = crawl_naver_news(url=target_url)
	except:
		main_logger.info("프로그램이 종료되었습니다.")
		sys.exit(1)
 
	# 'w'(쓰기 모드)로 파일을 열고 딕셔너리를 JSON 형식으로 저장합니다.
	with open('./article.json', 'w', encoding='utf-8') as f:
		json.dump(news_data, f, ensure_ascii=False, indent=4)

	print('article crawling completed')
	########################
 
	###### 기사 요약 #####
	print('summarize article')
	try:
		summary = summary_article(news_data['content'])
	except:
		main_logger.info("프로그램이 종료되었습니다.")
		sys.exit(1)
  
	# 'w'(쓰기 모드)로 파일을 열고 딕셔너리를 JSON 형식으로 저장합니다.
	with open('./summary.json', 'w', encoding='utf-8') as f:
		f.write(summary)
  
	print('summarize article completed')
	############################
	
 
	with open('./summary.json', 'r', encoding='utf-8') as file:
		# json.load()를 사용하여 파일 내용을 딕셔너리로 로드
		json_summary = json.load(file)
  
	try:
		for idx, value in enumerate(json_summary['summary_and_images']):
			print(f'generate audio{idx+1}')
			sentence = value['sentence']
			##### TTS 생성 #####
			audio = generate_audio(sentence)
			wave_file(f'./audios/audio{idx+1}.wav', audio)
			print(f'generate audio{idx+1} completed')
   
			##### 이미지 생성 #####
			print(f'generate image{idx+1}')
			generate_image(f'./images/image{idx+1}.png', value['image_prompt'])
			print(f'generate image{idx+1} completed')
	except:
		main_logger.info("프로그램이 종료되었습니다.")
		sys.exit(1)
 
	##### 영상 만들기 #####
	print('generate video')  
	make_video(json_summary)
	print('generate video completed')  
	############################
 
  	# ##### 실험 #####
	# os.chdir('0000000000')
	# with open('./summary.json', 'r', encoding='utf-8') as file:
	# 	# json.load()를 사용하여 파일 내용을 딕셔너리로 로드
	# 	json_summary = json.load(file)
	# print('generate video')  
	# make_video(json_summary)
	# print('generate video completed')
	# ####################