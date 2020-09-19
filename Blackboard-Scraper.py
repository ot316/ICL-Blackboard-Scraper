# This code logs into Blackboard and downloads all files into labelled directories.
# Oli Thompson 17/09/20

import os
from time import sleep
import sys
import platform
import shutil
import keyboard
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# appends the debug I/O to a log.txt file
def log_print(output):
    print(output)
    with open("log.txt", "a") as log:
        log.write("\n" + output)
        
# checks correct number of arguments        
def check_args_error():
    if len(sys.argv) != 3:
        log_print("Incorrect usage, run file as 'python Blackboard-Scraper.py <username> <password>' If your password countains certain special characters such as '$' or ' ' replace them with the escape characters'\$' and '\ ' etc.\nIf this doesn't work, try encapsulating the password in inverted commas e.g. \"^193*()&^\"")
        sys.exit()

# user warning notice
def disclaimer():
    log_print("\nIMPORTANT\nThis script will open an automated browser window and will navigate blackboard and download the files.\nThe script uses keyboard shortcuts to manage tabs, if you manually change windows then these shortuts will register on the new current window,\nthis may have unpredictable or dangerous effects.\nBecause of this please do not click outside the browser window when the sript is running.\nIf you have already run the script and have some files have downloaded, be aware that running it again will overwrite all files.\nPress 'y' to continue, any other key to abort.")
    text = input()
    if text.lower() != "y":
        sys.exit()
    log_print("\n")
        
# clear the argument directory of data
def purge_data(folder):
    shutil.rmtree(folder)
    log_print(f"'{folder}' Directory purged")
    os.mkdir(folder)

#setup chrome and chromedriver
def setup(download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs',  {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
        }
    )
    chrome_options.add_argument("--window-size=1080,780")
    DRIVER_PATH= os.getcwd() + "/Linux/chromedriver" # path to chromedriver exeutable, default to linux
    #check os type and choose driver accordingly
    if platform.system()  == 'Windows':
        DRIVER_PATH = os.getcwd() + "\Windows\chromedriver.exe"
    elif platform.system()  == 'Darwin':
        DRIVER_PATH = os.getcwd() + "/MACOS/chromedriver"
    try:
        scraper = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)   
    except Exception as e: 
        log_print("Incompatibility between chrome and chromedriver. Download the correct chromedriver for your machine from https://sites.google.com/a/chromium.org/chromedriver/downloads. Ensure it matches the version of chrome you have installed and extract it to this directory, replacing the old file. See below for more error info.\n")
        log_print(e)
        exit(scraper)
    return scraper


#login to blackboard
def login(USERNAME, PASSWORD, scraper):
    login = scraper.find_element_by_id("username").send_keys(USERNAME)
    password = scraper.find_element_by_id("password").send_keys(PASSWORD)
    submit = scraper.find_element_by_name("_eventId_proceed").click()
    try:
        scraper.find_element_by_id("topframe.logout.label")
        log_print("Login Successful\n")
    except:
        log_print("login failed, check details. If your password countains certain special characters such as '$' or ' ' replace them with the escape characters'\$' and '\ ' etc.\nIf this doesn't work, try encapsulating the password in inverted commas e.g. \"^193*()&^\"")
        exit(scraper)
    #wait up to 2 seconds for cookie notice to appear
    timeout = 2    
    for i in range(0,timeout*10):
        try:
            cookies = scraper.find_element_by_id("agree_button").click()
            break
        except:
            log_print("Cookie form not detected, retrying...")
            sleep(0.5)
            pass    
    

# alter the blackboard settings to show all modules on the home page if some are hidden. Comment out the call to this function if you only wish to scrape certain modules.
def show_all_modules(scraper):
    settings = scraper.find_element_by_xpath("//a[@title='Manage My Courses Module Settings']").click()
    allcheckboxes = scraper.find_elements_by_xpath("//*[contains(@id,'amc.showcourse._')]")
    for checkbox in allcheckboxes:
        if not checkbox.is_selected():
            scraper.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            checkbox.click()    
    submit = scraper.find_element_by_id("bottom_Submit").click()
    navigate_back(scraper, 2)
    sleep(1)
        
# scan page for links and click each one, when a link is clicked the function is called recursively and all links inside that link are clicked and so on.
def click_all_links(scraper):
    cleanup_tabs(scraper)
    for i in range(0,len(scan_for_links(scraper))):
        links = scan_for_links(scraper)
        url = scraper.current_url      
        try:
            sleep(0.1)
            links[i].click()
            scraper.switch_to.window(main_window)
            # If the url has changed, that means a new page has loaded and the navigate_back function must be called after it has been scanned. If it is just a file that is downloaded, 
            # the url will be the same and the navigate_back function does not need to be called.
            if not url == scraper.current_url:
                click_all_links(scraper)
                navigate_back(scraper, 1)
            else:
                log_print("Link opened or file downloaded...")
        except:
            pass


# navigate back a certain number of pages.
def navigate_back(scraper, number_of_pages):
    scraper.execute_script(f"window.history.go(-{number_of_pages})") 
    # if the function navigates too far backwards, it checks for the stale request warning page and moves back forwards 1 page.
    try:
        scraper.find_element_by_xpath("//*[contains(text(), 'Imperial College London Authentication - Stale Request')]")
        log_print("Stale request, navigated too far back, moving forwards to home page")
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
    try:
        items = scraper.find_element_by_xpath("//ul[contains(@id, 'content_listContainer')]")
        links = items.find_elements_by_xpath('.//a[not(contains(@class, "button"))]')
    except:
        try:
            log_print("No further links found, looking for submitted file")
            items = scraper.find_element_by_xpath("//ul[contains(@id, 'currentAttempt_submissionList')]")
            links = items.find_elements_by_xpath('.//a[not(contains(@class, "button"))]')
        except:
            log_print("No further links found, returning...")
            links = []
    return links


def cleanup_tabs(scraper):
    scraper.switch_to.window(main_window)
    while len(scraper.window_handles) > 2:
        keyboard.press_and_release('ctrl+tab')
        keyboard.press_and_release('ctrl+tab')
        sleep(0.1)
        keyboard.press_and_release('ctrl+w')
        sleep(0.1)
        scraper.switch_to.window(main_window)


def organise_files(name):   
    def download_check(source):
        files = os.listdir(source)
        for file in files:
            if file.endswith('.crdownload'):
                log_print("Waiting for files to finish downloading...")
                sleep(5)                
                download_check(source)

            
    try:
        os.mkdir(name)
    except Exception as e:
        log_print("\nFailed to create module directory. \n" + str(e) + "\nAssuming that the directory already exists and continuing...\n")
        pass
    log_print(name + " Directory created\n")
    # change filepath depending on operating system
    if platform.system()  == 'Windows':
        source = "data\\"
        dest = f'{name}\\'
    else:    
        source = "data/"
        dest = f'{name}/'
    purge_data(dest)
    download_check(source)
    files = os.listdir(source)
    for file in files:    
        shutil.move(source + file, dest)
    log_print("Files Moved\n")    
        
        
def exit(scraper):
    scraper.quit()
    log_print("Closing down")
    sys.exit()


# main
if __name__ == "__main__":
    open("log.txt", "w").close()
    log_print("Clearing log.txt")
    purge_data('data')    
    disclaimer()
    check_args_error()
    if platform.system()  == 'Windows':
        scraper = setup(os.getcwd() + '\data')
    else:    
        scraper = setup(os.getcwd() + '/data')  
    URL = "https://bb.imperial.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1"
    scraper.get(URL)    
    USERNAME= sys.argv[1]
    PASSWORD = sys.argv[2]
    login(USERNAME, PASSWORD, scraper)
    main_window = scraper.current_window_handle
    show_all_modules(scraper)
    for i in range(0,len(scan_for_modules(scraper))):
        sleep(1)
        modules = scan_for_modules(scraper)
        module_name = modules[i].text
        modules[i].click()
        click_all_links(scraper)
        navigate_back(scraper, 2)
        organise_files(module_name)
        log_print(f"\nFiles downloaded and organised for '{module_name}'\n")
    exit(scraper)