import psycopg2
from psycopg2 import pool
from config import Config

class Database:
    """数据库连接池管理类"""
    _connection_pool = None
    
    @classmethod
    def initialize(cls):
        """初始化连接池"""
        if cls._connection_pool is None:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
    
    @classmethod
    def get_connection(cls):
        """获取数据库连接"""
        if cls._connection_pool is None:
            cls.initialize()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, connection):
        """归还连接到池"""
        cls._connection_pool.putconn(connection)
    
    @classmethod
    def close_all_connections(cls):
        """关闭所有连接"""
        if cls._connection_pool:
            cls._connection_pool.closeall()

def get_db():
    """获取数据库连接的辅助函数"""
    return Database.get_connection()

def close_db(conn):
    """关闭数据库连接的辅助函数"""
    Database.return_connection(conn)
