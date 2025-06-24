import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 각 모듈의 최상단에서 자신의 이름으로 로거를 가져옵니다.
logger = logging.getLogger(__name__)

# 1. .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 2. os.getenv()를 사용하여 환경 변수에서 API 키를 가져옵니다.
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 3. (선택사항) API 키가 제대로 로드되었는지 확인합니다.
if not gemini_api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일에 GOOGLE_API_KEY를 설정해주세요.")

# 4. 가져온 API 키로 Gemini를 설정합니다.
client = genai.Client(api_key=gemini_api_key)

##### 기사 요약 #####
def summary_article(article: str):
	try:
		prompt = f'''
유튜브 쇼츠 영상 대본 생성 프롬프트

# 역할
당신은 최고의 유튜브 쇼츠 영상 기획자입니다.

# 임무
아래에 제공된 [뉴스 기사]를 분석하여, 1분 미만의 유튜브 쇼츠 영상에 최적화된 대본과 제목을 생성합니다. 제목은 짧고 간결하게 작성합니다. 대본은 시청자의 흥미를 유발할 수 있도록 핵심 내용만 간결하게 요약해야 합니다. 각 문장마다 타임라인과 함께 제안해야 합니다.

# 지시사항
제목 추천: 뉴스 기사의 주제에 맞는 제목을 추천합니다.
핵심 요약: 뉴스 기사의 내용을 5개의 핵심 문장으로 요약합니다.
간결한 문장: 각 문장은 시청자가 쉽게 이해할 수 있도록 짧고 명확하게 작성합니다.
시간 배분: 전체 영상 길이가 40초에서 55초 사이가 되도록 각 문장의 시간을 배분합니다.
출력 형식 준수: 아래 [출력 형식]을 반드시 지켜서 결과물을 생성해.
주의할 점: "를 사용할 땐, 반드시 \" 사용하기

[뉴스 기사]
{article}

[출력 형식]
{{
    "제목": "기사 제목과 어울리는 제목",
	"문장 1": {{
		"timestamp": "[00:00 - 00:08]",
		"transcript": "기사의 핵심을 관통하는 첫 번째 요약 문장"
	}},

	"문장 2": {{
		"timestamp": "[00:08 - 00:18]",
		"transcript": "기사의 구체적인 사실이나 사건을 설명하는 두 번째 요약 문장"
	}},

	"문장 3": {{
		"timestamp": "[00:18 - 00:29]",
		"transcript": "사건의 배경이나 원인을 설명하는 세 번째 요약 문장"
	}},

	"문장 4": {{
		"timestamp": "[00:29 - 00:40]",
		"transcript": "사건의 영향이나 전문가의 의견을 담은 네 번째 요약 문장"
	}},

	"문장 5": {{
		"timestamp": "[00:40 - 00:52]",
		"transcript": "영상의 결론 또는 미래 전망을 제시하는 다섯 번째 요약 문장"
	}}
}}
  '''
  
		response = client.models.generate_content(
			model="gemini-2.5-flash",
			contents=prompt,
			config=types.GenerateContentConfig(
				thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
			),
		)

	except Exception as e:
		logger(f"An error occurred: {e}")
		raise
	
	summary = response.text.strip().removeprefix('```json\n').removesuffix('```')
 
	return summary