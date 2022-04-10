import os
import datetime
import cv2
from PIL import Image

from nlp import scrape_daily_news, load_articles, generate_report_text
from audio import synthesize_text
from animation import generate_unsynced_video, load_avatar_image

import numpy as np
import ffmpeg


def combine(output_dir):
    audio_path = f'{output_dir}/audio.mp3'
    video_path = f'{output_dir}/video.mp4'
    audio = ffmpeg.input(audio_path)
    video = ffmpeg.input(video_path)
    ffmpeg.output(audio, video, f'{output_dir}/combined.mp4').run()


def main():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    output_path = f'data/{date_str}'
    os.makedirs(output_path, exist_ok=True)

    #scrape_daily_news(output_path)
    articles = load_articles(f'{output_path}/news.json')
    text = generate_report_text(articles)

    times = synthesize_text([c['text'] for c in text], f'{output_path}/audio.mp3')
    assert len(times) == len(text)
    
    avatar_image = load_avatar_image('talkinghead/avatar_images/reporter_female.png')
    background_image = cv2.resize(np.array(Image.open('data/cityscape.jpg')) / 255, (256,256))
    generate_unsynced_video(avatar_image, f'{output_path}/video.mp4', f'{output_path}/audio.mp3', background_image, times, [c['image'] for c in text])
    combine(output_path)


if __name__ == '__main__':
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    output_path = f'data/{date_str}'
    os.makedirs(output_path, exist_ok=True)
    main()
    #scrape_daily_news(output_path)
    #articles = load_articles(f'{output_path}/news.json')
    #text = generate_report_text(articles)
