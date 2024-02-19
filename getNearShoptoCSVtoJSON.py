import os
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
import time
from tqdm import tqdm
import random
import argparse
import json

# global var, so toxic LOL
failed_cnt = 0

def parse_args():
    parser = argparse.ArgumentParser(
        description="get shop list from specific location")
    # ------------------------>
    parser.add_argument("--centerFile", type=str, default='tw_points.csv',)
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--workerNumShop", type=int, default=1)
    parser.add_argument("--doSleep", type=bool, default=True)
    parser.add_argument("--outputPath", type=str,
                        default='../panda_data/shopLst/')
    args, _ = parser.parse_known_args()
    return args


def getNearShop(lat, lng, available_counts={}):
    """input columns:
    lat: 中心點latitude, 必要變數
    lng: 中心點longitude, 必要變數
    city: 中心點所在縣市, 用在output路徑名稱中
    loc: 中心點名稱, 用在output路徑名稱中(國小名字：School)
    output: dataframe
    """

    URL = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'
    now = datetime.now()
    result = {
        'shopName': [], 'shopCode': [], 'budget': [],
        'category': [], 'pandaOnly': [], 'minFee': [],
        'minOrder': [], 'minDelTime': [], 'minPickTime': [],
        'distance': [], 'rateNum': [], 'address': [],
        'chainCode': [], 'city': [],
        "latitude": [], "longitude": [],
        "anchor_latitude": [], "anchor_longitude": [],
        "hasServiceFee": [],
        "serviceFeeAmount(%)": [], "updateDate": [],
        "tags": [],
    }

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
        'limit': 30,
        'offset': 0,
        'customer_type': 'regular'
    }
    headers = {
        'x-disco-client-id': 'web',
    }
    # need sleep between request to prevent error 429
    time.sleep(random.uniform(3, 4))

    res = requests.get(url=URL, params=query, headers=headers)

    if res.status_code != requests.codes.ok:
        print(f"\n{lat}, {lng} not ok\n===")
        return
    data = res.json()

    # get total number of restaurants = datalen
    datalen = data['data']['available_count']
    restaurants = data['data']['items']

    PAGE_SIZE = 30
    offset = 0
    while True:
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
            'limit': PAGE_SIZE,
            'offset': offset,
            'customer_type': 'regular'
        }
        headers = {
            'x-disco-client-id': 'web',
        }
        res = requests.get(url=URL, params=query, headers=headers)

        time.sleep(1+random.random())

        if res.status_code != requests.codes.ok:
            print('fail to request')
            print(res.text)
            failed_cnt += 1
            continue

        restaurants = res.json()["data"]["items"]
        if len(restaurants) == 0:
            break
        # go through all the restaurants
        offset += len(restaurants)
        for restaurant in restaurants:
            # save to json file
            # if not os.path.exists(f'{args.outputPath}/shop_json'):
            #     os.makedirs(f'{args.outputPath}/shop_json')
            # filepath = f'{args.outputPath}/shop_json/foodpandaShop_{restaurant.get("code", "")}.json'
            # if not os.path.exists(filepath):
            #     with open(filepath, 'w', encoding='utf-8') as f:
            #         json.dump(restaurant, f, ensure_ascii=False)

            result['shopName'].append(restaurant.get('name', ''))
            result['shopCode'].append(restaurant.get('code', ''))
            result['budget'].append(restaurant.get('budget', 0))
            result['distance'].append(restaurant.get('distance', 0.0))
            result['pandaOnly'].append(
                restaurant.get('is_best_in_city', False))
            result['rateNum'].append(restaurant.get('review_number', 0))
            result['updateDate'].append(now.strftime("%Y-%m-%d %H:%M:%S"))
            result['city'].append(restaurant['city'].get('name', ''))
            result['address'].append(restaurant.get('address', ''))
            result['latitude'].append(restaurant.get('latitude', 0.0))
            result['longitude'].append(restaurant.get('longitude', 0.0))
            result['anchor_latitude'].append(lat)
            result['anchor_longitude'].append(lng)
            result['hasServiceFee'].append(
                restaurant.get('is_service_fee_enabled', False))
            result['serviceFeeAmount(%)'].append(
                restaurant.get('service_fee_percentage_amount', 0))

            categories = [
                cat['name'] for cat in restaurant.get('cuisines', None)]
            result['category'].append(categories)

            chain = restaurant['chain'].get(
                'main_vendor_code', "") if restaurant.get('chain') else ""
            result['chainCode'].append(chain)

            result["minFee"].append(
                restaurant.get('minimum_delivery_fee', 0))
            result["minOrder"].append(
                restaurant.get('minimum_order_amount', 0))
            result["minDelTime"].append(
                restaurant.get('minimum_delivery_time', 0))
            result["minPickTime"].append(
                restaurant.get('minimum_pickup_time', 0))

            result["tags"].append(
                json.dumps(restaurant.get("tags", []), ensure_ascii=False)
            )
    df = pd.DataFrame.from_dict(result)

    # output path, change this if needed
    # creat date folder under shoplist if it is not exsist
    if not os.path.exists(f'{args.outputPath}/{TODAY}'):
        os.makedirs(f'{args.outputPath}/{TODAY}')
    print(
        f"({lat}, {lng}) available: {df.shape[0]}/{datalen}\n===")
    df.to_csv(
        f'{args.outputPath}/{TODAY}/shopLst_{lng}_{lat}_{TODAY}.csv')


def concatDF():
    """
    concat
    shopLst_{city}_{loc}_{TODAY}.csv
    to
    {args.outputPath}/{TODAY}/all_most_{TODAY}.csv
    """
    joinedlist = []
    # 資料夾路徑
    dir_list = os.listdir(f'{args.outputPath}/{TODAY}/')

    # read all shopLst_{city}_{loc}_{TODAY}.csv
    for file in dir_list:
        if (file != '.DS_Store') and (TODAY in file) and\
                ('shopLst_' in file) and ('json' not in file):
            tmp = pd.read_csv(f'{args.outputPath}/{TODAY}/{file}')
            joinedlist.append(tmp)

    df = pd.concat(joinedlist)
    # df = df.dropna()
    df = df.drop_duplicates(subset=['shopCode'])  # drop duplicate shopCode
    df.to_csv(f'{args.outputPath}/{TODAY}/all_most_{TODAY}.csv')
    df.to_csv(f'{args.outputPath}/all_most_{TODAY}.csv')
    print(f'write {args.outputPath}/{TODAY}/all_most_{TODAY}.csv')
    return df


if __name__ == '__main__':
    args = parse_args()
    available_counts = {}

    # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    print(TODAY)

    if args.debug:
        getNearShop(lat=24.903991, lng=121.040505,
                    available_counts=available_counts)
        exit()

    # read central location information
    centerLst_most = pd.read_csv(
        f'./inputCentral/{args.centerFile}',
    )

    # get shop data around center point
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=args.workerNumShop) as executor:
        ttlResult = list(
            tqdm(
                executor.map(
                    getNearShop,
                    centerLst_most['newLat'].to_list(),
                    centerLst_most['newLng'].to_list(),
                    [available_counts for _ in range(len(centerLst_most))],
                )))
    print('shop catch down')
    # concat all the restuarant list, output:
    shopData = concatDF()

    pd.DataFrame(
        data=available_counts).to_csv(f'{args.outputPath}/{TODAY}/availableCounts.csv')

    print('number of resuarant in total: ', len(shopData))
    print(f"failed_count {failed_cnt}")
