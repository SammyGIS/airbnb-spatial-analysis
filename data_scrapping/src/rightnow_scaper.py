"""
************************************************
SCRAPE PROPERTY LISTED FOR SALES AND RENT IN LONDON FROM RIGHTNOW WEBSITE
************************************************
Date: May-20-2023
@Author: Ajeyomi Adedoyin -> adedoyinsamuel25@gmail.com

"""

import datetime
from datetime import timedelta
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from selenium.webdriver.common.by import By

from utils.utils import get_driver, merge_save
rm_salesurl = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&index={}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="
rm_renturl = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E87490&index={}&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords="

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
    print(driver)
    OM_DIV_TAG = 'propertyCard-wrapper'
    page_html = driver.find_elements(By.CLASS_NAME, OM_DIV_TAG)
    print(page_html)
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
            address_tag = page.find_element(By.CLASS_NAME, "propertyCard-address")
            address = address_tag.text
        except:
            address = None

        # Bedroom
        try:         
            bedroom_element = page.find_element(By.CLASS_NAME,"propertyCard-content")
            bedroom_span = bedroom_element.find_element(By.CLASS_NAME, "bed-icon")
            inner_html = bedroom_span.get_attribute('innerHTML')

            # use string formatting
            title_start = "<title>"
            title_end = "</title>"
            title_index_start = inner_html.index(title_start) + len(title_start)
            title_index_end = inner_html.index(title_end)
            bedroom = inner_html[title_index_start:title_index_end][0:1]    

            #.text.split("\n")[-1].strip()
            # bedroom = bedroom_span.get_attribute('innerHTML')
            # print(bedroom)
            # # print(bedroom_span.get_attribute('title')        
        
        except:
            bedroom = None
     
       
        
        # Bathroom
        try:
            
            bathroom_tag =page.find_element(By.CLASS_NAME,"propertyCard-content")
            bathroom_span = bathroom_tag.find_element(By.CLASS_NAME, "bathroom-icon")
            inner_html2 = bathroom_span.get_attribute('innerHTML')

            # use string formatting
            title_start = "<title>"
            title_end = "</title>"
            title_index_start = inner_html2.index(title_start) + len(title_start)
            title_index_end = inner_html2.index(title_end)
            bathroom = inner_html2[title_index_start:title_index_end][0:1]    

        except:
            bathroom =None


        # Description
        try:
            description_tag = page.find_element(By.CLASS_NAME, 'propertyCard-description')
            description = description_tag.text

        except:
            description = None


        # property Type
        try:
            property_type_tag =page.find_element(By.CLASS_NAME, 'property-information')
            property_type =property_type_tag.text.split("\n")[0].strip()

        except:
            property_type = None

  
        # rent payment
        if transaction_type == 'rent':

            sales_price = None
            
            # rent price per month
            try:
                pcm = page.find_element(By.CLASS_NAME, 'propertyCard-priceValue')
                per_month = int(pcm.text.split(" ")[0].strip().split("£")[1].split(" ")[0].replace(',', ''))
                
            except:
                per_month = None
                
            # rent price per week
            try:
                pw = page.find_element(By.CLASS_NAME, 'propertyCard-secondaryPriceValue')
                per_week = int(pw.text.split(" ")[0].strip().split("£")[1].split(" ")[0].replace(",", ""))

            except:
                per_week = None               

        else:
            # sales Price
            try:
                per_week = None  
                per_month = None
                
                price_tag = page.find_element(By.CLASS_NAME, 'propertyCard-priceValue')
                sales_price = int(price_tag.text.split(" ")[0].strip().split("£")[1].split(" ")[0].replace(',', ''))
                
            except:
                sales_price = None     

        # Location
        try:
            location_tag = page.find_element(By.CLASS_NAME, 'propertyCard-address')
            location = location_tag.text.split(" ")[-1].strip()
            
        
        except:
            location =None
    

        # Agent
        try: 
            agent_tag =page.find_element(By.CLASS_NAME, 'propertyCard-branchSummary')
            # print(agent_tag.get_attribute('innerHTML'))
            agent = agent_tag.text.split("by")[-1].strip()

        except:
            agent = None

        #Listing Source
        listing_source = source

        # Listing URL
        try:
            listing_url_tag =page.find_element(By.CLASS_NAME, 'propertyCard-link')
            listing_url = listing_url_tag.get_attribute('href')

        except:
            listing_url = None
        

        
        # Date Added
        try:
            date_tag = page.find_element(By.CLASS_NAME, 'propertyCard-branchSummary-addedOrReduced')
            # print(date_tag.get_attribute('innerHTML'))
            added_reduced = date_tag.text
            date_type = date_tag.text.split(" ")[0].strip()

            # date
            if added_reduced == 'Added today':
                date = datetime.date.today()
                
            elif added_reduced== 'Added yesterday':
                date = datetime.date.today() - timedelta(days=1)

            elif added_reduced== 'Reduced today':
                date = datetime.date.today()

            elif added_reduced== 'Reduced yesterday':
                date = datetime.date.today() - timedelta(days=1)

            else:
                date = date_tag.text.split()[-1].strip()
        except:
            date = None
            date_type = None      


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
            # 'date_type':date_type,
            'listed_date':date,
            })

    return page_data


def get_data(url,transaction_type,source,start_index, stop_index,increment):

    """
    Retrieves data from a specific range of pages on a website based on the provided parameters.

    Parameters:
        - url (str): The URL of the website.
        - transaction_type (str): The type of transaction for which data needs to be retrieved.
        - source (str): The source of the data.
        - start_index (int): The starting index of the pages to retrieve.
        - stop_index (int): The ending index of the pages to retrieve (inclusive).
        - increment (int): The increment between page indices.

    Returns:
        dataframe: Data retrieved from the specified pages.

    """

    browser = get_driver()
    all_pages_data = []
    print('runing.....................................')

    for page in range(start_index, stop_index,increment):
        
        page_html = get_pages(browser,page,url)
        pages_data = extract_data(page_html,transaction_type,source)
        all_pages_data.extend(pages_data)

    browser.quit()

    data = pd.DataFrame(all_pages_data)
    return data


if __name__ == "__main__":
    # Specify the start and end page numbers for scraping
    start_index = 0
    stop_index = 1100
    increment = 24  
    
    # Call the get_data function to scrape the data
    rent_data = get_data(rm_renturl,'rent','rightmove',start_index, stop_index,increment)
    sales_data = get_data(rm_salesurl,'sales','rightmove',start_index, stop_index,increment)

    #merge and save data as csv
    merge_save(rent_data,sales_data)

    # save scrapped data to csv
    print('data scraped successfully')    

