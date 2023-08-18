import random

from app.GetConn.DBUtil import get_conn, close_conn


# 判断是否输入用户名
def is_null(username, password):
    if username == '' or password == '':
        return True
    else:
        return False


# 判断是否用户和密码正常
def is_existed(username, password):
    # sql查询用户密码是否正确
    sql = "SELECT * FROM user WHERE username ='%s' and password ='%s'" % (username, password)
    conn, cur = get_conn()
    # 执行sql语句
    cur.execute(sql)
    # 获得查询结果返回一个元组
    result = cur.fetchall()
    close_conn(conn, cur)
    if len(result) == 0:
        return False
    else:
        return True


# 判断是否存在用户
def exist_user(username):
    sql = "SELECT * FROM user WHERE username ='%s'" % username
    conn, cur = get_conn()
    cur.execute(sql)
    result = cur.fetchall()
    close_conn(conn, cur)
    if len(result) == 0:
        return False
    else:
        return True


# 加入新用户
def add_user(username, password):
    # sql commands
    uid = random.randint(2, 100)
    sql = "INSERT INTO user(Uid,username, password) VALUES ('%d','%s','%s')" % (uid, username, password)
    conn, cursor = get_conn()
    cursor.execute(sql)
    # commit
    conn.commit()  # 对数据库内容有改变，需要commit()
    close_conn(conn, cursor)
