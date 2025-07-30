import os

class Config:
    SECRET_KEY = 'your_super_secret_key'  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enhanced Caching Configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 1
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default
    
    # Cache-specific timeouts
    CACHE_TIMEOUT_SUBJECTS = 600      # 10 minutes - rarely changes
    CACHE_TIMEOUT_CHAPTERS = 600      # 10 minutes - rarely changes
    CACHE_TIMEOUT_QUIZZES = 300       # 5 minutes - moderate changes
    CACHE_TIMEOUT_QUESTIONS = 180     # 3 minutes - frequent changes
    CACHE_TIMEOUT_CHARTS = 120        # 2 minutes - real-time data
    CACHE_TIMEOUT_USER_DATA = 60      # 1 minute - user-specific data
    CACHE_TIMEOUT_SEARCH = 30         # 30 seconds - search results
    
    # Cache key prefixes for organization
    CACHE_KEY_PREFIX = "quiz_master"
    
    # Email settings for MailHog (local development)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = 'admin@123.com'
    
    # Gmail App Password Instructions:
    # 1. Enable 2-Factor Authentication on your Gmail account
    # 2. Go to Google Account Settings > Security > App Passwords
    # 3. Generate an App Password for "Mail"
    # 4. Use that 16-character password here (not your regular Gmail password)