import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'recipe_app')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')