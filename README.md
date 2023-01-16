# Crawler for Foodpanda
Create for research project in Research Center for Humanities and Social Sciences. We use elementary school in Taiwan as our central location (about 354) and scrapy food menu from the restaurant located near by the school.

## file 
````
[
  '|-- uber爬蟲',
  '    |-- README.md',
  '    |-- foodpanda.py',
  '    |-- requirements.txt',
  '    |-- inputCentral',
  '    |   |-- school_most.csv',
  '    |   |-- school_nearest.csv',
  '    |-- meau_Foodpanda',
  '    |   |-- foodpandaMenu_{date}.csv',
  '    |-- shopLst',
  '        |-- {date}'
  '            |-- shopLst_{City}_{School}_{date}
  '            |-- shopLst_most_{date}.csv
  '
  '
]
````

## 1.Set up environment
We recommend to creat an environment for our crawler. Creat a environment name `spider`, and assign python version as 3.8
````
conda create --name spider python=3.8
````
install the package we need
````
pip3 install -r requirements.txt
````
## 2. prepare input
Input for `foodpanda.py` is a list of central location, this file should contain 4 columns.

1. latitude: 
    + latitude
    + longitude of central location
2. longitude
    + float
    + longitude of central location
3. City
    + city name, like `台北市`
4. School
    + central location name, it should be a unique string
    + In our project it is the name of elementary school, like `市立天母國小`
Our input is in `inputCentral`, `school_most.csv`

## 3. Get restaurant menu near by contral location
execute foodpanda.py
````
bash foodpanda.py
````
It will scan all the central location list in `school_most.csv`. 
````
[
  '|-- foodpanda_crawler',
  '    |-- inputCentral',
  '    |   |-- school_most.csv',
]
````
foodpanda.py will create a folder name by `date`
for each central location, foodpanda.py will output a csv file in `date`
````
[
  '|-- uber爬蟲',
  '    |-- README.md',
  '    |-- foodpanda.py',
  '    |-- requirements.txt',
  '    |-- inputCentral',
  '    |   |-- school_most.csv',
  '    |-- shopLst',
  '        |-- {date}'
  '            |-- shopLst_{City}_{School}_{date}
  '            |-- shopLst_most_{date}.csv
]
````
including all the restaurant near by the central location.
the file name will be like `shopLst_{City}_{School}_{date}`
`date` means the date we craw the data
`School` is the school columns in school_most.csv 

After that, we concat all the resturant list together and get `shopLst_most_{date}.csv`

the columns in `shopLst_most_{date}.csv`

1. shopName
    + string, resturant name
2. shopCode
    + 4 digit string, a unique value
    + example `y0yc`
3. budget
    + int
4. category
    + list like string, means resturant category
    + example `['歐美', '炸雞']`
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

Finally, we creat `foodpandaMenu_{date}.csv` according to the restuarant list in `meau_Foodpanda` called `foodpandaMenu_{date}.csv`
````
[
  '|-- foodpanda_crawler',
  '    |-- README.md',
  '    |-- foodpanda.py',
  '    |-- requirements.txt',
  '    |-- inputCentral',
  '    |   |-- school_most.csv',
  '    |-- meau_Foodpanda',
  '    |   |-- foodpandaMenu_{date}.csv',
  '    |-- shopLst',
  '        |-- {date}'
  '            |-- shopLst_{City}_{School}_{date}
  '            |-- shopLst_most_{date}.csv
]
````

