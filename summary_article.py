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
def summary_article(article: str) -> dict :
	try:
		prompt = f'''
당신은 유튜브 쇼츠 뉴스 채널을 전문으로 하는 콘텐츠 제작 전문가입니다. 제가 제공하는 뉴스 기사를 쇼츠 영상용 스크립트와 시각 자료 계획으로 변환하는 것이 당신의 임무입니다.

당신이 수행할 작업은 다음과 같습니다:
1.  제공된 뉴스 기사를 읽고 완벽하게 이해합니다.
2.  먼저, 유튜브 쇼츠 영상에 어울리는 짧고, 시선을 끌며, 클릭을 유도하는 한 줄 제목을 만듭니다.
3.  다음으로, 핵심 내용을 시청자가 순차적으로 이해하기 쉬운, 간결하고 영향력 있는 5개의 문장으로 요약합니다. **각 문장은 쇼츠 자막처럼 보이도록 자연스러운 호흡 단위에 맞춰 개행문자(\\n)를 사용해 줄을 나눠주세요.**
4.  요약된 5개의 각 문장에 대해, AI 이미지 생성기(Gemini)에 사용할, 문장의 내용과 분위기에 완벽하게 일치하는 시각적으로 매력적인 프롬프트를 만듭니다.

**이미지 프롬프트 가이드라인:**
* **스타일:** 영화적인 느낌, 사실적인 사진, 드라마틱한 조명, 높은 디테일.
* **종횡비:** 유튜브 쇼츠에 맞춰 세로 비율이어야 합니다. 각 프롬프트 끝에 `--ar 5:4`을 반드시 포함하세요.
* **명확성:** 주제, 행동, 환경에 대해 구체적으로 묘사하세요.
* **분위기:** 뉴스의 톤(예: 긴급함, 희망적, 진지함, 경이로움)과 시각적 톤을 일치시키세요.

당신의 최종 결과물은 반드시 단 하나의 JSON 객체여야 합니다. 이 객체는 두 개의 최상위 키를 포함해야 합니다:
1.  `title`: 생성된 영상의 제목 문자열.
2.  `summary_and_images`: 5개의 객체로 이루어진 배열.

summary_and_images 배열의 각 객체는 두 개의 키를 가져야 합니다: 요약된 텍스트를 위한 'sentence'(한국어)와 해당 이미지 생성 프롬프트를 위한 'image_prompt'(영어).

응답 시 JSON 객체 외에 다른 어떤 텍스트나 설명도 포함하지 마십시오.

기사 원문:
{article}
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