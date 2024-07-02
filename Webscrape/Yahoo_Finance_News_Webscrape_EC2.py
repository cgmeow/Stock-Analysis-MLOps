from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import os
import boto3
import botocore
import sys


s3_client = boto3.client("s3")


def key_exists(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The key does not exist
            return False
        else:
            # Something else has gone wrong
            raise
    else:
        # The key does exist
        return True

def get_news_urls(url, retry=5, url_limit=10): 
    for i in range(retry):
        try:
            # Configure Selenium to use headless mode
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--log-level=3")  # Suppress warnings

            # Set up the Chrome WebDriver
            #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver = webdriver.Chrome(options=chrome_options)

            # Open the Yahoo Finance news page
            driver.get(url)
            
            # Scroll to the bottom of the page to load all content
            wait = WebDriverWait(driver, 10)
            # wait until the table is loaded
            wait.until(lambda driver: driver.find_element(By.XPATH, "//a[contains(@href, '/news/')]"))
            print(f"[Timestamp: {datetime.datetime.now()}]:Opened {url}")
            max_attempts = 5
            scroll_attempts = 0

            #print("Scrolling to the bottom of the page...")

            while True:
                driver.execute_script('window.scrollBy(0, 1000)')
                print(f"[Timestamp: {datetime.datetime.now()}]:Scroll Count({scroll_attempts})")
                time.sleep(2)  # Wait for the page to load
                scroll_attempts += 1
                if scroll_attempts >= max_attempts:
                    #print("Reached the bottom of the page")
                    break

            # Find all news article links
            articles = driver.find_elements(By.XPATH, "//a[contains(@href, '/news/')]")

            # Extract URLs and metadata
            news_urls = []
            for article in articles:
                url = article.get_attribute('href')
                if url not in news_urls:
                    news_urls.append(url)
                if len(news_urls) >= url_limit:
                    break
                    
            driver.quit()
            print(f"[Timestamp: {datetime.datetime.now()}]:URL Extraction Complete: {len(news_urls)} news articles found.")
            return news_urls
        
        except Exception as e:    
            if i < retry - 1:
                print(f"[Timestamp: {datetime.datetime.now()}]:Error: {e}. Retrying...")
                # If driver exists, quit the driver
                if 'driver' in locals():
                    driver.quit()
                time.sleep(2)
            else:
                raise e

def extract_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title
    title = soup.find('h1').get_text()

    # Extract the date and source
    date_tag = soup.find('time')
    date = date_tag['datetime'] if date_tag else 'No date available'
    source = soup.find('div', class_='caas-attr-meta').get_text() if soup.find('div', class_='caas-attr-meta') else 'No source available'

    # Extract the content paragraphs
    paragraphs = soup.find_all('p')
    content = ' '.join([p.get_text() for p in paragraphs[:10]])

    return title, date, source, content


if __name__ == "__main__":
    print(f"[Timestamp: {datetime.datetime.now()}]:News Data Extraction Start.")
    s3_client = boto3.client("s3")
    date_run = str(date.today())

    df_news = pd.DataFrame()
    bucket_name = 'webscrape-bucket-mle611'

    # Get news URLs for a list of stocks, Doing it this way so that data can be extracted one stock at a time
    if len(sys.argv) == 1 or sys.argv[1] == 'all':
        stock_list = ['META', 
                    'AAPL', 
                    'GOOG', 
                    'AMZN', 
                    'MSFT', 
                    'NVDA', 
                    'AMD'] 
    else:
        stock_list = sys.argv[1].split(',')
    retry = 5
    for i in range(retry):
        try:
            
            for stock in stock_list:
                news_urls = []
                key = f'news_data_{stock}_{date_run}.csv'
                if key_exists(bucket_name, key):
                    print(f"[Timestamp: {datetime.datetime.now()}]:Data exist for {stock} on {date_run}")
                    continue
                else:
                    news_urls = get_news_urls(f'https://sg.finance.yahoo.com/quote/{stock}/news')

                # Extract content from each news article
                for url in news_urls:
                    print(f"[Timestamp: {datetime.datetime.now()}]:Scraping {url}...")
                    title, article_date, source, content = extract_article_content(url)
                    print(f"[Timestamp: {datetime.datetime.now()}]:Complete Scraping {url}...")
                    row_data = {'Title': title, 'Date': article_date, 'Source': source, 'Content': content, 'URL': url, 'Stock': stock}
                    df_news = pd.concat([df_news, pd.DataFrame([row_data])])

                df_news.reset_index(drop=True, inplace=True)
                
                s3_client = boto3.client('s3')

                csv_file = '/tmp/output.csv'
                df_news.to_csv(csv_file, index =False)

                #Upload the CSV file to S3 with the specified S3 path and filename
                s3_client.upload_file(csv_file, bucket_name, key)
                response_message = f"[Timestamp: {datetime.datetime.now()}]:CSV file successfully uploaded to s3://{bucket_name}/{key}"
                print(response_message)

            if stock == stock_list[-1]:
                break
        except Exception as e:
            if i < retry - 1:
                print(f"Error: {e}. Retrying...")
                time.sleep(2)
            else:
                raise e
    
    print(f"[Timestamp: {datetime.datetime.now()}]:News Data Extraction Complete.")