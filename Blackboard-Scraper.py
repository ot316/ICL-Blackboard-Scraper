import os
from time import sleep
import sys
import platform
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

options = Options()
#options.headless = True
options.add_argument("--window-size=1080,720")
DRIVER_PATH= os.getcwd() + "/chromedriver"
if platform.system()  == 'Windows':
    DRIVER_PATH += ".exe"
elif platform.system()  == 'Darwin':
    DRIVER_PATH += "_mac"
try:
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)   
except Exception as e: 
    print("Incompatibility with chrome and chromedriver. Download the correct chromedriver for your machine from https://sites.google.com/a/chromium.org/chromedriver/downloads and extract it to this directory, replacing the old file. See below for more.\n")
    print(e)
    sys.exit()
driver.get("https://bb.imperial.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1")

#login
USERNAME= sys.argv[1]
PASSWORD = sys.argv[2]
login = driver.find_element_by_id("username").send_keys(USERNAME)
password = driver.find_element_by_id("password").send_keys(PASSWORD)
submit = driver.find_element_by_name("_eventId_proceed").click()
sleep(1)
try:
    cookies = driver.find_element_by_id("agree_button").click()
except:
    pass

#show all modules
settings = driver.find_element_by_xpath("//a[@title='Manage My Courses Module Settings']").click()
allcheckboxes = driver.find_elements_by_xpath("//*[contains(@id,'amc.showcourse._')]")
for checkbox in allcheckboxes:
    if not checkbox.is_selected():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        checkbox.click()    
        
submit = driver.find_element_by_id("bottom_Submit").click()
driver.execute_script("window.history.go(-2)")
        
#driver.quit()
