import re
import requests
import pandas as pd
import json
from datetime import datetime
import concurrent.futures
import time
from random import randint
import pickle
import os
from tqdm import tqdm
import random
import bs4
import numpy as np

"""input columns:
lat: 中心點latitude, 必要變數
lng: 中心點longitude, 必要變數
city: 中心點所在縣市, 用在output路徑名稱中
loc: 中心點名稱, 用在output路徑名稱中(國小名字：School)

output: dataframe
"""
def getNearShop(lat, lng, city, loc):

    url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'

    result = {}
    result['shopName'] = []
    result['shopCode'] = []
    result['budget'] = []
    result['category'] = []
    result['pandaOnly'] = []
    result['minFee'] = []
    result['minOrder'] = []
    result['minDelTime'] = []
    result['minPickTime'] = []
    result['distance'] = []
    result['rateNum'] = []
    
    query = {
            'longitude': lng,
            'latitude': lat,
            'language_id': 6,
            'include': 'characteristics',
            'dynamic_pricing': 0,
            'configuration': 'Variant1',
            'country': 'tw',
            'budgets': '',
            'cuisine': '',
            'sort': '',
            'food_characteristic': '',
            'use_free_delivery_label': False,
            'vertical': 'restaurants',
            'limit': 48,
            'offset': 0,
            'customer_type': 'regular'
        }
    headers = {
        'x-disco-client-id': 'web',
    }
    r = requests.get(url=url, params=query, headers=headers)

    if r.status_code == requests.codes.ok:
        data = r.json()
        datalen = data['data']['available_count']
        restaurants = data['data']['items']
        for restaurant in restaurants:
            result['shopName'].append(restaurant['name'])
            result['shopCode'].append(restaurant['code'])
            result['budget'].append(restaurant['budget'])
            result['distance'].append(restaurant['distance'])
            result['pandaOnly'].append(restaurant['is_best_in_city'])
            result['rateNum'].append(restaurant['review_number'])
            
            tmp = []
            for cat in restaurant['cuisines']:
                tmp.append(cat['name'])
            result['category'].append(tmp)
            try:
                result['minFee'].append(restaurant['minimum_delivery_fee'])
            except:
                result['minFee'].append("")
            try:
                result['minOrder'].append(restaurant['minimum_order_amount'])
            except:
                result['minOrder'].append("")
            try:
                result['minDelTime'].append(restaurant['minimum_delivery_time'])
            except:
                result['minDelTime'].append("")
            try:
                result['minPickTime'].append(restaurant['minimum_pickup_time'])
            except:
                result['minPickTime'].append("")

    for i in range(1, datalen, 100):
        query = {
            'longitude': lng,
            'latitude': lat,
            'language_id': 6,
            'include': 'characteristics',
            'dynamic_pricing': 0,
            'configuration': 'Variant1',
            'country': 'tw',
            'budgets': '',
            'cuisine': '',
            'sort': '',
            'food_characteristic': '',
            'use_free_delivery_label': False,
            'vertical': 'restaurants',
            'limit': datalen,
            'offset': i,
            'customer_type': 'regular'
        }
        headers = {
            'x-disco-client-id': 'web',
        }
        r = requests.get(url=url, params=query, headers=headers)

        if i%10==0:
            time.sleep(3)
            print('sleeping at', i)
        elif i%5==0:
            time.sleep(randint(0,4))
            print('sleeping at' , i)

        if r.status_code == requests.codes.ok:
            data = r.json()
            restaurants = data['data']['items']
            for restaurant in restaurants:
                result['shopName'].append(restaurant['name'])
                result['shopCode'].append(restaurant['code'])
                result['budget'].append(restaurant['budget'])
                result['distance'].append(restaurant['distance'])
                result['pandaOnly'].append(restaurant['is_best_in_city'])
                result['rateNum'].append(restaurant['review_number'])
                tmp = []
                for cat in restaurant['cuisines']:
                    tmp.append(cat['name'])
                result['category'].append(tmp)
                try:
                    result['minFee'].append(restaurant['minimum_delivery_fee'])
                except:
                    result['minFee'].append("")
                try:
                    result['minOrder'].append(restaurant['minimum_order_amount'])
                except:
                    result['minOrder'].append("")
                try:
                    result['minDelTime'].append(restaurant['minimum_delivery_time'])
                except:
                    result['minDelTime'].append("")
                try:
                    result['minPickTime'].append(restaurant['minimum_pickup_time'])
                except:
                    result['minPickTime'].append("")
        else:
            print('faill to request')
    df = pd.DataFrame.from_dict(result)

    # output path, change this if needed
    # creat date folder under shoplist if it is not exsist
    if (os.path.exists(f'./shopLst/{TODAY}')):
        pass
    else:
        os.makedirs(f'./shopLst/{TODAY}')
    df.to_csv(f'./shopLst/{TODAY}/shopLst_{city}_{loc}_{TODAY}.csv')
    print(f'write ./shopLst/{TODAY}/shopLst_{city}_{loc}_{TODAY}.csv', 'shopNum:', len(df))

"""
concat shopLst_{city}_{loc}_{TODAY}.csv
to
./shopLst/{TODAY}/all_most_{TODAY}.csv 
"""
def concatDF():
    joinedlist = []
    # 資料夾路徑
    dir_list = os.listdir(f'./shopLst/{TODAY}/')

    # read all shopLst_{city}_{loc}_{TODAY}.csv
    for file in dir_list:
        if (file != '.DS_Store') and (TODAY in file) and ('shopLst_' in file):
            tmp = pd.read_csv(f'./shopLst/{TODAY}/{file}')
            joinedlist.append(tmp)

    df = pd.concat(joinedlist)
    df = df.dropna()
    df = df.drop_duplicates(subset=['shopCode'])
    df.to_csv(f'./shopLst/{TODAY}/all_most_{TODAY}.csv')
    print(f'write ./shopLst/{TODAY}/all_most_{TODAY}.csv')

    return df

"""
get menu from restaurant_code
"""
def getMenu(restaurant_code):
    
    currentTime = datetime.now()
    result = {}
    url = f'https://tw.fd-api.com/api/v5/vendors/{restaurant_code}'
    query = {
        'include': 'menus',
        'language_id': '6',
        'dynamic_pricing': '0',
        'opening_type': 'delivery',
    }
    # can add more detail information in the header, to let the crawler like real user
    headers = {
        'Connection':'close',
    }
    try:
        # need sleep to prevent error 429
        if bool(random.choices([1, 0], [1, 9])): # 90% not sleep, 10% sleep
            time.sleep(random.uniform(0.5, 1.5)) # randomly sleep 0.5~1.5s, the minium requirement
            data = requests.get(
                url=url,
                params=query,
                headers=headers, 
                )
        if (data.status_code == 429):
            print('$429$, sleep')
            time.sleep(random.uniform(30, 60))
            data = requests.get(
            url=url,
            params=query,
            headers=headers,
            )
    except:
        print("connect refused?")
        search = bs4.BeautifulSoup(data.text, "lxml")
        # get the error message if website refused to connect
        print(search.text)
        # randomly sleep 5~10s, if website refused to connect
        print("sleep ZZZzzz...ZZz..")
        time.sleep(random.uniform(5, 10))
        data = requests.get(
            url=url,
            params=query,
            headers=headers,
            )
        
    if data.status_code == requests.codes.ok:
        data = data.json()
        result['shopCode'] = restaurant_code
        result['Url'] = url
        result['address'] = data['data']['address']
        result['location'] = [data['data']['latitude'], data['data']['longitude']]
        result['rate'] = data['data']['rating']
        result['updateDate'] = currentTime
        tmp = []
        if data['data']['is_pickup_enabled']==True:
            result['pickup'] = 1
        else:
            result['pickup'] = 0
        tmpInshop = 0
        for i in range(len(data['data']['food_characteristics'])):
            if '店內價' in data['data']['food_characteristics'][i]['name']:
                tmpInshop = 1
            else:
                try:
                    tmp.append(data['data']['food_characteristics'][i]['name'])
                except:
                    pass
        if tmpInshop==1:
            result['inShopPrice'] = 1
        else:
            result['inShopPrice'] = 0

        result['shopTag'] = tmp

        tmp = []
        for i in range(len(data['data']['discounts'])):
            tmp.append(data['data']['discounts'][i]['name'])
        result['discount'] = tmp
        tmp = {}
        tmp['product'] = []
        tmp['preDiscountPrice'] = []
        tmp['discountedPrice'] = []
        try:
            for i in range(len(data['data']['menus'][0]['menu_categories'])):
                for k in range(len(data['data']['menus'][0]['menu_categories'][i]['products'])):
                    tmp['product'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['name'])
                    try:
                        tmp['preDiscountPrice'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['product_variations'][0]['price_before_discount'])
                    except:
                        tmp['preDiscountPrice'].append('')
                    tmp['discountedPrice'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['product_variations'][0]['price'])
        except:
            tmp['product'].append('')
            tmp['preDiscountPrice'].append('')
            tmp['discountedPrice'].append('')
        
        result['menu'] = tmp
    else:
        try:
            data = data.json()
            result['shopCode'] = restaurant_code
            result['Url'] = url
            result['error'] = data['data']['error']
            result['updateDate'] = currentTime
            result['menu'] = ""
            result['address'] = ""
            result['location'] = ""
            result['rate'] = np.NaN
            result['pickup'] = np.NaN
        except:
            pass
    if len(result) == 0:
      print('error code: ', data.status_code)
    return result

'''main'''
'''execute time about 2 hours'''
if __name__ == '__main__':
    
    # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    print(TODAY)

    # read central location information
    centerLst_most = pd.read_csv('./inputCentral/school_most.csv')

    # get shop data around center point
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        ttlResult = list(executor.map(getNearShop,
        centerLst_most['latitude'].to_list(),
        centerLst_most['longitude'].to_list(),
        centerLst_most['City'].to_list(),
        centerLst_most['School'].to_list(),
        ))

    # concat all the restuarant list, output: 
    shopData = concatDF()
    print('number of resuarant in total: ', len(shopData))

    # read the restuarant list file 
    shopLst_most = pd.read_csv(f'./shopLst/{TODAY}/all_most_{TODAY}.csv')

    """
    get menu data
    we recommend not to set max_workers more than 10, otherwise might be request too fast
    and get 429 error
    it take 1.5~2 hours to go through all the restuarant, about 50,000 resturant in Taiwan
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        ttlResult = list(tqdm(executor.map(getMenu, shopLst_most['shopCode'].to_list()),
        total=len(shopLst_most['shopCode'].to_list())))

    # conver result to data frame
    df = pd.DataFrame(ttlResult)
    print('number of shop did not catch data: ', df.isnull().sum())
    df.to_csv(f'./meau_Foodpanda/foodpandaMenu_{TODAY}.csv')

'''
this code is originally creat by 吳昕晏, modify by Yu-Shin, Liou
Modified the input output structure, fix the error caused by intense request.
Also notice the duplicate data in shopLst_most.
After drop the duplicted data, the number of shop will decrease from about 1,000,000 to 50,000
'''