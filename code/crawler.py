"""
Copyright 2023,Max Planck Institute for Security and Privacy
Sushil Ammanaghatt Shivakumar <sushil.shivakumar@mpi-sp.org,sushilkumar.shilsuba@gmail.com>
"""

from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
import pandas as pd

# predefined coookie list
Df = pd.read_csv("read_files/cookie_list.csv")
cbanner_list = list(Df["0"])

# Constants
max_waiting_time = 30


def check_soup(all_sources, name):
    # To get paragraphs that contain Legitimate interest 
    soup = BeautifulSoup(all_sources, "html.parser")

    elements = soup.find_all(
        string=lambda text: 'legitimate interest' in text or 'legitimate interests' in text)
    
    unique_ones = set(elements)
    with open(f"output_files/page_data/{name}.txt", 'w') as f:
        for ones in unique_ones:
            f.write(str(ones))
            f.write("\n")
    


def init_driver():
    """
        Initialise/create the driver
    """

    """
    Use this options for full sized screenshot (Does not work for all websites)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')
    driver = webdriver.Chrome(
    ChromeDriverManager().install(),options=chrome_options)
    
    ****************************************************************************
    
    for translating the website to english
    options = webdriver.ChromeOptions()
                options.add_experimental_option(
                    'prefs', {'intl.accept_languages': 'en,en_US'})
                driver = webdriver.Chrome(chrome_options=options)
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.set_page_load_timeout(max_waiting_time)

    return driver

def determine_purpose(text_around, name):
    """
        A predefined set of purposes are checked here!!
    """
    purposes = [
        "purpose",
        "store and/or access information on a device",
        "select basic ads",
        "create a personalised ads profile",
        "select personalised ads",
        "create a personalised content profile",
        "select personalised content",
        "measure ad performance",
        "measure content performance",
        "market research",
        "audience insights",
        "develop and improve products",
        "ensure security, prevent fraud, debug",
        "technically deliver"
    ]

    purpose_ = {purpose: False for purpose in purposes}
    
    for purpose in purposes:
        if purpose in text_around or purpose.replace("personalised", "personalized") in text_around:
            purpose_[purpose] = True
    purpose_['website'] = name

    return purpose_


def banner_ss(driver, name="x.png"):
    """
    Code to take screenshot of Cookie banner
    """
    time.sleep(2)
    # resize the browser window
    # driver.set_window_size(1300, 1400)
    S = lambda X: driver.execute_script(
        'return document.body.parentNode.scroll' + X)
    driver.set_window_size(S('Width'), S('Height'))
    banner = driver.find_element(By.CSS_SELECTOR, 'div[role=dialog]')
    # resize the banner
    driver.execute_script(
        "arguments[0].setAttribute('style', 'max-height: 1800px;')", banner)
    time.sleep(1)
    banner.screenshot(name)

def read_tranco(filename):
    """
    Read tranco list from disk.
    """
    tranco = OrderedDict()
    count = 0
    with open(filename, 'r', encoding='utf-8') as inputfile:
        for line in inputfile:
            line = line.rstrip('\r\n')
            splitted = line.split(',', 1)
            rank = int(splitted[0])
            url = splitted[1]
            tranco[rank] = url
            count += 1
            if count >= 10000:
                break
    return tranco


def download_all_resources(driver):
    """
        Download all page sources
    """
    all_sources = driver.page_source
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    print(f"Identified {len(iframes)} iframes on {driver.current_url}")
    if len(iframes) > 0:
        for iframe in iframes:
            all_sources += driver.page_source
    all_sources = all_sources.lower()
    return all_sources


def wait_until_page_loaded(driver):
    """
        wait until the page is loaded, 
        or the max_waiting_time is exceeded.
    """
    WebDriverWait(driver, max_waiting_time).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print(f"Page {driver.current_url} has loaded")
    driver.maximize_window()


def get_buttons(driver):
    """
        get buttons in the page so as to move to next page
    """
    my_lists = []
    my_lists = driver.find_elements(By.TAG_NAME, 'button')
    x = []
    for i in my_lists:
        x.append(str(i.text))
    result = list(filter(None, x))
    buttons = []
    # cleaning the list
    for xx in result:
        xx = str(xx).replace('[',
                             '').replace(']',
                                         '').replace('\'',
                                                     '').replace('\"',
                                                                 '')
        buttons.append(xx.lstrip())
    return buttons



def check_legitimate(driver, name, count):
    """
        checks whether Legitimate interest is present in the source
    """
    
    wait_until_page_loaded(driver) 
    all_sources = download_all_resources(driver)
    page = False
    page = any(search_string in all_sources\
        for search_string in ['legitimate interest', 'legitimate interests'])
    if page:
        driver.get_screenshot_as_file(f"output_files/pics/{name}_{count}.png")     
    return page, all_sources
    

def crawl_website(url, name):
    """
        Visit website and check for LI
    """
    driver = init_driver()
    driver.get(url)
    print("\n**************************************\n")
    final_data = ""
    count = 1
    result_ = []
    page1, all_sources = check_legitimate(driver, name, count)
    result_.append(page1)
    final_data += all_sources

    button_list = []
    button_list = get_buttons(driver)
    for buttonn in button_list:
        if buttonn.lower() in cbanner_list:
            val = f'//button[normalize-space()="{buttonn}"]'
            link = driver.find_element(by=By.XPATH, value=val)
            link.click()
            count += 1
            page2, all_sources = check_legitimate(driver, name, count)
            result_.append(page2)
            button_list2 = get_buttons(driver)
            for xx in button_list2:
                if xx.lower() in ['legitimate interest',
                                  'legitimate interests']:
                    val = f'//button[normalize-space()="{buttonn}"]'
                    link = driver.find_element(by=By.XPATH, value=val)
                    link.click()
                    count += 1
                    wait_until_page_loaded(driver)
                    all_sources = download_all_resources(driver)
                    final_data += all_sources
                    banner_ss(driver, f"output_files/pics/{name}_{count}.png")

    purp = determine_purpose(final_data, name)
    
    is_found = any(result_)
    if is_found:
        check_soup(final_data, name)

    driver.quit()
    return result_, purp


def main():
    """
        Main Function
        Input: 
        Reads the tranco file
        Output: 
        CSV file 
        Rank
        Website URL
        Number of pages with legitimate interests
        Whether there are any legitimate interests on the website
        Number of clicks needed to find legitimate interests (if any)
        Error (if any)
        The code will also output a CSV file with the list of websites and their legitimate  purposes(in terms od True or False).
        
    """
    tranco = read_tranco('read_files/tranco_KKJW.csv')
    tranco = read_tranco('read_files/tranco.csv') 
    print("Welcome!!!!!")
    DF = pd.DataFrame()
    DFF = pd.DataFrame()
    for entry in tranco:
        result = []
        errorr = None
        purp = None
        try:
            clicks = 0
            errorr = False
            final_result = False
            result ,purp = crawl_website("http://" + tranco[entry], tranco[entry])
            print(f"Now opening: Rank {entry} -- URL: \
                {tranco[entry]} -- Legitimate Interest: {result}\n")
            final_result = any(result)
            if final_result:
                clicks = result.index(True) + 1
        except Exception as e:
            print(f"Error: There was a problem with the website:\
                Rank {entry} -- URL: {tranco[entry]}\n")
            print(e)
            errorr = True

        dictt = {
            "rank": entry,
            "website": tranco[entry],
            "pagesres": [result],
            "pages": len(result),
            "final_result": final_result,
            "clicks needed": clicks,
            "Error": errorr
        }
        li_datta = pd.DataFrame(dictt)
        # append the data to the list
        DF = DF.append(li_datta)
        
        DF.to_csv("output_files/Table_results.csv", index=False)
        print(DF)
        
        # purpose data as seperate file
        purpose_data = pd.DataFrame(purp, index=['website'])
        DFF = pd.concat([DFF, purpose_data], ignore_index=True)
        DFF.to_csv("output_files/Purposes.csv")


if __name__ == '__main__':
    main()
