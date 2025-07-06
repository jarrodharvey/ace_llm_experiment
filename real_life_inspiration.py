import random
import requests
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import sys
import argparse
import base64

parser = argparse.ArgumentParser(
                    prog='real_life_inspiration',
                    description='A script to fetch a random legal case from the NSWCCA website and display its content.',
                    epilog='Use this script to get inspired by real-life legal cases.')

parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt the output')

should_encrypt = parser.parse_args().encrypt

years = list(range(1998, 2026))
entries = list(range(1, 200))

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def get_random_case_url():
    """
    Generate a random URL for a case from the NSWCCA website.
    """
    # Randomly select a year and entry numbe
    year = random.choice(years)
    entry = random.choice(entries)
    url = f"https://www.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWCCA/{year}/{entry}.html"
    return url

# Attempt get_random_case_url until you get one that is not a 404
while True:
    try:
        url = get_random_case_url()
        response = requests.get(url)
        if response.status_code == 404:
            continue
        else:
            break
    except Exception as e:
        print(f"Error fetching URL: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        continue

Website = requests.get(url, headers= {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3835.0 Safari/537.36', 'Accept': '*/*'})

website_text = text_from_html(Website.text)

# If required encode in base 64
if should_encrypt: 
    website_text = base64.b64encode(website_text.encode('utf-8')).decode('utf-8')

print(website_text) 