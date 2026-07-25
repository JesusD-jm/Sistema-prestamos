import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret'

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'prestamos_db')

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/prestamos_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
