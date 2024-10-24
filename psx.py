# from psx import stocks, tickers
# import datetime

# # tickers = tickers()

# # data = stocks("SILK", start=datetime.date(2020, 1, 1), end=datetime.date.today())

# print(data)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import pandas as pd

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


if tbody:
    with open("formatted_output.html", "w", encoding="utf-8") as file:
        file.write(tbody.prettify())

# Print or save the tbody content
print(tbody.prettify())

# Close the WebDriver
driver.quit()

