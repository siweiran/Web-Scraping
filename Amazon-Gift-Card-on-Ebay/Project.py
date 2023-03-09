#!/usr/bin/env python
# coding: utf-8

# In[412]:


from bs4 import BeautifulSoup
import requests 
import time
import re


# ### Question 1.2(a)

# In[434]:


def download_01():
    url= 'https://www.ebay.com/sch/i.html?_nkw=amazon+gift+card&LH_Sold=1'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url,headers = headers) 
    soup = BeautifulSoup(response.text, "lxml")
    webcontent = response.content
    f = open('amazon_gift_card_01.htm', 'wb')
    f.write(webcontent)
    f.close()
    time.sleep(10)
    print("Download Successfully!")

download_01()


# ### Question 1.2(b)

# In[435]:


def get_url(url,i):
    page_url = 'https://www.ebay.com/sch/i.html?_nkw=amazon+gift+card&LH_Sold=1' + f'&_pgn={i}'
    return(page_url)

def get_file(url, file_name):
    header = {'User-agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=header) 
    webcontent = response.content
    f = open(file_name,'wb') 
    f.write(webcontent) 
    f.close() 
    time.sleep(10)
    
def download_page(url,x):
    for i in range(1,x+1):
        page_url = (get_url(x,i))
        get_file(page_url, f"amazon_gift_card_{str(i).zfill(2)}.htm")
        print("successful for downloading gift page：",f'page {i}')

download_page('https://www.ebay.com/sch/i.html?_nkw=amazon+gift+card&LH_Sold=1',10)


# ### Question 1.2(c)

# In[436]:


def parse():
    for i in range(1,11):
        with open(f"amazon_gift_card_{str(i).zfill(2)}.htm") as f:
            soup = BeautifulSoup(f, 'lxml')


# ### Question 1.2(d)

# In[437]:


list_title = []
list_price = []
list_shipping = []
shipping = ""
for i in range(1,11):
    with open(f"amazon_gift_card_{str(i).zfill(2)}.htm") as f:
        soup = BeautifulSoup(f, 'lxml')
        # Find all values
        content = soup.find_all('li',attrs = {'class' :'s-item'})
        for p in content[1:]:
            title_all = p.find_all('div',class_= 's-item__title')
            for t in title_all:
                title = t.find('span').text
                title = title.replace("New Listing"," ")
                list_title.append(title)
            price_all = p.find_all('span',attrs = {'class' : 's-item__price'})
            for pri in price_all:
                price = pri.text
                list_price.append(price)
            shipping_all = p.find_all('span',attrs = {'class': 's-item__shipping s-item__logisticsCost'})
            for s in shipping_all:
                if len(s) == 0:
                    shipping = "Free shipping"
                else: 
                    shipping = s.text
            list_shipping.append(shipping)
print(list_title,'|',list_price,'|',list_shipping)


# ### Question 1.2(e)

# In[438]:


def num_overvalue(x):
    price_in_title = ""
    list_title_price = []
    for i in range(0,x):
        price_in_title = re.findall(r'\d+', list_title[i])
        if len(price_in_title) > 0:
            price_in_title = price_in_title[0]
        else: 
            price_in_title = 0
        list_title_price.append(int(price_in_title))

    list_price_in_price = []
    price_in_price = ""
    for i in range(0,x):
        price_in_price = re.findall(r'\d+', list_price[i])
        price_in_price = price_in_price[0]
        list_price_in_price.append(int(price_in_price))

    list_shipping_price = []
    price_in_shipping = ""
    for i in range(0,x):
        price_in_shipping = re.findall(r'\d+.\d+', list_shipping[i])
        if len(price_in_shipping) > 0:
            price_in_shipping = price_in_shipping[0]
        else: 
            price_in_shipping = 0
        list_shipping_price.append(float(price_in_shipping))

    counter_sellabove = 0
    for i in range(0,x):
        if list_title_price[i] < list_price_in_price[i] + list_shipping_price[i]:
            counter_sellabove = counter_sellabove + 1
    return(counter_sellabove)

num_overvalue(600)


# ### Question 1.2(f)

# In[439]:


# Calculate fraction
counter1 = num_overvalue(600)
def frac(counter):
    frac = counter/600
    return(frac)

frac(counter1)

### There are several reasons. Firstly, people dont want to buy the gift card by walking out. Secondly,
### maybe there are some knowledge gap and the sellers could use those gaps to make money. Finally, maybe some
### gift card are unique, people like to collect them.


# ### Question 2.2(a)

# In[442]:


def login(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    time.sleep(1) 
    payload = {
        "login_action":"1",
        "login_username":"daran",
        "login_password":"test1234",
        "user_remeber":"1",
        "submit":"1"
    }
    session_requests = requests.session()
    res = session_requests.post(url,payload)
    if "200" in str(res):
        print("Login Successfully!")

login("https://www.fctables.com/user/login/")


# ### Question 2.2(b)

# In[444]:


# Verify my login status by Cookies
def login_cookie(url,page2_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    time.sleep(1) 
    payload = {
        "login_action":"1",
        "login_username":"daran",
        "login_password":"test1234",
        "user_remeber":"1",
        "submit":"1"
    }
    session_requests = requests.session()
    res = session_requests.post(url,payload)
    cookies = session_requests.cookies.get_dict()
    page2 = session_requests.get(page2_url, cookies=cookies)
    if page2.text.find('Wolfsburg') >= 0:
    #The return shows that in index 44473, the word "wolfsburg" showes in the page 2.
        print("Wolfsburg is found!")
    else:
        print('Null')

login_cookie("https://www.fctables.com/user/login/","https://www.fctables.com/tipster/my_bets/")


# In[ ]:




