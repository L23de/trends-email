import requests
import bs4

res = requests.get(
    'https://trends.google.com/trends/trendingsearches/daily/rss?geo=US')
trends = dict()

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
    if len(list) == 0:  # Default case
        return

    newDict = dict()
    for tag in list:
        if tag.name in tagToKey:  # Only includes values we need
            newDict[tagToKey[tag.name]] = soup2dict(tag.contents)
    return newDict


if res.status_code == 200:
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all('item')

    for item in items:
        trends[item.title] = soup2dict(item.contents)

    trends = soup2dict(items)
    print(trends)
    # print(soup.prettify)
    # Loops through each item in the list
    # for item in soup.find_all('item'):
    # trends[item.title] = {
    # 	'traffic': item.approx_traffic,
    # 	'description': item.description,
    # 	'pictureSource': item.picture,
    # }
else:
    print(f"Error: Status code {res.status_code})")
