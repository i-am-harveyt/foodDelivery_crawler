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
    parser.add_argument("--shopLstPath", type=str, default='../panda_data/shopLst',)
    parser.add_argument("--outputPath", type=str, default='../panda_data/panda_menu/')
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--workerNumShop", type=int, default=10)
    parser.add_argument("--workerNumMenu", type=int, default=10)
    parser.add_argument("--doSleep", type=bool, default=True)
    parser.add_argument("--reTryNum", type=int, default=5)
    args, unknown = parser.parse_known_args()
    return args


"""get menu from restaurant_code"""
def getMenu(restaurant_code):
    currentTime = datetime.now()
    result = {}

    # data need for request
    url = f'https://tw.fd-api.com/api/v5/vendors/{restaurant_code}'
    query = {
        'include': 'menus',
        'language_id': '6',
        'dynamic_pricing': '0',
        'opening_type': 'delivery',
    }
    headers = {
        'Connection': 'close',
    }
    
    def get_data():
        nonlocal data # nonlocal variable, can be used in the function
        data = requests.get(
            url=url,
            params=query,
            headers=headers,
            # verify=False,
        )
    
    def sleep_randomly(min_sleep, max_sleep):
        time.sleep(random.uniform(min_sleep, max_sleep))
    
    try:
        if bool(random.choices([1, 0], [1, 9])):
            sleep_randomly(2, 3)
            get_data()
            
        if data.status_code == 429:
            print('$429$, sleep')
            sleep_randomly(30, 60)
            get_data()
    except:
        print("connect refused?")
        try:
            # we used this way to get the error message, but sometime it will fail
            search = bs4.BeautifulSoup(data.text, "lxml")
            print("error message:")
            print(search.text)
        except:
            print("fail to get error message")
        print("sleep ZZZzzz...ZZz..")
        sleep_randomly(30, 60)
        try:
            # try again
            get_data()
        except:
            failDict['shopCode'].append(restaurant_code)
            return result
    # if status code is ok, then get the data
    if data.status_code == requests.codes.ok:
        data = data.json()
        result['shopCode'] = restaurant_code
        result['Url'] = url
        result['address'] = data['data']['address']
        result['location'] = [data['data']['latitude'], data['data']['longitude']]
        result['rate'] = data['data']['rating']
        result['updateDate'] = currentTime
        result['pickup'] = 1 if data['data']['is_pickup_enabled'] else 0
        
        tmpInshop = 0
        tmp = []
        
        for item in data['data']['food_characteristics']:
            if '店內價' in item['name']:
                tmpInshop = 1
            else:
                try:
                    tmp.append(item['name'])
                except:
                    pass
        
        result['inShopPrice'] = tmpInshop
        result['shopTag'] = tmp
        
        tmp = []
        
        for discount in data['data']['discounts']:
            tmp.append(discount['name'])
        
        result['discount'] = tmp
        tmp = {
            'product': [],
            'preDiscountPrice': [],
            'discountedPrice': [],
            'description': []
        }
        
        try:
            for category in data['data']['menus'][0]['menu_categories']:
                for product in category['products']:
                    tmp['product'].append(product['name'])
                    tmp['description'].append(product['description'])
                    
                    try:
                        tmp['preDiscountPrice'].append(product['product_variations'][0]['price_before_discount'])
                    except:
                        tmp['preDiscountPrice'].append('')
                    
                    tmp['discountedPrice'].append(product['product_variations'][0]['price'])
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
    # check whether path exist
    if (os.path.exists(f'{args.outputPath}/')):
        pass
    else:
        os.makedirs(f'{args.outputPath}')

    failDict = {} # record the fail shop code
    failDict['shopCode'] = []

    # # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    # TODAY = '2023-06-24'
    print('start get menu')

    # read the restuarant list file 
    shopLst_most = pd.read_csv(f'{args.shopLstPath}/all_most_{TODAY}.csv')

    """
    get menu data
    we recommend not to set max_workers more than 10, otherwise might be request too fast
    and get 429 error
    it take 1.5~2 hours to go through all the restuarant, about 50,000 resturant in Taiwan
    """
    for i in range(args.reTryNum):
        print(f"{i+1} round get menu")

        if (i == 0):
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workerNumMenu) as executor:
                ttlResult = list(tqdm(executor.map(getMenu, shopLst_most['shopCode'].to_list()),
                total=len(shopLst_most['shopCode'].to_list())))
        else:
            if len(failDict['shopCode']) == 0:
                print('no shop code fail')
                break
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.workerNumMenu) as executor:
                    failTtlResult = list(tqdm(executor.map(getMenu, failDict['shopCode']),
                    total=len(failDict['shopCode'])))
                ttlResult.extend(failTtlResult) # add the fail result ttlResult
        # conver result to data frame
        df = pd.DataFrame(ttlResult)
        print('number of shop did not catch data: ', df.isnull().sum())
        try:
            df.to_csv(f'{args.outputPath}/foodpandaMenu_{TODAY}.csv')
            print(f'save {{args.outputPath}}/foodpandaMenu_{TODAY}.csv')
        except:
            df.to_csv(f'foodpandaMenu_{TODAY}.csv')
            print(f'save foodpandaMenu_{TODAY}.csv')
