# "${1}"
date
python3 --version
cd /home/b08305056/fromGit/foodDelivery_crawler
/bin/python3 getNearShop.py --workerNumShop 10 -debug true
/bin/python3 getMeau.py --workerNumMenu 1 -debug true
# python3.8 upload.py
# usr/bin/python3.8 sentOut.py
