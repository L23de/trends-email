from datetime import date
from typing import Dict, List
import requests
import bs4
import yagmail
# import json

DAYS_TO_FILTER = 7
TRENDS_TO_SHOW = 10 # Should be less than 20 (If duplicates exist in DAYS_TO_FILTER, email may show less trends than desired)
DUP_TRENDS_PATH = "duplicateTrends.txt"
GTRENDS_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"

def main():
    # List of emails, defaults to oauth2.json email (Send to self)
    recipients = []

    trends = scrape(GTRENDS_RSS)
    contents = createEmail(trends)
    subject = f"""Google Trends Top 10 - {date.today().strftime("%m/%d/%y")}"""

    yag = yagmail.SMTP(oauth2_file="oauth2.json")
    yag.send(subject=subject, contents=contents)
    yag.close()


def scrape(linkToScrape: str) -> Dict:
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
                tagName = tagToKey[tag.name]
                # For news item (Avoids overwriting and preserves duplicate XML tags)
                if tagName in newDict:
                    tagName += '_'
                newDict[tagName] = soup2dict(tag.contents)
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


def createEmail(trends: List[Dict]) -> List[str]:
    """
    Creates message body for the email
    """
    # Message components
    # TODO: Fix the header logo
    logoURL = "https://raw.githubusercontent.com/L23de/trends-email/main/attachments/TodayOnGTrends.png"
    css = """
    newsItem {

    }
    """
    header = f"""
    <div id="Header">
        <div id="Header Logo">
            <img src="{logoURL}" alt ="Today On Google Trends Logo" style="display: block; margin-left: auto; margin-right: auto;">
        </div>
        <div id="About Me">
            <hr>
            <table width=100%>
                    <tr>
                    <td style="text-align: left">Created by: <a href = "https://github.com/L23de/trends-email">Lester Huang</a></td> 
                    <td style="text-align: right;">{date.today().strftime("%B %d, %Y")}</td>
                    </tr>
                </table>
            <hr>
        </div>
    </div>
    """
    contents = [header]

    # TODO: Fix how scraper stores the two news items
    trendCount = 0
    for trend in (trend for trend in trends if trendCount < TRENDS_TO_SHOW):
        trendCount += 1
        body = f"""
        <div id="trend{trendCount}">
            <table width=100%>
                <tr>
                    <th rowspan="3" valign="top">
                        <a href="https://www.google.com/search?q={trend["title"]}">
                        <img src={trend["pictureSrc"]} alt={trend["desc"]} width="250" height="250">
                        </a>
                    </th>
                    <th style="text-align: left; font-size: 30px">{trend["title"]} [{trend["traffic"]} Searches]</th>
                </tr>
                <tr>
                    <td style="font-size: 20px; font-weight: bold;">{trend["newsItem"]["newsItemTitle"]}</td>
                    <td style="font-size: 20px; font-weight: bold;">{trend["newsItem_"]["newsItemTitle"]}</td>
                </tr>
                <tr>
                    <td>{trend["newsItem"]["newsItemDesc"]}</td>
                    <td>{trend["newsItem_"]["newsItemDesc"]}</td>
                </tr>
            </table>
        <br>
        </div>
        """
        contents.append(body)

    return contents


def checkTrend(trends: List[Dict], range: int = 7) -> List[Dict]:
    """
    Checks that trends that are being sent have not been set in the past 'range' days
    Range defaults to previous 7 days
    """

    # TODO: When calling checkTrend(), check that range > 0

    dupList = [] # Allows duplicates opposed to a set
    with open(DUP_TRENDS_PATH, 'r+') as dupFile:
        """
        Deletes duplicates from the past 'range' days from the current trends dictionary
        """
        fileContents = dupFile.read()
        dupList = fileContents.splitlines() # Parses newline separated data
        dupSize = len(dupList)

        for dup in dupList: # Deletes existing duplicates from trends dictionary
            if dup in trends:
                del trends[dup]


        """
        Deletes trends if past 'range' days (Takes note that it doesn't write trends yet)
        """
        if dupSize >= TRENDS_TO_SHOW * DAYS_TO_FILTER:
            pass
        

        """
        Writes today's trends to the dictionary
        """
        postNum = 0
        for trend in  (trend for trend in trend.keys() if postNum < TRENDS_TO_SHOW):
            postNum += 1
            dupFile.write(f"{trend}\n")


if __name__ == '__main__':
    main()
