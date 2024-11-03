from telebot import main
from db.createDB import create_database

if __name__ == "__main__":
    create_database()
    main()
    pass