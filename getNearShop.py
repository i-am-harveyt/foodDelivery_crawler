import os
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
import time
from random import randint
from tqdm import tqdm
import random
import argparse

"""pass argument"""
def parse_args():
    parser = argparse.ArgumentParser(description="get shop list from specific location")
    # ------------------------>
    parser.add_argument("--centerFile", type=str, default='school.csv',)
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--workerNumShop", type=int, default=10)
    parser.add_argument("--doSleep", type=bool, default=True)
    parser.add_argument("--outputPath", type=str, default='../panda_data/shopLst/')
    args, unknown = parser.parse_known_args()
    return args

"""input columns:
lat: 中心點latitude, 必要變數
lng: 中心點longitude, 必要變數
city: 中心點所在縣市, 用在output路徑名稱中
loc: 中心點名稱, 用在output路徑名稱中(國小名字：School)

output: dataframe
"""
def getNearShop(lat, lng, city, loc):

    url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'
    currentTime = datetime.now() 
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
    # need sleep between request to prevent error 429
    if args.doSleep:
        if bool(random.choices([1, 0], [1, 9])): # 90% not sleep, 10% sleep
            time.sleep(random.uniform(0.5, 1.5)) # randomly sleep 0.5~1.5s, the minium requirement

    r = requests.get(url=url, params=query, headers=headers)

    if r.status_code == requests.codes.ok:
        data = r.json()
        # get total number of restaurants = datalen
        datalen = data['data']['available_count']
        restaurants = data['data']['items']
        # go through all the restaurants
        for restaurant in restaurants:
            result['shopName'].append(restaurant['name'])
            result['shopCode'].append(restaurant['code'])
            result['budget'].append(restaurant['budget'])
            result['distance'].append(restaurant['distance'])
            result['pandaOnly'].append(restaurant['is_best_in_city'])
            result['rateNum'].append(restaurant['review_number'])
            result['updateDate'] = currentTime
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
    # 
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
    if (os.path.exists(f'{args.outputPath}/{TODAY}')):
        pass
    else:
        os.makedirs(f'{args.outputPath}/{TODAY}')
    df.to_csv(f'{args.outputPath}/{TODAY}/shopLst_{city}_{loc}_{TODAY}.csv')

"""
concat shopLst_{city}_{loc}_{TODAY}.csv to {args.outputPath}/{TODAY}/all_most_{TODAY}.csv """
def concatDF():
    joinedlist = []
    # 資料夾路徑
    dir_list = os.listdir(f'{args.outputPath}/{TODAY}/')

    # read all shopLst_{city}_{loc}_{TODAY}.csv
    for file in dir_list:
        if (file != '.DS_Store') and (TODAY in file) and ('shopLst_' in file):
            tmp = pd.read_csv(f'{args.outputPath}/{TODAY}/{file}')
            joinedlist.append(tmp)

    df = pd.concat(joinedlist)
    df = df.dropna()
    df = df.drop_duplicates(subset=['shopCode']) # drop duplicate shopCode
    df.to_csv(f'{args.outputPath}/{TODAY}/all_most_{TODAY}.csv')
    df.to_csv(f'{args.outputPath}/all_most_{TODAY}.csv')
    print(f'write {args.outputPath}/{TODAY}/all_most_{TODAY}.csv')
    return df


'''main'''
'''execute time about 2 hours'''
if __name__ == '__main__':

    args = parse_args()
    print()
    
    # # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    print(TODAY)

    # read central location information
    if args.debug:
        centerLst_most = pd.read_csv(
            f'./inputCentral/{args.centerFile}',
            nrows=1,
            )
    else:
        centerLst_most = pd.read_csv(
            f'./inputCentral/{args.centerFile}',
            )        

    # get shop data around center point
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workerNumShop) as executor:
        ttlResult = list(tqdm(executor.map(getNearShop,
        centerLst_most['newLat'].to_list(),
        centerLst_most['newLng'].to_list(),
        # centerLst_most['City'].to_list(),
        # centerLst_most['School'].to_list(),
        )))
    print('shop catch down')
    # concat all the restuarant list, output: 
    shopData = concatDF()
    print('number of resuarant in total: ', len(shopData))

