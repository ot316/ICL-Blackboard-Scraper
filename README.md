# ICL-Blackboard-Scraper
This script will login to blackboard and download all the files to labelled directories.
Only tested on Windows so far, but should work on Mac and linux. requires Python 3.6

The scraper looks through the modules that are visible on blackboard's homepage, you can control which modules will be scraped by showing and hiding modules, this can be done through the settings button see below.

<img src="https://github.com/ot316/ICL-Blackboard-Scraper/blob/master/screenshot.PNG" alt="screenshot" width="500"/>

## Usage

1. Install Python 3.6
2. Install the dependencies listed in requirements.txt (e.g. using Windows ```pip install -r requirements.txt```)
3. Install Chrome (the chromedrivers supplied here work with chrome version 85, different drivers can be found [here][1])
4. Run with ```python Blackboard-Scraper.py <username> <password>``` where username and password are your blackboard credentials.

## Known issues
1. The script cannot download files submitted through turnitin yet.
2. The .py and .mat file types cannot be automatically downloaded as chrome thinks they are a security risk. They will stay on the downloads page and must be manually confirmed (after the script has finished) before they will download. They must then be manually organised.

Please get in touch for any comments or improvements olithompson@protonmail.com

 [1]: https://chromedriver.chromium.org/downloads
