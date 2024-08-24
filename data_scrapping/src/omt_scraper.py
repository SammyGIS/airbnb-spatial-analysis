"""
************************************************
SCRAPE PROPERTY LISTED FOR SALES AND RENT IN LONDON FROM ON THE MARKET WEBSITE
************************************************
Date: May-20-2023
@Author: Ajeyomi Adedoyin -> adedoyinsamuel25@gmail.com

"""
import re
import time
from datetime import date, timedelta
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import pandas as pd
from selenium.webdriver.common.by import By

from utils.utils import get_driver, merge_save

om_renturl  = 'https://www.onthemarket.com/to-rent/property/london/?page={}&view=grid'
om_salesurl  = 'https://www.onthemarket.com/for-sale/property/london/?page={}&view=grid'


def get_pages(driver,page,url):
    """
    Retrieves the content of a web page using the provided Selenium WebDriver.

    Parameters:
        - driver (WebDriver): The Selenium WebDriver instance used to access the web page.
        - page (str): The name or identifier of the page being retrieved.
        - url (str): The URL of the web page to be retrieved.

    Returns:
        The HTML content of the web page.
    
    """
    driver.get(url.format(page))
    OM_DIV_TAG = 'otm-PropertyCard '
    page_html = driver.find_elements(By.CLASS_NAME, OM_DIV_TAG)
    return page_html

def extract_data(page_html:'page_html', transaction_type:str, source:str):
    """
    Parses the given HTML content of a web page and extracts relevant information based on the provided transaction type and source.

    Parameters:
        - page_html (html elements): The HTML content of the web page to be parsed.
        - transaction_type (str): The type of transaction for which information needs to be extracted.
        - source (str): The source of the web page content.

    Returns:
        dataframe containing the data sccrapped from the website
        
    """
    page_data = []

    for page in page_html:
        # Transaction

        try:
            if transaction_type == 'rent':
                transaction = transaction_type

            elif transaction_type == 'sales':
                transaction = transaction_type

            else:
                print('transaction_type can either be sales or rent')
                break

        except:
                print('transaction_type can either be sales or rent')
                break
        
        # Address
        try:
            address_tag = page.find_element(By.CLASS_NAME, 'address')
            address = address_tag.text 

        except:
            address = None

        # Bedroom
        try:         
            
            bedroom_element = page.find_element(By.CLASS_NAME,"otm-BedBathCount")
            bedroom = int(bedroom_element.text.split("\n")[0].strip())

        except:
            bedroom = None
        # Bathroom
        try:
            
            bathroom_tag = page.find_element(By.CLASS_NAME,"otm-BedBathCount")
            bathroom = bathroom_tag.text.split("\n")[1].strip()

        except:
            bathroom =None
        # Description
        try:
            description_tag = page.find_element(By.CLASS_NAME, 'title')
            description = description_tag.text.split("\n")[0].strip()

        except:
            description = None


        # property Type
        try:
            property_type_tag =page.find_element(By.CLASS_NAME, 'title')
            property_desc = property_type_tag.text.split("\n")[0].strip()
            
            match_semi = re.search(r'\bsemi-detached\b', property_desc)
            match_flat = re.search(r'\bflat\b', property_desc)
            match_apartment = re.search(r'\bapartment\b', property_desc)
            match_studio = re.search(r'\bStudio\b', property_desc)
            match_terraced = re.search(r'\bterraced\b', property_desc)
            match_penthouse = re.search(r'\bpenthouse\b', property_desc)
            match_duplex = re.search(r'\bduplex\b', property_desc)
            match_house = re.search(r'\bhouse\b', property_desc)
            match_detached = re.search(r'\bdetached\b', property_desc)
            match_maisonette = re.search(r'\bmaisonette\b', property_desc)
        
            if match_semi is not None:
                property_type = match_semi.group(0).capitalize()

            elif match_flat is not None:
                property_type = match_flat.group(0).capitalize()

            elif match_apartment is not None:
                property_type = match_apartment.group(0).capitalize()

            elif match_studio is not None:
                property_type = match_studio.group(0).capitalize()

            elif match_terraced is not None:
                property_type = match_terraced.group(0).capitalize()

            elif match_penthouse is not None:
                property_type = match_penthouse.group(0).capitalize()

            elif match_duplex is not None:
                property_type = match_duplex.group(0).capitalize()
            
            elif match_detached is not None:
                property_type = match_detached.group(0).capitalize()

            elif match_house is not None:
                property_type = match_house.group(0).capitalize()

            elif match_maisonette is not None:
                property_type = match_maisonette.group(0).capitalize()

            else:
                property_type = None

        except:
            property_type = None


            # price

        # rent payment
        if transaction_type == 'rent':

            sales_price = None
            
            # rent price per month
            try:
                price_tag= page.find_element(By.CLASS_NAME, 'otm-Price')
                price = price_tag.text.split("\n")[-1].strip()
                per_month = int(price.split("pcm")[0].strip().split("£")[1].split(" ")[0].replace(",", ""))
                
            except:
                per_month = None
                
            # rent price per week
            try:
                price_tag= page.find_element(By.CLASS_NAME, 'otm-Price')
                price = price_tag.text.split("\n")[-1].strip()
                per_week = int(price.split("pcm")[-1].strip().split("£")[1].split(" ")[0].replace(",", ""))

            except:
                per_week = None               

        else:
            # sales Price
            try:
                per_week = None  
                per_month = None
                
                price_tag = page.find_element(By.CLASS_NAME, 'otm-Price')
                sales_price = int(price_tag.text.split("\n")[-1].strip().split("£")[1].split(" ")[0].replace(",", ""))
                
            except:
                sales_price = None           
        # Location
        try:
            location_tag = page.find_element(By.CLASS_NAME, 'address')
            location = location_tag.text.split(" ")[-1].strip()
        
        except:
            location =None

        # Agent
        try: 
            agent_tag = page.find_element(By.CLASS_NAME, 'agent-logo')
            agent_tag = agent_tag.find_element(By.TAG_NAME, 'img')            
            agent = agent_tag.get_attribute('alt')
            
        except:
            agent = None


        #Listing Source
        listing_source = source
        # Listing URL

        try:
            
            listing_url_tag =page.find_element(By.CLASS_NAME, 'agent-logo')
            listing_url_tag =listing_url_tag.find_element(By.TAG_NAME, 'a')
            listing_url = listing_url_tag.get_attribute('href')

        except:
            listing_url = None

        # Date Added
        try:
            date_added_tag = page.find_element(By.CLASS_NAME, 'days-otm')
            date_string = date_added_tag.text.split("OnTheMarket")[-1].strip()
            date_string2 = date_added_tag.text.split("Reduced")[-1].strip()

            if date_string == "today":
                date_added = date.today()

            elif date_string == "yesterday":
                date_added = date.today() - timedelta(1)
            
            elif date_string2 == "today":
                    date_added = date.today()

            elif date_string2 == "yesterday":
                date_added = date.today() - timedelta(1)

            else:
                date_added = date_string 
       
        except:
            date_added = None
            
            
        page_data.append({
            'transaction': transaction,
            'address': address,
            'bedroom': bedroom,
            'bathroom': bathroom,
            'sales_price': sales_price,
            'rent_perMonth': per_month,
            'rent_perWeek': per_week,
            'description': description,
            'propertyType': property_type,
            'location':location,
            'agent':agent,
            'listing_source':listing_source,
            'listing_url':listing_url,
            'listed_date': date_added ,
            })

    return page_data


def get_data(url,transaction_type,source,start_page, end_page):
    
    """
    Retrieves data from a specific range of pages on a website based on the provided parameters.

    Parameters:
        - url (str): The URL of the website.
        - transaction_type (str): The type of transaction for which data needs to be retrieved.
        - source (str): The source of the data.
        - start_page (int): The starting index of the pages to retrieve.
        - end_page (int): The ending index of the pages to retrieve (inclusive).

    Returns:
        dataframe: Data retrieved from the specified pages.

    """
    browser = get_driver()
    all_data = []
    
    print('runing.....................................')

    for page in range(start_page, end_page+1):
        time.sleep(1)
        page_html = get_pages(browser,page,url)
        time.sleep(1)

        data_extracted = extract_data(page_html,transaction_type, source)
        time.sleep(1)

        all_data.extend(data_extracted)
        time.sleep(1)
    
    browser.quit()

    data = pd.DataFrame(all_data)
    return data


if __name__ == "__main__":
    # Specify the start and end page numbers for scraping
    start_page = 1
    end_page = 40

    # Call the get_data function to scrape the data
    rent_data = get_data(om_renturl,'rent','omt',start_page, end_page)
    sales_data = get_data(om_salesurl,'sales','omt',start_page, end_page)

    #merge and save data as csv
    merge_save(rent_data,sales_data)

    # save scrapped data to csv
    print('data scraped successfully')    