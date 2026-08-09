from datetime import timedelta
import os


import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True) # <-- ADD THIS

class Config:
    
    SECRET_KEY = os.environ.get('KEY', 'this_is_super_secret_key')

    # SQLite database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "trekking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'thisisjwtkey')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Redis Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB=1
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery 
    
    broker_url = "redis://localhost:7000/1"
    result_backend = "redis://localhost:7000/2"
    
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authorization"
    
    admin_email = "admin@gmail.com"
    admin_password = "admin123"