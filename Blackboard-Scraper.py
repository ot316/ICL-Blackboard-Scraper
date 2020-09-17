import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH= os.getcwd() + "/chromedriver"
if os.name == 'nt':
    DRIVER_PATH += ".exe"
try:
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)   
except:
    print("Incompatible version of chrome and chromedriver. Download the correct chromedriver from https://sites.google.com/a/chromium.org/chromedriver/downloads and extract it to this directory, replacing the old file.")
    sys.exit()
driver.get("https://www.olithompson.com/")
print(driver.page_source)
driver.quit()