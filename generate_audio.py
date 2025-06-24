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

##### TTS #####
import wave

# Set up the wave file to save the output:
def wave_file(save_path, pcm, channels=1, rate=24000, sample_width=2):
	with wave.open(save_path, "wb") as wf:
		wf.setnchannels(channels)
		wf.setsampwidth(sample_width)
		wf.setframerate(rate)
		wf.writeframes(pcm)

def generate_audio(transciption: str):
	try:
		response = client.models.generate_content(
			model="gemini-2.5-flash-preview-tts",
			contents=transciption,
			config=types.GenerateContentConfig(
				response_modalities=["AUDIO"],
				speech_config=types.SpeechConfig(
					voice_config=types.VoiceConfig(
						prebuilt_voice_config=types.PrebuiltVoiceConfig(
							voice_name='Enceladus',
						)
					)
				),
			)
		)
	except Exception as e:
		logger.error(f'An error occurred: {e}')

	data = response.candidates[0].content.parts[0].inline_data.data

	return data