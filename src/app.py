################ all imports ################
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import sqlite3

############################# web scrapping #########################

#storing URL
tesla_url='https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue'

#Creating request
time.sleep(20) #20 sec delay before making the request to not overload server
try:
    response=requests.get(tesla_url)
    response.raise_for_status()
    tesla_raw=BeautifulSoup(response.text, 'html')

#handles errors specific to the request 
except requests.exceptions.RequestException as e:
    print(f"Request Exception: {e}") #prints the error
    header={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response=requests.get(tesla_url, headers=header)
    tesla_raw=BeautifulSoup(response.text, 'html.parser')

# Prints other exceptions that may occur during parsing or processing
except Exception as e:
    print(f"Other Exception: {e}")

########################### findind tables & Storing data as data frame ####################

#finding all tables about Tesla's financial performance
all_tables = tesla_raw.find_all("table")

#finding quarterly evolution table of Tesla's revenue
for table in all_tables:
    if 'Tesla Quarterly Revenue' in table.get_text():
        tesla_data=table
        break #stops the code once it finds the table

#storing result as dataframe
tesla_qrev=pd.read_html(str(tesla_data))[0]
tesla_qrev.columns=['quarter', 'revenue'] #renames columns
tesla_qrev['quarter']=pd.to_datetime(tesla_qrev['quarter']) #sets date format
tesla_qrev['revenue']=tesla_qrev['revenue'].str.replace('[\$,]','', regex=True).astype(float) #removes $ and ,

print(tesla_qrev)

####################### exploratory analysis of Tesla's quarterly revenue ###################################

#Line plot of revenue
plt.plot(tesla_qrev['quarter'],tesla_qrev['revenue'], "blue")
plt.xlabel("Quarters")
plt.ylabel('Revenue ($)')
plt.title("Tesla quartertly revenue from 2009 to 2023")
plt.tick_params(axis='x') 
plt.show()

#histogram of revenue
plt.hist(tesla_qrev['revenue'], color="blue")
plt.ylabel('Revenue ($)')
plt.ylabel("Frequency")
plt.title("Histogram - Tesla quartertly revenue from 2009 to 2023")
plt.show()

#Area chart of revenue
plt.fill_between(tesla_qrev['quarter'],tesla_qrev['revenue'], color='skyblue', alpha=0.5)
plt.plot(tesla_qrev['quarter'],tesla_qrev['revenue'], marker='o', linestyle='-', color='b', label='Revenue')
plt.xlabel('Quarters')
plt.ylabel('Revenue ($)')
plt.title("Tesla's Quarterly Revenue Trend (Area Chart)")
plt.show()


#####################Creating SQL data base ##############################

con = sqlite3.connect("tesla_qrev.db")
cursor=con.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS TESLA
    (quarter        DATE    NOT NULL,
     revenue         FLOAT)""")

tesla_qrev.to_sql('TESLA', con, index=False, if_exists='replace') #converting DF to SQL

#Checking the table was created properly
for row in cursor.execute("SELECT * FROM TESLA"):
    print(row)

con.commit()
con.close()
