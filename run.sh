# "${1}"
date
cd /home/b08305056/Downloads/panda0208
python3 getNearShop.py --workerNumShop 10
python3 getMeau.py --workerNumMeau 5
# python3 upload.py
python3 sentOut.py
