from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from datetime import date
import boto3
import datetime

def get_latest_price_data(url,retry=5): 
    # Configure Selenium to use headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress warnings


    # Set up the Chrome WebDriver
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    top_row_xpath = '//*[@id="nimbus-app"]/section/section/section/article/div[2]/div[3]/table/tbody/tr[1]'
    for i in range(retry):
        
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            # Open the Yahoo Finance History Page
            driver.get(url)
            print(f"[Timestamp: {datetime.datetime.now()}]:Opened {url}")
            wait = WebDriverWait(driver, 10)
            # wait until the table is loaded
            try:
                wait.until(lambda driver: driver.find_element(By.XPATH, top_row_xpath))
                top_row = driver.find_element(By.XPATH, top_row_xpath)
            except:
                top_row_xpath="#nimbus-app > section > section > section > article > div.container > div.table-container.svelte-ewueuo > table > tbody > tr:nth-child(1)"
                wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, top_row_xpath))
                top_row = driver.find_element(By.CSS_SELECTOR, top_row_xpath)
            # Locate the topmost row using the full XPath
            
            
            data = [cell.text for cell in top_row.find_elements(By.TAG_NAME, 'td')]
            driver.quit()
            return data
        except Exception as e:
            #top_row_xpath = '/html/body/div[1]/main/section/section/section/article/div[2]/div[3]/table/tbody/tr[1]'
            if i < retry - 1:
                print(f"[Timestamp: {datetime.datetime.now()}]:Error: {e}. Retrying...")
                if driver:
                    driver.quit()
                time.sleep(2)
            else:
                raise e
            

# Get news URLs for a list of stocks, Doing it this way so that data can be extracted one stock at a time
if __name__ == "__main__":
    print(f"[Timestamp: {datetime.datetime.now()}]:Starting Yahoo Finance Data Webscrape")
    stock_list = ['META', 
                'AAPL', 
                'GOOG', 
                'AMZN', 
                'MSFT', 
                'NVDA', 
                'AMD']
    finance_data_array = []
    for stock in stock_list:
        url = f"https://finance.yahoo.com/quote/{stock}/history/"
        data_array = get_latest_price_data(url)
        data_array.insert(0,stock)
        print(f'[Timestamp: {datetime.datetime.now()}]:{data_array}')
        finance_data_array.append(data_array)
    
    finance_data_df = pd.DataFrame(finance_data_array, columns = ['Stock', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
    s3_client = boto3.client('s3')
    
    output_s3_bucket = 'webscrape-bucket-mle611'
    output_s3_key = f'webscrape_{str(date.today())}.csv'
    
    csv_file = '/tmp/output.csv'
    finance_data_df.to_csv(csv_file, index =False)
    
    # Upload the CSV file to S3 with the specified S3 path and filename
    s3_client.upload_file(csv_file, output_s3_bucket, output_s3_key)
    
    response_message = f"[Timestamp: {datetime.datetime.now()}]:CSV file successfully uploaded to s3://{output_s3_bucket}/{output_s3_key}"
    print(response_message)

    