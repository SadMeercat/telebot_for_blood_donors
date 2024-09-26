from DB import createDB
import os

def first_launch():
    createDB.createDB()

if __name__ == "__main__":
    if not os.path.exists("data.db"):
       first_launch()