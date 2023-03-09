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


url = "https://www.yellowpages.com/search"
headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
session_requests = requests.session()
# navigate to the Yellow page
response = session_requests.get(url,headers = headers)

# seach for "Pizzeria" in San Francisco by get request
session_requests = requests.session()
payload = {
        'search_terms':'Pizzeria',
        'geo_location_terms': 'San Francisco, CA'
}
search_response = session_requests.get(url,headers = headers, params=payload)

# save search result page 
webcontent = search_response.content
f = open('sf_pizzeria_search_page.htm', 'wb')
f.write(webcontent)
f.close()
time.sleep(1)
print("Download Successfully!")

info_results = []
name_list = []
rank_list = []
rank_name_list =[]
link_url_list =[]
ta_list = []
ta_rating_list =[]
ta_count_list = []
star_list = []
review_list = []
money_list = []
year_list =[]
per_rev_list =[]
amenity_list =[]

with open('sf_pizzeria_search_page.htm') as f:
    soup = BeautifulSoup(f, 'lxml')

    # Name and rank list
    rank_name = soup.find_all('h2',class_= 'n')
    for i in rank_name:
        x = re.search("^[0-9].*", i.text)
        if x != None:
            rank_name_list.append(x.group())
    for i in range(0,len(rank_name_list)):
        name = re.split(". ",rank_name_list[i],maxsplit = 1)[1]
        name_list.append(name)
        rank = re.split(". ",rank_name_list[i],maxsplit = 1)[0]
        rank_list.append(rank)

    info_results = soup.find_all('div',{'class':'info'})
    #print(info_results[2])
    for restaurant in info_results[1:31]: # remove Ad here
        try:
            # link url list
            link = restaurant.find('a',{'class' : 'business-name'})
            if link != None:
                link = "https://www.yellowpages.com" + link.get('href')
            link_url_list.append(link)

            # Star rating
            star = restaurant.find('div',{'class':'ratings'}).find('div')
            if star != None:
                star = "Rating: "+ star.get('class')[1]+ ' star'
            star_list.append(star)

            # Number of review
            review = restaurant.find('span',{'class':'count'})
            if review != None:
                review = review.text
            review_list.append(review)

            # TripAdvisor list and num of ta
            TA = restaurant.find('div',{'class':'ratings'}).get('data-tripadvisor')
            ta_list.append(TA)

            # $ sign
            money = restaurant.find('div',{'class':'price-range'})
            if money != None:
                money = money.text
            money_list.append(money)

            # years in business
            year =  restaurant.find('div',{'class':'number'})
            if year != None:
                year = year.text
            year_list.append(year)

            # review by person
            person_review = restaurant.find('p',{'class':'body with-avatar'})
            if person_review != None:
                person_review = person_review.text
            per_rev_list.append(person_review)

            # Amenities
            amenity = restaurant.find('div',{'class':'amenities-info'})
            amenity_per_res = []
            if amenity != None:
                amenity = amenity.find_all('span')
                for a in amenity:
                    amenity_per_res.append(a.text)
                amenity_list.append(amenity_per_res)
            else:
                amenity_list.append(amenity)
        except:
            print("Something went wrong here")
            continue

# split TA rating and Num of TA
for n in range(0,30):
    try:
        if ta_list[n] != None:
            ta_rating_list.append(ta_list[n].split(',')[0].split('{')[1])
        else:
            ta_rating_list.append(ta_list[n])
    except:
        print("something went wrong here")
        continue

for n in range(0,30):
    try:
        if ta_list[n] != None:
            ta_count_list.append(ta_list[n].split(',')[1].split('}')[0])
        else:
            ta_count_list.append(ta_list[n])
    except:
        print("something went wrong here")
        continue

# Create database in MongoDB
client = MongoClient()
client = MongoClient('localhost',27017)
try:
    project_db = client['sf_restaurant']
    collection = project_db['sf_pizzerias']
    print("Create database and sf_pizzerias collection")
except:
    print("Database and collection have been created")

sf_res = []
for i in range(0,30):
    try:
        sf_res.append({"Name":name_list[i],"Rank":rank_list[i],
              'Link':link_url_list[i],"Star Rating":star_list[i],
              'Number of Reviews':review_list[i],'TripAdvisor Rating': ta_rating_list[i],
               'TripAdvisor Counts': ta_count_list[i],
              '$ Sign':money_list[i],'years in business':year_list[i],
              "Person's review" : per_rev_list[i], 'Amenity':amenity_list[i]})
    except:
        print("something went wrong here")
        continue
try:
    result = collection.insert_many(sf_res)
    print("Insert data into Collection")

except:
    print("Data has been Inserted")
    
client = MongoClient()
client = MongoClient('localhost',27017)
project_db = client['sf_restaurant']
collection = project_db['sf_pizzerias']

# query the column from my MongoDB
sf_rank = collection.find({},{"Rank":1})
rank_db_list =[]
for i in sf_rank:
    rank_db_list.append(i['Rank'])

sf_link = collection.find({},{"Link":1})
link_db_list =[]
for i in sf_link:
    link_db_list.append(i['Link'])

rank_db_list
# Download each shop page
for i in range(0,30):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(link_db_list[i],headers = headers) 
        soup = BeautifulSoup(response.text, "lxml")
        webcontent = response.content
        with open(f'sf_pizzerias_[{rank_db_list[i]}].htm','wb') as f:
            f.write(webcontent)
            f.close()
            print(f"Download restaurant rank {rank_db_list[i]} Successfully!")
    except:
        print(f"cannot download restaurant rank {rank_db_list[i]}")
        continue

address_list = []
phone_num_list = []
website_list = []
for i in range(1,31):
    try:
        with open(f'sf_pizzerias_[{i}].htm') as f:
            soup = BeautifulSoup(f, 'lxml')
            # Address
            address = soup.find('span',{'class':'address'})
            if address != None:
                address = address.text
            address_list.append(address)
            # Phone Number
            phone_num = soup.find('a',{'class':'phone dockable'})
            if phone_num != None:
                phone_num = phone_num.get('href')
            phone_num_list.append(phone_num)
            # website
            website = soup.find('a',{'class':'website-link dockable'})
            if website != None:
                website = website.get('href')
            website_list.append(website)
    except:
        print("Something went wrong here")
        continue
new_address_list = []
for i in range(0,30):
    try:
        x = address_list[i].split("San")
        new_address_list.append(x[0] + ", San" + x[1])
    except:
        new_address_list.append(None)
        continue
        
geolocation_list = []
for i in range(0,30):
    try:
        conn = http.client.HTTPConnection('api.positionstack.com')
        access_key = 'e98946814192886582f27b699fe9f72f'
        params = urllib.parse.urlencode({
            'access_key': access_key,
            'query': new_address_list[i],
            'limit': 1,
            })
        conn.request('GET', '/v1/forward?{}'.format(params))
        res = conn.getresponse()
        data = res.read()
        data_dic = json.loads(data.decode('utf-8'))
        if data_dic['data'][0]['latitude'] != None:
            latitude = data_dic['data'][0]['latitude']
        if data_dic['data'][0]['longitude'] != None:
            longitude = data_dic['data'][0]['longitude']
        geolocation_list.append({'latitude':latitude,'longitude':longitude})
    except:
        geolocation_list.append(None)
        continue

# Connect to MongoDB
    client = MongoClient()
    client = MongoClient('localhost',27017)
    project_db = client['sf_restaurant']
    collection = project_db['sf_pizzerias']

# Update new data into MongoDB
new_data = []
for i in range(0,30):
    try:
        new_data.append({"Address": address_list[i],"Phone Number" : phone_num_list[i],
                   "Website" : website_list[i] , 'Geolocation':geolocation_list[i]})
    except:
        print("Something went wrong here")
        continue

# query name from MongoDB
name = collection.find({},{"Name":1})
name_list =[]
for i in name:
    name_list.append(i['Name'])

# Insert new data into MongoDB
for i in range(0,30):
    collection.update_many({"Name":name_list[i]},{"$set":new_data[i]})
print("New Data has been inserted")

