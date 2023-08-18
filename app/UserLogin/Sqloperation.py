from app.GetConn.DBUtil import get_conn, close_conn


# 根据用户名获取信息==查全表
def getUserdata(username):
    sql = "SELECT * FROM user WHERE username ='%s'" % username
    conn, cur = get_conn()
    cur.execute(sql)
    result = cur.fetchall()
    close_conn(conn, cur)
    # 返回一个保存有用户信息的列表
    userdata = [result[0][1], result[0][2]]
    return userdata


def updata_password(username, password):
    sql = "UPDATE user SET password='%s' WHERE username='%s'" % (password, username)
    if username is not None and password is not None:
        conn, cur = get_conn()
        cur.execute(sql)
        conn.commit()  # 对数据库内容有改变，需要commit()
        close_conn(conn, cur)
        return True
    else:
        return False


