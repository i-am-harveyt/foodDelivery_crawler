import argparse
import concurrent.futures
import json
import os
import random
import time
from datetime import datetime

import bs4
import numpy as np
import pandas as pd
import requests
from fake_useragent import UserAgent
from tqdm import tqdm

"""pass argument"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Finetune a transformers model on a summarization task"
    )
    # ------------------------>
    # parser.add_argument("--center_type", type=str, default='most',)
    parser.add_argument(
        "--shopLstPath",
        type=str,
        default="../panda_data/shopLst",
    )
    parser.add_argument("--outputPath", type=str, default="../panda_data/panda_menu")
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--workerNumShop", type=int, default=10)
    parser.add_argument("--workerNumMenu", type=int, default=1)
    parser.add_argument("--doSleep", type=bool, default=True)
    parser.add_argument("--reTryNum", type=int, default=5)
    args, unknown = parser.parse_known_args()
    return args


def getMenu(restaurant_code, anchor_lat, anchor_lng):
    """
    get menu from restaurant_code
    """
    currentTime = datetime.now()
    result = {}

    ua = UserAgent(os="linux")
    firefox = ua.getFirefox

    # data need for request
    url = f"https://tw.fd-api.com/api/v5/vendors/{restaurant_code}"
    headers = {
        "User-Agent": firefox["useragent"],
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    query = {
        "include": "menus,bundles,multiple_discounts",
        "language_id": 6,
        "opening_type": "delivery",
        "basket_currency": "TWD",
        "latitude": anchor_lat,
        "longitude": anchor_lng,
    }

    def get_data():
        nonlocal data  # nonlocal variable, can be used in the function
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
            print("$429$, sleep")
            sleep_randomly(30, 60)
            get_data()
    except:
        print("connect refused?")
        try:
            # we used this way to get the error message,
            # but sometime it will fail
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
            failDict["shopCode"].append(restaurant_code)
            return result
    # if status code is ok, then get the data
    if data.status_code == requests.codes.ok:
        data = data.json()

        # write into json file
        # if not os.path.exists(f'{args.outputPath}/menuJson_{TODAY}'):
        #     os.makedirs(f'{args.outputPath}/menuJson_{TODAY}')
        # filepath = f'{args.outputPath}/menuJson_{TODAY}/foodpandaMenu_{restaurant_code}.json'
        # with open(filepath, 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False)

        result["shopCode"] = restaurant_code
        result["Url"] = url
        result["address"] = data["data"]["address"]
        result["location"] = [data["data"]["latitude"], data["data"]["longitude"]]
        result["rate"] = data["data"]["rating"]
        result["updateDate"] = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        result["pickup"] = 1 if data["data"]["is_pickup_enabled"] else 0

        # get platform service fee
        # I'm not very sure about the meanings respectively,
        # so I fetch 'em all
        try:
            result["service_fee_total"] = data["data"]["service_fee"]
        except:
            result["service_fee_total"] = 0
        try:
            result["service_fee_type"] = data["data"]["dynamic_pricing"]["service_fee"][
                "type"
            ]
        except:
            result["service_fee_type"] = np.NaN
        try:
            result["service_fee_setup_value"] = data["data"]["dynamic_pricing"][
                "service_fee"
            ]["setup_value"]
        except:
            result["service_fee_setup_value"] = np.NaN

        tmpInshop = 0
        tmp = []

        for item in data["data"]["food_characteristics"]:
            if "店內價" in item["name"]:
                tmpInshop = 1
            else:
                try:
                    tmp.append(item["name"])
                except:
                    pass

        result["inShopPrice"] = tmpInshop
        result["shopTag"] = tmp

        tmp = []

        for discount in data["data"]["discounts"]:
            tmp.append(discount["name"])

        result["discount"] = tmp
        tmp = {
            "id": [],
            "code": [],
            "product": [],
            "variations": {
                "code": [],
                "name": [],
                "preDiscountPrice": [],
                "discountedPrice": [],
            },
            "tags": [],
            "description": [],
        }

        try:
            for category in data["data"]["menus"][0]["menu_categories"]:
                for product in category["products"]:
                    tmp["id"].append(product["id"])
                    tmp["product"].append(product["name"])
                    tmp["description"].append(product["description"])

                    tmp["code"].append(product.get("code", ""))

                    for v in product.get("product_variations", []):
                        tmp["variations"]["code"].append(v.get("code", ""))
                        tmp["variations"]["name"].append(v.get("name", ""))
                        tmp["variations"]["preDiscountPrice"].append(
                            v.get("price_before_discount", "")
                        )
                        tmp["variations"]["discountedPrice"].append(v.get("price", ""))
                    tmp["tags"].append(product.get("tags", []))
        except:
            tmp["product"].append("")
            tmp["variations"]["preDiscountPrice"].append("")
            tmp["variations"]["discountedPrice"].append("")
            tmp["description"].append("")

        result["menu"] = json.dumps(tmp, ensure_ascii=False)
    else:
        try:
            data = data.json()
            result["shopCode"] = restaurant_code
            result["Url"] = url
            result["error"] = data["data"]["error"]
            result["updateDate"] = currentTime
            result["menu"] = ""
            result["address"] = ""
            result["location"] = ""
            result["rate"] = np.NaN
            result["pickup"] = np.NaN
            result["service_fee_total"] = np.NaN
            result["service_fee_type"] = np.NaN
            result["service_fee_setup_value"] = np.NaN
        except:
            pass

    if len(result) == 0:
        print("error code: ", data.status_code)
        failDict["shopCode"].append(restaurant_code)

    return result


if __name__ == "__main__":
    """
    main
    execute time about 2 hours
    """
    args = parse_args()
    # check whether path exist
    if not os.path.exists(f"{args.outputPath}/"):
        os.makedirs(f"{args.outputPath}")

    failDict = {}  # record the fail shop code
    failDict["shopCode"] = []

    # # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    # TODAY = '2023-06-24'
    print("start get menu")

    # read the restuarant list file
    if args.debug:
        shopLst_most = pd.read_csv(
            f"{args.shopLstPath}/all_most_{TODAY}.csv", nrows=100
        )
    else:
        shopLst_most = pd.read_csv(f"{args.shopLstPath}/all_most_{TODAY}.csv")

    """
    get menu data
    we recommend not to set max_workers more than 10, otherwise might be request too fast
    and get 429 error
    it take 1.5~2 hours to go through all the restuarant, about 50,000 resturant in Taiwan
    """
    for i in range(args.reTryNum):
        print(f"{i+1} round get menu")

        if i == 0:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=args.workerNumMenu
            ) as executor:
                ttlResult = list(
                    tqdm(
                        executor.map(
                            getMenu,
                            shopLst_most["shopCode"].to_list(),
                            shopLst_most["anchor_latitude"].to_list(),
                            shopLst_most["anchor_longitude"].to_list(),
                        ),
                        total=len(shopLst_most["shopCode"].to_list()),
                    )
                )
        else:
            if len(failDict["shopCode"]) == 0:
                print("no shop code fail")
                break
            # with concurrent.futures.ThreadPoolExecutor(
            #     max_workers=args.workerNumMenu
            # ) as executor:
            #     failTtlResult = list(
            #         tqdm(
            #             executor.map(getMenu, failDict["shopCode"]),
            #             total=len(failDict["shopCode"]),
            #         )
            #     )
            # # add the fail result ttlResult
            # ttlResult.extend(failTtlResult)
        # conver result to data frame
        df = pd.DataFrame(ttlResult)
        print("number of shop did not catch data: ", df.isnull().sum())
        try:
            df.to_csv(f"{args.outputPath}/foodpandaMenu_{TODAY}.csv")
            print(f"save {{args.outputPath}}/foodpandaMenu_{TODAY}.csv")
        except:
            df.to_csv(f"foodpandaMenu_{TODAY}.csv")
            print(f"save foodpandaMenu_{TODAY}.csv")
