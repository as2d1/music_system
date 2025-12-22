import psycopg2
from config import Config

def init_db():
    """
    初始化数据库表结构
    注意：请确保数据库(Config.DB_NAME)已经存在
    """
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
            
        conn.commit()
        cursor.close()
        conn.close()
        print("数据库表结构初始化成功！")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        print("请检查 config.py 中的数据库配置，并确保数据库已创建。")

if __name__ == '__main__':
    init_db()
