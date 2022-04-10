import os
import datetime
import cv2
import numpy as np
from PIL import Image

from nlp import scrape_daily_news, load_articles, generate_report_text
from audio import synthesize_text
from animation import generate_unsynced_video, load_avatar_image

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
    #articles = load_articles(f'{output_path}/news.json')
    #text = generate_report_text(articles)

    text = "Its clear Kid Rock knows his audience and so, apparently, does Donald Trump. On Wednesday night, the singers concert in Evansville, Ind, began with video greeting from the 45th president, which has now been viewed more than half million times on TikTok Flanked by American flags, Trump appeared full of affection both for concertgoers and for Rock, whom he referred to by the singers given name, Bob Immediately after the video ended, Kid Rock launched into performance of his obscenity laced new song, We The People, whose lyrics are filled with partisan rage directed at supporters of the Black Lives Matter movement; people who wear masks to prevent the spread of covid 19; the mainstream media; Anthony Fauci; and using the phrase Lets go, Brandon President Biden, among others."

    synthesize_text(text, f'{output_path}/audio.mp3')

    avatar_image = load_avatar_image('talkinghead/avatar_images/reporter_female.png')
    background_image = cv2.resize(np.array(Image.open('data/cityscape.jpg')) / 255, (256,256))
    generate_unsynced_video(avatar_image, f'{output_path}/video.mp4', f'{output_path}/audio.mp3', background_image)
    combine(output_path)


if __name__ == '__main__':
    '''
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    output_path = f'data/{date_str}'
    os.makedirs(output_path, exist_ok=True)
    #scrape_daily_news(output_path)
    articles = load_articles(f'{output_path}/news.json')
    text = generate_report_text(articles)x
    print(text)
    '''
    main()
