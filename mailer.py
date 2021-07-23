from datetime import date
from dotenv import load_dotenv
import yagmail
import os

# Loads env variables from local .env file
load_dotenv()


class Mailman():
    # Requires trendsList to be passed when creating a Mailer obj
    def __init__(self, trendsList: dict) -> None:
        self.trends = trendsList

    def sendMail(self):
        # Access to sender email
        email = os.environ.get("email")
        password = os.environ.get("password")

        # Formats today's date
        today = date.today()
        mdyy = today.strftime("%m/%d/%y")
        mmdyyyy = today.strftime("%B %d, %Y")

        # Message components
        to = os.environ.get("recv")
        subject = f"Google Trends Top 10 - {mdyy}"
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
                        <td style="text-align: right;">{mmdyyyy}</td>
                        </tr>
                    </table>
                <hr>
            </div>
        </div>
        """
        contents = [header]

        # TODO: Fix how scraper stores the two news items
        trendCount = 0
        for trend in self.trends:
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
            if trendCount >= 10:
                break

        yag = yagmail.SMTP(email, password)
        yag.send(to=to, subject=subject, contents=contents)
