import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    
    # OpenGauss数据库配置
    DB_HOST = 'localhost'  # 如果Docker映射到本地，使用localhost
    DB_PORT = 5432  # OpenGauss默认端口，根据你的Docker映射修改
    DB_NAME = 'music_db'  # 你的数据库名
    DB_USER = 'gaussdb'  # 你的数据库用户名
    DB_PASSWORD = 'Gauss@123'
    
    # 数据库连接字符串
    DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
