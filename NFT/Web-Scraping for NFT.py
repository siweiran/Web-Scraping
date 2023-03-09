#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import requests 
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymongo
from pymongo import MongoClient
import http.client, urllib.parse
import json
import os
chromedriver = '/opt/homebrew/bin/chromedriver'


# In[ ]:


# navigate to the all apes with “Solid gold” fur and sort them “Price high to low”
def navigate_url():
    url = "https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold"
    driver = webdriver.Chrome(chromedriver)
    driver.implicitly_wait(1)
    driver.set_script_timeout(12000)
    driver.set_page_load_timeout(100000)
    driver.get(url)
    time.sleep(1)
navigate_url()
# click on the each of the top-8 most expensive Bored Apes and get url
click_list = []
url_list = []
ape_num_list =[]
def click_and_geturl():
    url = "https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold"
    driver = webdriver.Chrome()
    for i in range(1,9):
        try:
            click_list.append(f'''//*[@id="main"]/div/div/div/div[5]/div/div[7]/div[3]/div[2]/div/div[{i}]/article/a/div[1]/div/div/div/div/span/img''')
        except:
            print('something went wrong with click_list')
            continue
    for i in range(0,8):
        try:
            driver.get(url)
            expens_most = driver.find_element(By.XPATH,click_list[i])
            expens_most.click()
            time.sleep(5)
            url_list.append(driver.current_url)
            time.sleep(5)
        except:
            print("Maybe not enough sleep")
            continue
click_and_geturl()
# get the ape number 
def get_ape_num(urllist):
    for i in range(0,8):
        try:
            x = re.split("f13d/",urllist[i])
            ape_num_list.append(x[1])
        except:
            print('cannot get ape number')
            continue
get_ape_num(url_list)

# download page
def get_file(url, file_name):
    header = {'User-agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=header) 
    webcontent = response.content
    f = open(file_name,'wb') 
    f.write(webcontent) 
    f.close() 
    time.sleep(1)
def download_page(urllist,ape_num):
    for i in range(0,8):
        try:
            get_file(url_list[i], f"bayc_[{ape_num[i]}].htm")
            print(f"successful for downloading ape item {ape_num[i]} page：",f'item{i+1}')
        except:
            print(f"cannot download ape item {ape_num[i]} page")
            continue
download_page(url_list,ape_num_list)

# Get the data into dictionary
for n in range(0,8):
    try:
        with open(f"bayc_[{ape_num_list[n]}].htm") as f:
            soup = BeautifulSoup(f, 'lxml')
            attribute = soup.select_one('#Body\ assets-item-properties > div > div')
            for i in attribute:
                value_list = i.find_all('div',class_= 'Property--value')
            for i in attribute:
                rarity_list = i.find_all('div',class_= 'Property--rarity')
            for i in attribute:
                type_list = i.find_all('div',class_= 'Property--type')
            for i in range(0,len(type_list)):
                my_dict.append({"Ape name":ape_num_list[n],f"Attributes_{i}": {"Type" : type_list[i].text,
                "Value":value_list[i].text,"Rarity":rarity_list[i].text}})
    except:
        print("Cannot append data into dict")
        continue

# Connect to MongoDB
client = MongoClient()
client = MongoClient('localhost',27017)

# create database and insert data
try:
    project_db = client['bayc']
    collection = project_db['bayc']
    result = collection.insert_many(my_dict)
    print("Create bayc and insert data")
except:
    print("Database has been created and data has been inserted")

