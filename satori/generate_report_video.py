import os
import datetime

import cv2
from PIL import Image

from news_scraper import scrape_daily_news
from news_utils import *
from news_summarizer import generate_report_text
from news_article import load_articles

from audio import synthesize_text

from animation import generate_unsynced_video, load_avatar_image
from combine import combine

def main():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    output_path = f'data/{date_str}'
    os.makedirs(output_path, exist_ok=True)

    scrape_daily_news(output_path)

    articles = load_articles(f'{output_path}/news.json')
    text = generate_report_text(articles)

    synthesize_text(text, f'{output_path}/audio.mp3')

    avatar_image = load_avatar_image('talkinghead/avatar_images/reporter_female.png')
    background_image = cv2.resize(np.array(Image.open('data/cityscape.jpg')) / 255, (256,256))
    generate_unsynced_video(avatar_image, f'{output_path}/video.mp4', f'{output_path}/audio.mp3', background_image)
    combine(output_path)


if __name__ == '__main__':
    main()
