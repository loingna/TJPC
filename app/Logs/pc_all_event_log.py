# -*- coding = utf-8 -*-
# @Time : 2023/5/6
# @author : dsy
# @Software: PyCharm
"""
主要功能：
 (1)日志记录，记录所有的操作写入的数据库中
 (2)日志的查询功能
"""
from app.GetConn.DBUtil import get_conn, close_conn
import datetime


# 记录所有用户的操作
def save_to_pc_all_event(pc_event_information):
    conn, cur = get_conn()
    pc_event_information['event_happen_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # all是以列表形式返回所有查询结果
    args = (pc_event_information['pc_event'], pc_event_information['detail_description'],
            pc_event_information['event_happen_time'])
    sql = 'insert into pc_all_event(pc_event,detail_description,event_happen_time)values(%s,%s,%s)'
    cur.execute(sql, args)
    conn.commit()
    print('插入pc_user_all_event成功')
    close_conn(conn, cur)


# 记录功能运行的操作
def save_function_all_event(pc_event_information):
    conn, cur = get_conn()
    pc_event_information['event_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # all是以列表形式返回所有查询结果
    args = (pc_event_information['node_name'], pc_event_information['node_model'], pc_event_information['node_ip'],
            pc_event_information['node_port'],
            pc_event_information['node_operation'], pc_event_information['node_respones'],
            pc_event_information['event_time'])
    sql = 'insert into functional_operation(node_name,node_model,node_ip,node_port,node_operation,node_respones,' \
          'event_time)values(%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, args)
    conn.commit()
    print('插入pc_function_all_event成功')
    close_conn(conn, cur)


# 记录状态自检的操作
def save_detect_all_event(pc_event_information):
    conn, cur = get_conn()
    pc_event_information['event_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # all是以列表形式返回所有查询结果
    args = (
        pc_event_information['detect_name'], pc_event_information['detect_item'],
        pc_event_information['detect_statement'], pc_event_information['Alarmlevel'],
        pc_event_information['Alarmdetail'], pc_event_information['event_time'])
    sql = 'insert into detect_history(detect_name,detect_item,detect_statement,Alarmlevel,Alarmdetail,' \
          'event_time)values(%s,%s,%s,%s,%s,%s) '
    cur.execute(sql, args)
    conn.commit()
    print('插入pc_detect_all_event成功')
    close_conn(conn, cur)


# 所有用户操作历史信息查询展示
def pc_all_event():
    conn, cur = get_conn()
    sql1 = "select event_happen_time from pc_all_event"
    cur.execute(sql1)
    sql_get_all = cur.fetchall()
    # print(sql_get_all[0])
    num = len(sql_get_all)
    # 数据库数据只保留2000条，多余的删除
    if num > 2000:
        for i in sql_get_all[2000:]:
            arg = i[2]
            sql2 = 'delete from pc_all_event where event_happen_time=%s'
            cur.execute(sql2, arg)
            conn.commit()
        print('发现所有路由器状态历史信息数据库数据多于2000条，多余的删除')
    # 查询信息，all是以列表形式返回所有查询结果
    sql3 = "select * from pc_all_event"
    cur.execute(sql3)
    pc_all_events = list(cur.fetchall())
    pc_all_events.reverse()
    cur.close()
    conn.close()
    return pc_all_events


# 查询所有的功能操作日志
def function_all_event():
    conn, cur = get_conn()
    sql1 = "select event_time from functional_operation"
    cur.execute(sql1)
    sql_get_all = cur.fetchall()
    # print(sql_get_all[0])
    num = len(sql_get_all)
    # 数据库数据只保留2000条，多余的删除
    if num > 2000:
        for i in sql_get_all[2000:]:
            arg = i[2]
            sql2 = 'delete from functional_operation where event_time=%s'
            cur.execute(sql2, arg)
            conn.commit()
        print('发现所有路由器状态历史信息数据库数据多于2000条，多余的删除')
    # 查询信息，all是以列表形式返回所有查询结果
    sql3 = "select * from functional_operation"
    cur.execute(sql3)
    function_all_events = list(cur.fetchall())
    function_all_events.reverse()
    cur.close()
    conn.close()
    return function_all_events


# 查询所有的状态自检信息
def detect_all_event():
    conn, cur = get_conn()
    sql1 = "select event_time from detect_history"
    cur.execute(sql1)
    sql_get_all = cur.fetchall()
    # print(sql_get_all[0])
    num = len(sql_get_all)
    # 数据库数据只保留2000条，多余的删除
    if num > 2000:
        for i in sql_get_all[2000:]:
            arg = i[2]
            sql2 = 'delete from detect_history where event_time=%s'
            cur.execute(sql2, arg)
            conn.commit()
        print('发现所有路由器状态历史信息数据库数据多于2000条，多余的删除')
    # 查询信息，all是以列表形式返回所有查询结果
    sql3 = "select * from detect_history"
    cur.execute(sql3)
    detect_all_events = list(cur.fetchall())
    detect_all_events.reverse()
    cur.close()
    conn.close()
    return detect_all_events
