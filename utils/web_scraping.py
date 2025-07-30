import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_car_listing(link):
    """
    Launches an automated Chrome browser session to scrape the content of a dynamically loaded car listing page.

    Parameters:
        link (str): URL of the car listing page to scrape.

    Returns:
        BeautifulSoup: Parsed HTML content of the fully loaded page.

    Raises:
        Exception: Catches any general exceptions that may occur.
    """
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(link)
        
        scroll_pause_time = random.uniform(2, 4)
        scroll_increment = 1000
    
        last_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
    
        while True:
            driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(scroll_pause_time)
    
            new_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
            total_page_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height >= total_page_height or new_height == last_height:
                break
            last_height = new_height
    
        html = driver.page_source
    
        driver.quit()
    
        soup = BeautifulSoup(html, 'lxml')
    
        return soup
    
    except Exception as e:
        print(f"[General Error] {e}")
    finally:
        if driver:
            driver.quit()