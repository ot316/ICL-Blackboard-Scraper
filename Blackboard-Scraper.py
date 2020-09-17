# This code logs into Blackboard and downloads all files into labelled directories.
# Oli Thompson 17/09/20

import os
from time import sleep
import sys
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def check_args_error():
    if len(sys.argv) != 3:
        print("Incorrect usage, run file as 'python Blackboard-Scraper.py <username> <password>' If your password countains certain special characters such as '$' or ' ' replace them with '\$' and '\ ' etc.")
        sys.exit()


#setup chrome and chromedriver
def setup():
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs',  {
        #"download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
        }
    )
    #options.add_argument("--window-size=1080,720")
    
    
    DRIVER_PATH= os.getcwd() + "/chromedriver" # path to chromedriver exeutable, default to linux
    #check os type and choose drier accordingly
    if platform.system()  == 'Windows':
        DRIVER_PATH += ".exe"
    elif platform.system()  == 'Darwin':
        DRIVER_PATH = os.getcwd() + "/MACOS/chromedriver"
    try:
        scraper = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)   
    except Exception as e: 
        print("Incompatibility between chrome and chromedriver. Download the correct chromedriver for your machine from https://sites.google.com/a/chromium.org/chromedriver/downloads. Ensure it matches the version of chrome you have installed and extract it to this directory, replacing the old file. See below for more error info.\n")
        print(e)
        exit(scraper)
    return scraper


#login to blackboard
def login(USERNAME, PASSWORD, scraper):
    login = scraper.find_element_by_id("username").send_keys(USERNAME)
    password = scraper.find_element_by_id("password").send_keys(PASSWORD)
    submit = scraper.find_element_by_name("_eventId_proceed").click()
    #wait up to 2 seconds for cookie notice to appear
    timeout = 2
    for i in range(0,timeout*10):
        try:
            cookies = scraper.find_element_by_id("agree_button").click()
            break
        except:
            sleep(0.1)
            pass
    try:
        scraper.find_element_by_id("topframe.logout.label")
    except:
        print("login failed, check details. If your password countains certain special characters such as '$' or ' ' replace them with '\$' and '\ ' etc.")
        exit(scraper)
    

# alter the settings to show all modules on the home page if some are hidden
def show_all_modules(scraper):
    settings = scraper.find_element_by_xpath("//a[@title='Manage My Courses Module Settings']").click()
    allcheckboxes = scraper.find_elements_by_xpath("//*[contains(@id,'amc.showcourse._')]")
    for checkbox in allcheckboxes:
        if not checkbox.is_selected():
            scraper.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            checkbox.click()    
            
    submit = scraper.find_element_by_id("bottom_Submit").click()
    navigate_back(scraper, 2)


# navigate back a certain number of pages.
def navigate_back(scraper, number_of_pages):
    scraper.execute_script(f"window.history.go(-{number_of_pages})") 
    try:
        scraper.find_element_by_xpath("//*[contains(text(), 'Imperial College London Authentication - Stale Request')]")
        print("stale request, too far back, moving forwards to home page")
        scraper.execute_script("window.history.go(1)") 
    except:
        pass    


# scans the home page for modules
def scan_for_modules(scraper):
    container = scraper.find_element_by_xpath("//div[contains(@id, 'div_4_1')]")
    modules = container.find_elements_by_xpath('.//a')
    return modules


# scans for links inside a module
def scan_for_links(scraper):
    items = scraper.find_element_by_xpath("//ul[contains(@id, 'content_listContainer')]")
    links = items.find_elements_by_xpath('.//a[not(contains(@class, "button"))]')    
    return links

  
def exit(scraper):
    scraper.quit()
    print("Closing down")
    sys.exit()

# main
if __name__ == "__main__":
    check_args_error()
    scraper = setup()
    URL = "https://bb.imperial.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1"
    scraper.get(URL)    
    USERNAME= sys.argv[1]
    PASSWORD = sys.argv[2]
    login(USERNAME, PASSWORD, scraper)
    main_window = scraper.current_window_handle
    #show_all_modules(scraper)
    for i in range(0,len(scan_for_modules(scraper))):
        sleep(1)
        modules = scan_for_modules(scraper)
        modules[i].click()
        for ii in range(0,len(scan_for_links(scraper))):
            sleep(0.5)
            links = scan_for_links(scraper)
            try:
                links[ii].click()              
            except:
                pass
            # check if a new tab has been opened, if it has it is moved to the background rather than navigating back.
            if len(scraper.window_handles) > 1:
                scraper.switch_to.window(main_window)
            else:
                navigate_back(scraper, 1)     
        navigate_back(scraper, 5)      

            
    exit(scraper)