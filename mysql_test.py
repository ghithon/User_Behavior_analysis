import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB

def test_mysql_connection():
    try:
        # 建立连接
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT,
            database=MYSQL_DB
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"✅ MySQL连接成功！数据库版本：{version[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ 连接失败，错误信息：{e}")

if __name__ == "__main__":
    test_mysql_connection()
