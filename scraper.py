import requests
from mailer import Mailer
import bs4

res = requests.get(
    'https://trends.google.com/trends/trendingsearches/daily/rss?geo=US')

'''
Converts from XML tags to dictionary-friendly keys
Also used to filter out unwanted entries
'''
tagToKey = {
    'title': 'title',
    'ht:approx_traffic': 'traffic',
    'description': 'desc',
    'ht:picture': 'pictureSrc',
    'ht:news_item': 'newsItem',
    'ht:news_item_title': 'newsItemTitle',
    'ht:news_item_snippet': 'newsItemDesc',
    'ht:news_item_url': 'newsItemURL',
}


def soup2dict(list):
    '''
    Converts a BeautifulSoup object into a dictionary
    '''
    if len(list) == 1:
        return list[0]

    newDict = dict()
    for tag in list:
        if tag.name in tagToKey:  # Only includes values we need
            newDict[tagToKey[tag.name]] = soup2dict(tag.contents)
    return newDict


if res.status_code == 200:
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all('item')
    trends = []

    for item in items:
        trends.append(soup2dict(item.contents))

else:
    print(f"Error: Status code {res.status_code})")
