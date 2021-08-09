# trends-email

Trends Email is a simple program that can run locally or on the cloud to send daily newsletters about the [latest search trends][1] powered by Google Trends

<p align="center">
   <img src="attachments/TodayOnGTrends.png" alt="Trends Email Logo" width=400>
</p>

## Usage

### Setting up OAuth

Follow instructions on [this page][2] to set up your Google OAuth2 token\
You may have to create a project first, as well as a OAuth consent screen, which will automatically be shown if you try to create a OAuth client ID\
Keep your OAuth client ID and secret safe

### Installing

```bash
$ git clone git@github.com:L23de/trends-email.git
$ cd trends-email
$ pip install pipenv
$ pipenv install
```

This clones the repo to your local machine, as well as sets up a virtual environment and installs the appropriate dependencies required

Inside `app.py`, modify the global variables to your desire:

```python
TRENDS_TO_SHOW = 10 # Max num. of trends that show up in the newsletter (Max is 20)
DAYS_TO_FILTER = 7 # Continuously trending trends will be filtered out for this amount of days
RECIPIENTS = [] # Recipient List, list of email strings
```

Run the program:

```bash
$ python app.py
```

> You may have to use `pip3`, `python3` if `pip`, `python` does not work for you

### First Run - Configuring OAuth

On the first run, you will get prompted for the OAuth client ID and secret generated at the beginning\
Enter them in the terminal, note that the password input is hidden, so just paste and hit enter

```
Your 'email address': <your-email>
Your 'google_client_id': <client-id-from-gcp>
Your 'google_client_secret': <client-secret-from-gcp>
Navigate to the following URL to auth:
<Permission URL>
Enter verification code: <code-from-clicking-on-url>
```

If everything goes well, an `oauth2.json` file will be generated in the root directory, this will allow you to use the program without having to go through the OAuth configuration again

### You've got mail!

Check your inbox, and a fresh new email should be there, and now you know what's trending!

## Roadmap

- [x] Using [Google's OAuth2][2] to authenticate emails (Currently storing account credentials locally)
- [x] Adding a filter for trends that may occur multiple times in a short time period
- [ ] Improving the email layout (HTML/CSS)
- [ ] Adding a config file for easy configuration (Email frequency, filter time period, recipients list, etc)
- [x] Launch it in a container or on the cloud to automatically send newsletters (Catch: No free options, can self host)

[1]: https://trends.google.com/trends/trendingsearches/daily?geo=US "Google Trends Link"
[2]: https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html "Google OAuth2 using Python"
