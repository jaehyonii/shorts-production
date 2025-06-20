from collection import crawl_naver_news, summary_article, generate_audio, generate_image




# --- 메인 실행 부분 ---
if __name__ == "__main__":
	# 크롤링할 네이버 뉴스 URL
	target_url = "https://n.news.naver.com/mnews/article/018/0006044470" # 예시 URL

	news_data = crawl_naver_news('./article.txt', target_url)

	if news_data:
		print("--- 크롤링 결과 ---")
		print(f"언론사: {news_data['media_company']}")
		print(f"제목: {news_data['title']}")
		print(f"입력 시간: {news_data['timestamp']}")
		print("\n--- 본문 ---")
		print(news_data['content'])

	summary_article('./summary.txt', news_data)