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


# Checks Python version at runtime
def check_version(version):
    version = str(version)
    log_print(f"Using Python {sys.version}")
    if sys.version_info[0] < int(version[0]) or sys.version_info[1] < int(version[2]):
        log_print(f"Must be using Python {version}")
        raise Exception(f"Must be using Python {version}")
        
# clear the argument directory of data
def purge_data(folder):
    shutil.rmtree(folder)
    log_print(f"'{folder}' Directory purged")
    os.mkdir(folder)

# setup chrome and chromedriver
def setup(download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs',  {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
        }
    )
    chrome_options.add_argument("--window-size=1080,720")
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


# login to blackboard
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
    
# This function checks if the module uses blackboard's table of contents structure and behaves slightly differently.
def check_for_contents(scraper):
    try:
        contents = scraper.find_element_by_xpath("//h2[@id='tocTitle']") 
        print("contents mode")        
        count = 1
    except:
        return False
    while True:
        cleanup_tabs(scraper)
        try:
            url = scraper.find_element_by_xpath("//a[contains(text(), 'here')]").get_attribute('href') + "&launch_in_new=true"
            scraper.get(url)
            scraper.switch_to.window(main_window)
            navigate_back(scraper, 1)                        
        except:
            try:
                body = scraper.find_element_by_xpath("//ul[@class='attachments clearfix']")
                pdf = body.find_element_by_xpath(".//a").get_attribute('href')
                scraper.get(pdf)   
                scraper.switch_to.window(main_window)                
            except:
                pass
        try:
            sleep(0.1)
            next_button = scraper.find_element_by_xpath('//img[@alt="Next item"]').click()
            count += 1
        except:
            navigate_back(scraper, count)
            return True

# alter the blackboard settings to show all modulezzzs on the home page if some are hidden. Comment out the call to this function if you only wish to scrape certain modules.
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
        
# scan page for links, and click each one providing it is not an email address. When a link is clicked the function is called recursively and all links inside that link are clicked and so on.
def click_all_links(scraper):
    cleanup_tabs(scraper)
    for i in range(0,len(scan_for_links(scraper))):
        links = scan_for_links(scraper)
        url = scraper.current_url      
        try:
            sleep(0.1)
            # ignore emails
            if '@' not in links[i].text:
                links[i].click()
            else:
                log_print("Ignoring Email")
            contents = False
            contents = check_for_contents(scraper)
            scraper.switch_to.window(main_window)
            try:
                scraper.find_element_by_xpath("//*[@text()='Submit Turnitin Assignment']")
                turnitin_download(scraper)
            except:
                pass
            # If the url has changed, that means a new page has loaded and the navigate_back function must be called after it has been scanned. If it is just a file that is downloaded, 
            # the url will be the same and the navigate_back function does not need to be called.
            if not url == scraper.current_url and not contents:
                click_all_links(scraper)
                navigate_back(scraper, 1)
            else:
                log_print("Link opened or file downloaded...")
        except:
            pass


# navigate back a certain number of pages.
def navigate_back(scraper, number_of_pages):
    for i in range(0,number_of_pages):
        scraper.execute_script(f"window.history.go(-1)") 
        # if the function navigates too far backwards, it checks for the stale request warning page and moves back forwards 1 page.
        try:
            scraper.find_element_by_xpath("//*[contains(text(), 'Imperial College London Authentication - Stale Request')]")
            log_print("Stale request, navigated too far back, moving forwards to home page")
            scraper.execute_script("window.history.go(1)") 
            return
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
            links = []         
    return links


def turnitin_download(scraper):
    #to do
    pass

# close extraneous tabs
def cleanup_tabs(scraper):
    scraper.switch_to.window(main_window)
    while len(scraper.window_handles) > 2:
        keyboard.press_and_release('ctrl+tab')
        keyboard.press_and_release('ctrl+tab')
        sleep(0.3)
        keyboard.press_and_release('ctrl+w')
        sleep(0.3)
        scraper.switch_to.window(main_window)


# organise downloaded files into a directory named with the module title
def organise_files(name):  
    # check if downloads are still in progress by looking for .crdownload files
    def download_check(source):
        files = os.listdir(source)
        for file in files:
            if file.endswith('.crdownload') and not file[12:-11].isnumeric():
                log_print("Waiting for files to finish downloading...")
                log_print(file)
                sleep(5)                
                download_check(source)

            
    try:
        os.mkdir(name)
    except Exception as e:
        log_print(f"\nFailed to create module directory. \n{str(e)}\nAssuming that the directory already exists and continuing...\n")
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
    # move files from temprary data diretory to labelled new directory
    for file in files:
        if not file.endswith('.crdownload'):
            shutil.move(source + file, dest)
    log_print("Files Moved\n")    
        
# quit the program        
def exit(scraper):
    scraper.quit()
    log_print("Closing down")
    sys.exit()


# main
if __name__ == "__main__":
    # clear log
    open("log.txt", "w").close()
    log_print("Clearing log.txt")
    purge_data('data')
    check_version(3.6)
    disclaimer()
    check_args_error()
    if platform.system()  == 'Windows':
        data_dir = os.getcwd() + '\data'
        scraper = setup(data_dir)
        log_print(f"Download directory is: {data_dir}")
    else:    
        scraper = setup(os.getcwd() + '/data')  
    URL = "https://bb.imperial.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1"
    scraper.get(URL)    
    USERNAME= sys.argv[1]
    PASSWORD = sys.argv[2]
    login(USERNAME, PASSWORD, scraper)
    main_window = scraper.current_window_handle
    #show_all_modules(scraper)
    # Iterate through modules
    for i in range(0,len(scan_for_modules(scraper))):
        sleep(1)
        modules = scan_for_modules(scraper)
        module_name = modules[i].text
        log_print(f"Scraping '{module_name}'")
        modules[i].click()
        # Look for content in the following directories 
        content = 'Course Content'
        other_content = ['Week Materials', 'Module Descriptor', 'Additional info', 'Assignment Information', 'Assignment Submission']
        # check for course content first, if not present scraper the home directory.
        try:
            scraper.find_element_by_xpath(f"//span[contains(text(), '{content}')]").click()
            click_all_links(scraper)
        except:
            click_all_links(scraper)
        # now scrape the other directories
        for content in other_content:
            try:
                scraper.find_element_by_xpath(f"//span[contains(text(), '{content}')]").click()
                click_all_links(scraper)
                sleep(0.5)
                log_print(f"Checked: {content}")
            except:
                pass
        navigate_back(scraper, 8)
        organise_files(module_name)
        log_print(f"\nFiles downloaded and organised for '{module_name}'\n")
    log_print("Scraping Finished")
    files = os.listdir(data_dir)
    for file in files:
        if file.endswith('.crdownload') and file[12:-11].isnumeric():
            log_print("A file has a warning and couldn't be downloaded automatically, probably because chrome has deteccted it as a threat. It will remain in the download page of chrome and must be downloaded and organised manually.")              
    exit(scraper)
