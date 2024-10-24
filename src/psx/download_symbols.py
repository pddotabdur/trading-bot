
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import pandas as pd

def download_symbols():

    driver = webdriver.Chrome()  
    driver.get('https://dps.psx.com.pk/')

    index_dropdown = Select(driver.find_element(By.NAME, 'index'))
    index_dropdown.select_by_value('KMIALLSHR')

    entries_dropdown = Select(driver.find_element(By.NAME, 'DataTables_Table_0_length'))
    entries_dropdown.select_by_value('-1')

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('table', id='DataTables_Table_0')

    tbody = table.find('tbody')
    table = tbody.find_parent('table')

    with open("extracted_table.html", "w") as file:
        file.write(str(table.prettify()))

    table_html = str(table)

    df = pd.read_html(table_html)[0]

    # Save the DataFrame as a CSV file
    df.to_csv("extracted_table.csv", index=False)


    # Close the WebDriver
    driver.quit()

    return df

