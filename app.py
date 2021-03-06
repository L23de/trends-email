from datetime import date
from typing import Dict, List
from os import path
from cron import keepAlive
import requests
import bs4
import yagmail

# Modify if needed:
TRENDS_TO_SHOW = 10 # Should be less than 20 (If duplicates exist in DAYS_TO_FILTER, email may show less trends than desired)
DAYS_TO_FILTER = 7
RECIPIENTS = []

# No touchie
DUP_TRENDS_PATH = "duplicateTrends.txt"
GTRENDS_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"


def main():
    keepAlive()
    trends = getTrends()
    contents = createEmail(trends)
    subject = f"""Google Trends Top 10 - {date.today().strftime("%m/%d/%y")}"""

    yag = yagmail.SMTP(oauth2_file="oauth2.json")
    if RECIPIENTS:
        yag.send(to=RECIPIENTS, subject=subject, contents=contents)
    else: # Send to self if no RECIPIENTS provided
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

    def soup2dict(list) -> dict:
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


def createEmail(trends: List[dict]) -> List[str]:
    """
    Creates message body for the email
    """
    # Message components
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

    # TODO: Perhaps optimize how to treat trends w/ only 1 news item
    trendCount = 0
    for trend in trends:
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
        """
        if "newsItem_" in trend:
            body += f"""
                    <tr>
                        <td style = "font-size: 20px; font-weight: bold;">{trend["newsItem"]["newsItemTitle"]}</td>
                        <td style = "font-size: 20px; font-weight: bold;">{trend["newsItem_"]["newsItemTitle"]}</td>
                    </tr>
                    <tr>
                        <td>{trend["newsItem"]["newsItemDesc"]}</td>
                        <td>{trend["newsItem_"]["newsItemDesc"]}</td>
                    </tr>
                </table>
            <br>
            </div>
            """
        else:
            body += f"""
                    <tr>
                        <td style = "font-size: 20px; font-weight: bold;">{trend["newsItem"]["newsItemTitle"]}</td>
                    </tr>
                    <tr>
                        <td>{trend["newsItem"]["newsItemDesc"]}</td>
                    </tr>
                </table>
            <br>
            </div>
            """
        contents.append(body)

    return contents


def getTrends() -> List[dict]:
    """
    Checks that trends that are being sent have not been set in the past 'range' days
    Range defaults to previous 7 days
    """

    allTrends = scrape(GTRENDS_RSS)  # Gets all 20 daily trends
    dupList = []

    """
    Deletes duplicates from the past 'range' days from the current trends dictionary
    """
    if path.exists(DUP_TRENDS_PATH):
        with open(DUP_TRENDS_PATH, 'r') as readDup:
            fileContents = readDup.read()
            dupList = fileContents.splitlines()  # Parses newline separated data

            # O(n^2) - Not great, should be optimized
            # index = 0
            tempTrends = allTrends.copy()
            for trend in allTrends:  # Deletes existing duplicates from trends dictionary
                if trend['title'] in dupList:
                    tempTrends.remove(trend)

    else:
        print("File does not exist yet, creating new file to store trends info")

    """
    Deletes trends if past 'range' days and adds today's trends to the list
    """
    # Removes any excess elements in the list and set to global var
    trends = tempTrends[:10] if len(tempTrends) > 10 else tempTrends

    if len(dupList) >= TRENDS_TO_SHOW * DAYS_TO_FILTER:
        dupList = dupList[-TRENDS_TO_SHOW * (DAYS_TO_FILTER - 1):]
    for trend in trends:
        dupList.append(trend['title'])

    """
    Writes today's trends to the text file (acts as a database)
    """
    with open(DUP_TRENDS_PATH, 'w') as writeDup:
        for trend in dupList:
            writeDup.write(f"{trend}\n")

    if len(trends) < TRENDS_TO_SHOW:
        print(
            f"NOTE: Newsletter contains less than {TRENDS_TO_SHOW} items.\nDecreasing the TRENDS_TO_SHOW and DAYS_TO_FILTER variables may help")

    return trends


if __name__ == '__main__':
    main()
