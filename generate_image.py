import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

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

def generate_image(save_path: str, transcript: str):
	response = client.models.generate_content(
		model="gemini-2.0-flash-preview-image-generation",
		contents=f'generate appropriate image for the following dialogue: {transcript}',
		config=types.GenerateContentConfig(
		response_modalities=['TEXT', 'IMAGE']
		)
	)

	for part in response.candidates[0].content.parts:
		if part.text is not None:
			print(part.text)
		elif part.inline_data is not None:
			image = Image.open(BytesIO((part.inline_data.data)))
			image.save(save_path)