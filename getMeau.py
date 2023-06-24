import os
# os.system('pip install -r requirements.txt')
import re
import requests
import pandas as pd
import json
from datetime import datetime
import concurrent.futures
import time
from random import randint
import pickle
from tqdm import tqdm
import random
import bs4
import numpy as np
import argparse
from dropbox.exceptions import AuthError
import pathlib
import shutil

"""pass argument"""
def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers model on a summarization task")
    # ------------------------>
    # parser.add_argument("--center_type", type=str, default='most',)
    parser.add_argument("--shopLstPath", type=str, default='../panda_data/shopLst/',)
    parser.add_argument("--outputPath", type=str, default='../panda_data/panda_menu/')
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--workerNumShop", type=int, default=10)
    parser.add_argument("--workerNumMenu", type=int, default=5)
    parser.add_argument("--doSleep", type=bool, default=True)
    args, unknown = parser.parse_known_args()
    return args


"""get menu from restaurant_code"""
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
        if bool(random.choices([1, 0], [4, 6])): # 60% not sleep, 40% sleep
            time.sleep(random.uniform(2, 3)) # randomly sleep 0.5~1.5s, the minium requirement
            data = requests.get(
                url=url,
                params=query,
                headers=headers, 
                )
        if (data.status_code == 429):
            print('$429$, sleep')
            time.sleep(random.uniform(30, 60)) # sleep 30~60s
            data = requests.get(
            url=url,
            params=query,
            headers=headers,
            )
    except:
        print("connect refused?")
        search = bs4.BeautifulSoup(data.text, "lxml")
        # get the error message if website refused to connect
        print("error message:")
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
        tmp['description'] = []
        try:
            for i in range(len(data['data']['menus'][0]['menu_categories'])):
                for k in range(len(data['data']['menus'][0]['menu_categories'][i]['products'])):
                    tmp['product'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['name'])
                    tmp['description'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['description'])
                    try:
                        tmp['preDiscountPrice'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['product_variations'][0]['price_before_discount'])
                    except:
                        tmp['preDiscountPrice'].append('')
                    tmp['discountedPrice'].append(data['data']['menus'][0]['menu_categories'][i]['products'][k]['product_variations'][0]['price'])
        except:
            tmp['product'].append('')
            tmp['preDiscountPrice'].append('')
            tmp['discountedPrice'].append('')
            tmp['description'].append('')
        
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

    args = parse_args()
    
    # # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    print('start get menu')

    # read the restuarant list file 
    shopLst_most = pd.read_csv(f'{args.shopLstPath}/all_most_{TODAY}.csv')

    """
    get menu data
    we recommend not to set max_workers more than 10, otherwise might be request too fast
    and get 429 error
    it take 1.5~2 hours to go through all the restuarant, about 50,000 resturant in Taiwan
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workerNumMenu) as executor:
        ttlResult = list(tqdm(executor.map(getMenu, shopLst_most['shopCode'].to_list()),
        total=len(shopLst_most['shopCode'].to_list())))

    # conver result to data frame
    df = pd.DataFrame(ttlResult)
    print('number of shop did not catch data: ', df.isnull().sum())
    df.to_csv(f'{args.outputPath}/foodpandaMenu_{TODAY}.csv')
    print(f'save {{args.outputPath}}/foodpandaMenu_{TODAY}.csv')
