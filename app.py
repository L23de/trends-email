from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# Run selenium in headless mode
opts = Options()
opts.add_argument(" --headless")

# Path to browser's exec
opts.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\Chrome.exe"
# Path to web driver 
chrome_driver = os.getcwd() + "\\chromedriver.exe"

# Scrapes url w/ dynamic JS
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
driver.get("https://trends.google.com/trends/trendingsearches/daily?geo=US")

# Loads into BeautifulSoup object
soup_file = driver.page_source
soup = BeautifulSoup(soup_file, features="html.parser")

# Scrape like static page
print(soup.title)

# Closes chrome driver
driver.quit()