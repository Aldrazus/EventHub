#this file probably will not be used after switch to SQLAlchemy

import pymysql.cursors
import config

#returns connection to database
def connect():
    conn = pymysql.connect(host=config.DB_HOST,
                       user=config.DB_USER,
                       password=config.DB_PASSWORD,
                       db=config.DB_NAME,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

    return conn