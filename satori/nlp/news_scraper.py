import time
import json
import random
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from GoogleNews import GoogleNews
from .news_utils import *
import requests
import matplotlib.pyplot as plt
import cv2


HEADER = {'User-Agent': 'Mozilla/5.0'}  # get around 403 forbidden error
ENDPAGE = 1

googlenews = GoogleNews(lang='en', period='1d', encode='utf-8')


def random_delay(base, range):
    time.sleep(base + random.random() * range)


class Newspaper:
    def __init__(self, source):
        self.source = source
        self.urls = []
        self.articles = []

    def crawl(self):
        print(f'Crawling {self.source}...')
        googlenews.search(self.source)

        self.urls.extend(googlenews.get_links())
        for i in range(1, ENDPAGE + 1):
            random_delay(4.123, 10.245)
            googlenews.getpage(i)
            self.urls.extend(googlenews.get_links())

        googlenews.clear()
        self.urls = list(set(self.urls)) # remove duplicates
        print(f'Found {len(self.urls)} articles.')

    def scrape(self):
        self.articles = list(
            filter(lambda x: len(x[2]),
                map(self.scrape_article, self.urls)
            )
        )

    def scrape_article(self, url):
        print(f'Scraping {url}...')
        page = urlopen(Request(url, headers=HEADER))
        random_delay(0, 1.123)
        soup = BeautifulSoup(page, 'html.parser')
        try:
            body = self.parse(soup)
            images = self.scrape_image(soup)
        except:
            return ('', '', [])
        body = filter_text(body) # feel free to add to filter_text regex
        return {
            'source': self.source, 
            'url': url, 
            'text': body,
            'images': images
        }
        
    def scrape_image(self, soup):
        """
        Scrapes images from the article. Returns a generator.
        """
        
        images = []
        for image_soup in soup.find_all('img'):
            image_url = image_soup.get('src')
            caption = image_soup.get('alt')
            if image_url and caption:
                images.append({
                    'url': image_url, 
                    'caption': caption})
        return images


    def get_image(self, image_url):
        bytecodes = requests.get(image_url).content
        nparr = np.frombuffer(bytecodes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
        return image[:,:,::-1]
                
    def parse(self, soup):
        """ Fill this implementation in for subclasses, specialized to newspaper

            General guidelines:
                1) First the method should find all body html components
                2) Convert body components to body texts:
                        body_texts = map(lambda x: x.get_text(), body_soups)
                3) Custom post process
        """
        raise NotImplementedError


class CNN(Newspaper):
    def __init__(self):
        super().__init__('cnn')

    def parse(self, soup):
        body_soups = []
        body_soups.extend(soup.find_all('p', class_='zn-body__paragraph speakable'))
        body_soups.extend(soup.find_all('div', class_='zn-body__paragraph'))
        not_heading = lambda x: not contains_heading(x, ['h3', 'strong'])
        body_soups = filter(not_heading, body_soups)
        body = concat_body_soups(body_soups)
        body = remove_source_tag(body, r'^.*\(CNN.*?\)')
        return body

class NYT(Newspaper):
    def __init__(self):
        super().__init__('new york times')

    def parse(self, soup):
        body_soups = []
        body_soups.extend(soup.find_all('p', class_='css-g5piaz evys1bk0'))
        body = concat_body_soups(body_soups)
        body = remove_source_tag(body, r'^(.* )?[A-Z]+ —')
        return body

class HuffPost(Newspaper):
    def __init__(self):
        super().__init__('huffington post') 

    def parse(self, soup):
        body_soups = []
        body_soups.extend(soup.find_all('div', class_='primary-cli cli cli-text'))
        body = concat_body_soups(body_soups)
        body = remove_source_tag(body, r'^.* [—-] (?=[A-Z])')
        return body


class WaPost(Newspaper):
    def __init__(self):
        super().__init__('washington post')

    def parse(self, soup):
        body_soups = []
        body_soups.extend(soup.find_all('p', class_='font-copy font--article-body gray-darkest ma-0 pb-md'))
        body = concat_body_soups(body_soups)
        body = remove_source_tag(body, r'^(.* )?[A-Z]+ —')
        return body


def scrape_daily_news(save_path):
    newspapers = [CNN(), NYT(), WaPost(), HuffPost()]

    articles = []
    for paper in newspapers:
        paper.crawl()
        paper.scrape()
        articles.append(paper.articles)
        # for source, url, text in paper.articles:
        #     articles.append({
        #         'source': source,
        #         'url': url,
        #         'text': text,
        #     })

    with open(f'{save_path}/news.json', 'w') as fout:
        json.dump(articles, fout, indent=4)

if __name__ == '__main__':
    url = "https://www.cnn.com/europe/live-news/ukraine-russia-putin-news-04-09-22/h_ff5483c56912605145a6806accf7b402"
    cnn = CNN()
    image_url = cnn.scrape_article(url)['images'][0]['url']
    image = cnn.get_image(image_url)
    cv2.imwrite('sample.jpg', image)
