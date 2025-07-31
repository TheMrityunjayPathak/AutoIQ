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

def get_car_details(soup):
    """
    Extract car details from a BeautifulSoup object containing HTML content of a car listing page.

    Parameters:
        soup (BeautifulSoup): Parsed HTML content of a webpage.

    Returns:
        pd.DataFrame: A DataFrame containing the following columns ↓
            model_name: Car model name.
            km_driven: Kilometers driven for each car.
            fuel_type: Fuel type of each car (e.g., Petrol, Diesel, CNG).
            transmission: Transmission type (Manual or Automatic).
            owner: Ownership status (e.g., First Owner, Second Owner).
            price: Listed price of each car.
            link: URL link to the individual car listing.
    """
    model_name = []
    for i in soup.find_all('span', 'sc-braxZu kjFjan'):
        model_name.append(i.text)

    clean_model_name = []
    for i in model_name:
        if i.startswith('2'):
            clean_model_name.append(i)

    specs = []
    for i in soup.find_all('p', 'sc-braxZu kvfdZL'):
        specs.append(i.text)

    clean_specs = []
    for i in range(0,len(specs),5):
        clean_specs.append(specs[i:i+5])

    km_driven = []
    for i in clean_specs:
        km_driven.append(i[0])

    fuel_type = []
    for i in clean_specs:
        fuel_type.append(i[1])

    transmission = []
    for i in clean_specs:
        transmission.append(i[2])

    owner = []
    for i in clean_specs:
        owner.append(i[3])
            
    price = []
    for i in soup.find_all('p', 'sc-braxZu cyPhJl'):
        price.append(i.text)

    price = price[2:]

    link = []
    for i in soup.find_all('a', 'styles_carCardWrapper__sXLIp'):
        link.append(i['href'])

    df = pd.DataFrame({'model_name':clean_model_name,'km_driven':km_driven,'fuel_type':fuel_type,
                       'transmission':transmission,'owner':owner,'price':price,'link':link})
    return df

def get_engine_capacity(urls):
    """
    Extract engine capacity values from a list of car listing page URLs.

    Parameters:
        urls (list of str): List of URLs pointing to individual car listings.

    Returns:
        list: A list containing engine capacity values (str) for each URL.
              Returns None for entries where engine capacity is not found.
    """
    engine_capacity = []
    for url in urls:
        headers = {"User-Agent":"Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=random.randint(4,8))
        soup = BeautifulSoup(response.text,"lxml")

        found = False
        for i in soup.find_all('p', attrs={"class":"sc-braxZu jjIUAi"}):
            if i.text.strip() == 'Engine capacity':
                engine_capacity.append(i.find_next_sibling().text)
                found = True
                
        if not found:
            engine_capacity.append(None)
    return engine_capacity