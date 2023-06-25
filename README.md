# Crawler for Foodpanda

Create for research project in Research Center for Humanities and Social Sciences. We use elementary school in Taiwan as our central location (about 544) and scrapy food menu from the restaurant located near by the school.

## folder structure

```
├── foodDelivery_crawler
│   ├── README.md
│   ├── getMeau.py
│   ├── getNearShop.py
│   ├── getProxy.py
│   ├── inputCentral
│   │   └── school.csv
│   ├── requirements.txt
│   ├── run.sh
│   └── sentMail.py
│   └── shopLst
│   ├── {date} # eg. 2023-06-24
│   │   ├── all_most_{date}.csv # eg. all_most_2023-06-24.csv
│   │   ├── shopLst_{city}_{school}_{data}.csv # eg. shopLst_金門縣_縣立金寧國(中)小_2023-06-24.csv
│   └── meau_Foodpanda
│   │   └── foodpandaMenu_{date}.csv # eg. foodpandaMenu_2023-06-24.csv
```

## 1.Set up environment

We recommend to creat an environment for our crawler. The fellowing command creat a environment name `spider`, and assign python version as 3.8

key in the fellowing command in your command line:

```
conda create --name spider python=3.8
```

install the package we need

```
pip3 install -r requirements.txt
```

* sync data with google drive
  
  * To sync our data between google drive and remote server, we use `google-drive-ocamlfuse`
  
  * google-drive-ocamlfuse is a FUSE filesystem for Google Drive, written in OCaml. It lets you mount your Google Drive on Linux.

```
sudo add-apt-repository ppa:alessandro-strada/ppa
sudo apt-get install google-drive-ocamlfuse
google-drive-ocamlfuse # open browser ask for authorize access of gdrive
mkdir ~/migoogledrive # create a folder for gdrive
google-drive-ocamlfuse ~/migoogledrive
```

now you can creat a folder in `migoogledrive` to clone this repo, for example:

```
cd path/to/migoogledrive
mkdir yourWebCrawler
git clone git@github.com:yushinliou/foodDelivery_crawler.git
```



## 2. prepare input

You need to prepare an csv file contain the central location you want to get foodpanda menu. This file should at least contain 4 columns.

1. latitude:
+ float

+ latitude of central location
2. longitude
+ float

+ longitude of central location
3. City
+ str

+ city name, like `台北市`
4. School
+ str

+ central location name

+ In our project it is the name of elementary school, like `市立天母國小`

Our input is in `./inputCentral`, named `school.csv`. If need, you can replace it with your own interested central location list.

## 3. Execute crawler: run.sh

```
bash run.sh
```

The input file we provided have 544 central location and it take hours (around 4~5) to finish. To prevent our program accidentally interpreted by SSH connection exit or terminal window close, we recommend use:

```
nohup bash run.sh > out.txt 2>&1 &
```

* run.sh
  
  * Firstly, Our program will scan all the central location listed in input file and get a list of restarant near by central location.
  - For each central location, our program will generate csv files save in `outputPath"` (by default it is `../panda_data/shopLst/`) with format `shopLst_{city}_{school}_{data}.csv`
  
  - After scan all the central location, our program will generate a csv file `all_most_{date}.csv` concat all the `shopLst_{city}*{school}*{data}.csv`

```
date # show date
python3 --version # python3.8 is recommend
cd /path/to/run.sh/ # remember to replace this with the code path in your device
/bin/python3 getNearShop.py
/bin/python3 getMeau.py
```

* output file structure

```
│   └── shopLst
│   ├── {date} # eg. 2023-06-24
│   │   ├── all_most_{date}.csv # eg. all_most_2023-06-24.csv
│   │   ├── shopLst_{city}_{school}_{data}.csv # eg. shopLst_金門縣_縣立金寧國
```

you can supervise the pregress of crawler by

```
cat out.txt
```

the output should look like:

```
公曆 20廿三年 六月 廿五日 週日 一時廿五分十一秒
Python 3.8.10
2023-06-25
1it [00:11, 11.85s/it]
```

getNearShop from central location takes about 10 minuts, usually we will get around 50000+ shop in `all_most_{date}.csv`. It takes around 6 hours for `getMenu.py` request menu for all shop.

### getNearShop.py

The argument you can pass to getNearShop.py

* centerFile, type=str, default='school.csv'
  
  * By default, the in put file name is `school.csv`. locat in `inputCentral`. You can change the in put file name by passing variable in to

* debug, type=bool, default=False
  
  * if debug, only request shopLst for first 3 central location in `school.csv`
+ workerNumShop", type=int, default=10
  
  + we parallel request to faster the speed of request shop information near by central location
  
  + this arguement set max_workers for ThreadPoolExecutor

+ doSleep", type=bool, default=True
  
  + whether to sleep between request
  
  + to prevent max entries error or error 429, sleep is recommend

+ outputPath", type=str, default='../panda_data/shopLst/'
  
  + the path of output
  
  + auto check whether output path exist, if not, generate a folder for out put

### The columns in `shopLst_most_{date}.csv`

1. shopName
+ string, resturant name
2. shopCode
+ 4 digit string, a unique value

+ example: `y0yc`
3. budget
+ int
4. category
+ list like string, means resturant category

+ example: `['歐美', '炸雞']`
5. pandaOnly
+ bool value
6. minFee
+ int
7. minOrder
+ int
8. minDelTime
+ int
9. minPickTime
+ int
10. distance
+ float
11. rateNum
+ int

+ number of people rate resturant

### getMeau.py

The argument you can pass to getNearShop.py

* shopLstPath, type=str, default='../panda_data/shopLst',

* outputPath, type=str, default='../panda_data/panda_menu/'
  
  * the path of output
  - auto check whether output path exist, if not, generate a folder for out put

* debug, type=bool, default=False
  
  * if debug, only request shopLst for first 3 rows in all_most_{date}.csv

* workerNumShop, type=int, default=10
  
  * we parallel request to faster the speed of request menu
  
  * this arguement set max_workers for ThreadPoolExecutor

* workerNumMenu, type=int, default=5

* doSleep, type=bool, default=True
  
  * whether to sleep between request
  
  * to prevent max entries error or error 429, sleep is recommend

## Auto execute crawler

we use `crontab` to auto execute crawler. It a command in Unix-like operating systems allows users to schedule and automate recurring tasks or commands to be executed at specific times or intervals.

Our operating system is `ubuntu` Ubuntu is a popular open-source operating system based on the Linux kernel. If you use other operating system my might need to consider use other commend to acheive auto execute.

First of all, we need to modify the permission of `run.sh` Eable it read, write and execute. Open your terminal and run the fellowing commend:

```
chmod 755 path/to/your/run.sh
```

To edit crontab commemd:

```
crontab -e # edit crontab commend 
```

You should see the output look like:

```
# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
# 
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
# 
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 
# m h  dom mon dow   command
# ┌───────────── 分鐘   (0 - 59)
# │ ┌─────────── 小時   (0 - 23)
# │ │ ┌───────── 日     (1 - 31)
# │ │ │ ┌─────── 月     (1 - 12)
# │ │ │ │ ┌───── 星期幾 (0 - 7，0 是週日，6 是週六，7 也是週日)
# │ │ │ │ │
```

We hope to craw data in every day 9:00 AM, so we add these line in the end of crontab file

```
00 9 * * * nohup bash absolute/path/to/your/run.sh > /absolute/path/to/your/out.txt 2>&1 &
```

You can refer  [cronitor](https://crontab.guru) if you want to set other schedule for crontab.
