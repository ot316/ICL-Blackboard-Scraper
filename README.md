# ICL-Blackboard-Scraper
This script will login to blackboard and download all the files to labelled directories.
Only tested on Windows so far, but should work on Mac and linux. requires Python 3.6

1. Install Python 3.6
2. Install the dependencies listed in requirements.txt (e.g. using Windows ```pip install requirements.txt```)
3. Install Chrome (the chromedrivers suplied here work with chrome version 85, different drivers can be found [here][1])
4. Run with ```python Blackboard-Scraper.py <username> <password>``` where username and password are your blackboard credentials.

Please get in touch for any comments or improvements olithompson@protonmail.com

## Known issues
1. The script cannot download files through turnitin yet
2. The .py and .mat file types cannot be automatically downloaded as chrome thinks they are a security risk. They will stay on the downloads page and must be manually confirmed before they will download. Then they must then be manually organised.


 [1]: https://chromedriver.chromium.org/downloads
