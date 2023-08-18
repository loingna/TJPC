import pymysql


def get_conn():
    # 建立与mysql连接
    conn = pymysql.connect(host="localhost", user="root", password="root", db="tjtest", charset="utf8")
    # c创建游标A
    cursor = conn.cursor()
    return conn, cursor


def close_conn(conn, cursor):  # 关闭模块
    if cursor:
        cursor.close()
    if conn:
        conn.close()


if __name__ == "__main__":
    conn, cur = get_conn()
    sql1 = "select Uid,username from user where username='dsy' union select version(),database() # asdsad'"
    cur.execute(sql1)
    sql_get_all = cur.fetchall()
    print(sql_get_all)
    close_conn(conn, cur)
