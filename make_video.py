from moviepy import (
    VideoClip,
    VideoFileClip,
    ImageSequenceClip,
    ImageClip,
    TextClip,
    ColorClip,
    AudioFileClip,
    AudioClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from moviepy import vfx, afx
import json

with open(f'{__file__}/../config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
    
channel=config['channel']
bg_color=config['bg_color']
title_font = f'{__file__}/../font/Jalnan2TTF.ttf'
content_font = f'{__file__}/../font/NotoSansKR-SemiBold.ttf'

def make_video(json_summary: dict):
    # --- 입력 파일 경로 ---
    image_files = [f'./images/image{i+1}.png' for i in range(len(json_summary['summary_and_images']))]  # 사용할 이미지 파일 경로
    audio_files = [f'./audios/audio{i+1}.wav' for i in range(len(json_summary['summary_and_images']))] # 사용할 WAV 오디오 파일 경로
    title = json_summary['title']
    sentences = [v['sentence'] for v in json_summary['summary_and_images']] # 사용할 WAV 오디오 파일 경로
    output_file = "result.mp4"   # 최종 저장될 MP4 영상 파일 경로
    
    # 완성된 '영상 조각'들을 담을 리스트
    content_track_segments = []
    
    # 이미지와 영상을 먼저 합성
    for image_file, audio_file in zip(image_files, audio_files):
        print(f"처리 중: {image_file} + {audio_file}")
        
        # 1. 오디오 클립 로드
        audio_clip = AudioFileClip(audio_file)
        print(f"  - 오디오 길이: {audio_clip.duration:.2f}초")
        
        # 2. 이미지 클립 생성 및 오디오 길이에 맞춰 duration 설정 (set_duration 사용)
        image_clip = ImageClip(image_file)
        image_clip = image_clip.with_effects([vfx.Resize(height=800)]) if (image_clip.h) / 800 > (image_clip.w / 1000) else image_clip.with_effects([vfx.Resize(width=1000)])
        image_clip = image_clip.with_duration(audio_clip.duration)
        
        # 3. 이미지 클립에 오디오를 설정하여 '소리가 포함된 영상 조각' 생성
        video_segment_with_audio = image_clip.with_audio(audio_clip)
        print(f"  - 생성된 영상 조각 길이: {video_segment_with_audio.duration:.2f}초")
        
        # 4. 완성된 영상 조각을 리스트에 추가
        content_track_segments.append(video_segment_with_audio)
        
    # 모든 영상 조각들을 순서대로 이어 붙입니다.
    content_track = concatenate_videoclips(content_track_segments)
    total_duration = content_track.duration
    
    # 배경 생성
    bg_clip = bg_clip = ColorClip(size=(1080, 1920), color=bg_color, duration=total_duration)
    
    # 채널명 생성
    author_clip = TextClip(
            text=channel, 
            font=title_font,
            font_size=150,
            color='white',
            text_align='center',
            horizontal_align='center',
            method='label',
            duration=total_duration
        )
    
    # 제목 생성
    title_clip = TextClip(
            text=title, 
            font=title_font,
            font_size=45,
            color='white',
            text_align='left',
            horizontal_align='center',
            method='label',
            duration=total_duration
        )

    # 자막 클립 생성
    transcript_track_segments = []
    for i, seg in enumerate(content_track_segments):
        txt_clip = TextClip(
            text=sentences[i], 
            font=content_font,
            font_size=45,
            size=(900, 500),
            color='white',
            interline=10,
            text_align='center',
            horizontal_align='center',
            vertical_align='top',
            method='caption',
            duration=seg.duration
        )
        transcript_track_segments.append(txt_clip)
    
    # 모든 대사 조각들을 순서대로 이어 붙입니다.
    transcript_track = concatenate_videoclips(transcript_track_segments)
    
    # 이미지 블록
    ex_clip = ColorClip(size=(1000, 800), color=[0,0,0], duration=total_duration)
    
    # 합성
    final_clip = CompositeVideoClip([
        bg_clip,
        author_clip.with_position(('center', 'top')).with_effects([vfx.Margin(top=100, opacity=0)]),
        title_clip.with_position(('left', 'top')).with_effects([vfx.Margin(top=500, left=40, opacity=0)]),
        content_track.with_position('center'),
        transcript_track.with_position(('center', 'bottom')),
    ])

    final_clip.show(1.5)

    # --- 3단계: 최종 결과물 파일로 저장 ---
    print("\n3단계: 최종 비디오 파일을 저장합니다...")
    final_clip.write_videofile(output_file, fps=24)

    print(f"\n최종 영상 제작 완료! '{output_file}' 파일이 생성되었습니다.")
    
