from datetime import date
from typing import Dict, List
from dotenv import load_dotenv
import requests
import bs4
import yagmail
import os

# Loads env variables from local .env file
load_dotenv()

# Gets OAUTH ID and PASS from .env file in root
# IMPORTANT: Add a .env file and add both fields
GOOGLE_CLIENT_ID = os.environ.get("OAUTH_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("OAUTH_PASS")
GOOGLE_REFRESH_TOKEN = None

GTRENDS_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"


def scrape(linkToScrape: str):
    """
    Provides a method to scrape a XML file using the requests library and bs4
    """

    res = requests.get(linkToScrape)

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
        Converts a XML-formatted BeautifulSoup object into a dictionary
        '''
        if len(list) == 1:
            return list[0]

        newDict = dict()
        for tag in list:
            if tag.name in tagToKey:  # Only includes values we need
                newDict[tagToKey[tag.name]] = soup2dict(tag.contents)
        return newDict

    trends = []
    if res.status_code == 200:
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all('item')

        for item in items:
            trends.append(soup2dict(item.contents))
    else:
        print(f"Error: Status code {res.status_code})")

    return trends


def createEmail(trends: List[Dict]):
    # Formats today's date
    today = date.today()
    fDate = today.strftime("%B %d, %Y")

    # Message components
    # TODO: Fix the header logo
    header = f"""
    <div id="Header">
        <div id="Header Logo">
            <img src="attachments/TodayOnGTrends.png" alt ="Today On Google Trends Logo" style="display: block; margin-left: auto; margin-right: auto;">
        </div>
        <div id="About Me">
            <hr>
            <table width=100%>
                    <tr>
                    <td style="text-align: left">Created by: <a href = "https://github.com/L23de/trends-email">Lester Huang</a></td> 
                    <td style="text-align: right;">{fDate}</td>
                    </tr>
                </table>
            <hr>
        </div>
    </div>
    """
    contents = [header]

    # TODO: Fix how scraper stores the two news items
    trendCount = 0
    for trend in trends:
        trendCount = trendCount + 1
        body = f"""
        <div id="trend{trendCount}">
            <a href="{trend["newsItem"]["newsItemURL"]}">
                <img src={trend["pictureSrc"]} alt={trend["desc"]} width="200" height="200" style="float: left;">
            </a>
            <p style="clear: left; float: left;">
                <h1>{trend["title"]} [{trend["traffic"]} Searches]</h1>
                <div id="news-items" style="display: table;">
                    <div id="news-item" style="float: left; width: 50%;">
                            <h3>{trend["newsItem"]["newsItemTitle"]}</h3>
                            <p>{trend["newsItem"]["newsItemDesc"]}</p>
                    </div>
                </div>
            </p>
        </div>
        <br>
        """
        contents.append(body)
        if trendCount >= 10:  # Only sends top 10 trends
            break

    return contents


if __name__ == '__main__':
    fromAddr = os.environ.get("from")
    toAddr = os.environ.get("to")
    trends = scrape(GTRENDS_RSS)
    contents = createEmail(trends)

    today = date.today()
    fDate = today.strftime("%m/%d/%y")
    subject = f"Google Trends Top 10 - {fDate}"

    yag = yagmail.SMTP(to=toAddr, oauth2_file="oauth2.json")
    yag.send(to=toAddr, subject=subject, contents=contents)
