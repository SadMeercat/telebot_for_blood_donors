from sqlalchemy import create_engine
from prepDB import hospital_controlDB, parser, schemas
import os

def createDB():
    if not os.path.exists("data.db"):
        engine = create_engine("sqlite:///data.db")
        schemas.Base.metadata.create_all(engine)
        #hospital_controlDB.add_hospitals_to_db(parser.get_data())

if __name__ == "__main__":
    createDB()