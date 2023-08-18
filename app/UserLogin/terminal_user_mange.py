# -*- coding = utf-8 -*-
# @Time : 2023/6/1
# @author : dsy
# @Software: PyCharm
"""
主要功能：
 (1)实现终端用户的添加、查看等操作
 (2)发送方发送的指令的交互操作
"""
import random
# 连接数据库的操作
from socket import *

from app.DataInteraction.IPFSAPI import get_all_node_ip
from app.GetConn.DBUtil import get_conn, close_conn
# 功能运行详细记录
from app.Logs import pc_all_event_log


# 添加新用户
# 输入：终端用户名、终端用户手机型号、终端用户的操作权限和IP地址
# 输出：终端用户的唯一id
def add_Terminal_user(username, model, power, userip):
    # 随机生成一个五位数的id
    uid = random.randint(10000, 19999)
    # 写入sql语句
    sql = "INSERT INTO termialusers(id,username,Terminal_model,User_permissions,user_ip) VALUES ('%d','%s','%s','%d'," \
          "'%s')" % (uid, username, model, int(power), str(userip))
    conn, cursor = get_conn()
    cursor.execute(sql)
    # commit
    conn.commit()  # 对数据库内容有改变，需要commit()
    close_conn(conn, cursor)
    print('---用户插入成功----')
    return uid


# 查看所有用户
# 输入：无
# 输出：所有终端用户的信息
def show_all_Terminal_user():
    # 查询所有用户信息的sql语句
    sql = "select * from termialusers"
    conn, cursor = get_conn()
    cursor.execute(sql)
    result = cursor.fetchall()
    close_conn(conn, cursor)
    # 返回所有用户的列表
    return result


# 根据id查询用户信息
# 输入：终端用户的id
# 输出：指定id终端用户的信息
def check_id_Terminal_user(ids):
    sql = "select * from termialusers where id= %d " % int(ids)
    conn, cursor = get_conn()
    cursor.execute(sql)
    result = cursor.fetchall()
    close_conn(conn, cursor)
    return result


# 根据id修改终端用户信息
# 输入：需要修改的用户id以及基本信息（终端用户名、终端用户手机型号、终端用户的操作权限和ip）
# 输出：无(可以输出true以判断是否插入成功，方便起见不报错就说明成功了)
def update_terminal_user(username, model, power, ids, userip):
    sql = "update termialusers set username='%s',Terminal_model='%s',User_permissions='%s',user_ip='%s' where id= %d " % (
        username, model, power, str(userip), int(ids))
    conn, cursor = get_conn()
    cursor.execute(sql)
    conn.commit()
    close_conn(conn, cursor)


# 根据id删除指定用户
# 输入：指定的id
# 输出：无（同上）
def delete_terminal_user(ids):
    sql = "delete from termialusers where id= %d " % int(ids)
    conn, cursor = get_conn()
    cursor.execute(sql)
    conn.commit()
    close_conn(conn, cursor)


# 设置用户权限的函数
def set_jurisdiction():
    return '1'


# 处理注册操作，传入指令
# 输入：用户发过来的注册信息，其中格式为：1#register#username#model#ip
# 输出：返回注册成功的id
def Process_Registration(chooseoperate, ip):
    # 获得用户的注册数据
    username = chooseoperate[2]
    Terminal_model = chooseoperate[3]
    power = int(set_jurisdiction())
    userip = str(ip)
    # 添加到终端用户数据库中
    ids = add_Terminal_user(username, Terminal_model, power, userip)
    return ids


def Get_id_all_file(userid, userpower):
    sql = "select * from filedatahash where target_id= %d " % int(userid)
    if int(userpower) == 1:
        conn, cursor = get_conn()
        cursor.execute(sql)
        result = cursor.fetchall()  # 是包含所有发送给指定用户的数据
        close_conn(conn, cursor)
        return result
    else:
        return None


# 处理发来的指令
# 输入：用户发过来的指令信息，其中格式为：num#operation#detaildata，其中第一个num是表示哪一种节点，第二个operating是要执行什么操作，最后一个是具体的操作数据
# 输出：根据具体的情况返回结果
def Processing_Instructions(c_socket, c_addr, chooseoperate, CLIENT):
    # 终端用户
    if chooseoperate[0] == '1':
        # 注册操作
        if chooseoperate[1] == 'register':
            # 具体的操作
            uid = Process_Registration(chooseoperate, c_addr[0])
            # 返回权限和标识信息给用户
            power = set_jurisdiction() + '#' + str(uid)
            # 发送权限信息和标识给终端用户
            c_socket.send(power.encode())
            c_socket.send('finish'.encode())
            # 将功能运行详细操作记录下来
            pc_event_information = {'node_name': str(chooseoperate[2]), 'node_model': str(chooseoperate[3]),
                                    'node_ip': str(c_addr[0]), 'node_port': str(c_addr[1]), 'node_operation': '在线注册',
                                    'node_respones': str(chooseoperate[2]) + '成功注册'}
            pc_all_event_log.save_function_all_event(pc_event_information)
            # 处理结束 释放连接
            c_socket.close()
            print(str(c_addr) + '断开连接')
            # CLIENT保存有当前连接的情况，注册操作完成以后就不需要再继续连接，所以将其移除
            CLIENT.remove((c_socket, c_addr))
        # 获取当前可供连接的地址
        elif chooseoperate[1] == 'get_connection':
            # 随机一个连接地址
            mian_ip = '10.25.9.11'
            # 根据连接地址获取当前局域网中的在线ip地址信息
            all_node = get_all_node_ip(mian_ip)
            re_data = '#'.join(all_node)  # 转为以＃分割的字符串
            c_socket.send(re_data.encode())  # 发送给链接方
            c_socket.send('finish'.encode())
            # 将功能运行详细操作记录下来
            get_data = check_id_Terminal_user(chooseoperate[2])[0]
            print(get_data)
            pc_event_information = {'node_name': str(get_data[1]), 'node_model': str(get_data[2]),
                                    'node_ip': str(c_addr[0]), 'node_port': str(c_addr[1]),
                                    'node_operation': '在线查询当前可供连接的ip地址',
                                    'node_respones': '成功返回对应的ip给链接方'}
            pc_all_event_log.save_function_all_event(pc_event_information)
            # 处理结束 释放连接
            c_socket.close()
            print(str(c_addr) + '断开连接')
            CLIENT.remove((c_socket, c_addr))
        # 查看当前可供连接的用户信息
        elif chooseoperate[1] == 'get_other_user':
            # 获得当前所有的用户
            all_user = show_all_Terminal_user()
            new_list = []
            now_id = chooseoperate[2]  # 解码出发来用户的信息id
            for user in all_user:
                # 去除自己的id对应的信息
                if str(user[0]) != str(now_id):
                    # 将其他设备的id和名称发送给终端以'id#name'形式返回
                    new_list.append(str(user[0]) + '#' + str(user[1]) + '#' + str(user[4]))
            # 将获取的信息发送出去
            c_socket.send('#'.join(new_list).encode())
            c_socket.send('finish'.encode())
            # 将功能运行详细操作记录下来
            get_data = check_id_Terminal_user(now_id)[0]
            pc_event_information = {'node_name': str(get_data[1]), 'node_model': str(get_data[2]),
                                    'node_ip': str(c_addr[0]), 'node_port': str(c_addr[1]),
                                    'node_operation': '在线查询当前可供发送的用户',
                                    'node_respones': '成功返回对应的用户给链接方'}
            pc_all_event_log.save_function_all_event(pc_event_information)
            # 处理结束 释放连接
            c_socket.close()
            print(str(c_addr) + '断开连接')
            CLIENT.remove((c_socket, c_addr))
        # 获得属于指定id的文件已经大小和datahash的信息
        elif chooseoperate[1] == 'get_filehash':
            user_id = chooseoperate[2]
            user_power = chooseoperate[3]
            get_file = Get_id_all_file(user_id, user_power)
            all_file = []
            for files in get_file:
                all_file.append(str(files[2]) + '#' + str(files[3] + '#' + str(files[4])))
            # 将获取的信息发送出去
            c_socket.send('#'.join(all_file).encode())
            # 将功能运行详细操作记录下来
            get_data = check_id_Terminal_user(user_id)[0]
            pc_event_information = {'node_name': str(get_data[1]), 'node_model': str(get_data[2]),
                                    'node_ip': str(c_addr[0]), 'node_port': str(c_addr[1]),
                                    'node_operation': '在线查询获得自己的文件',
                                    'node_respones': '成功返回对应的文件给链接方'}
            pc_all_event_log.save_function_all_event(pc_event_information)
            # 处理结束 释放连接
            c_socket.close()
            print(str(c_addr) + '断开连接')
            CLIENT.remove((c_socket, c_addr))

    # 星载节点
    elif chooseoperate[0] == '2':
        pass
    # 地面节点
    elif chooseoperate[0] == '3':
        pass


if __name__ == '__main__':
    # socket线程的申请
    IP = '10.25.2.177'
    # 端口号
    PORT = 8900
    clint = []
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((IP, PORT))
    sock.listen(10)
    try:
        # lock.acquire()
        print('---等待用户连接----')
        # 无连接的情况阻塞
        connection, addr = sock.accept()
        print(f"接收到新用户，其地址为:%s " % str(addr))
        rawdata = connection.recv(512)
        revicedata = rawdata.decode()
        chooseoperate = revicedata.split('#')
        print(chooseoperate)
        clint.append((connection, addr))
        Processing_Instructions(connection, addr, chooseoperate, clint)
        sock.close()
    except BlockingIOError:
        pass
    # ressult = Get_id_all_file(14378, 1)
    # all_file=[]
    # for nums in ressult:
    #     all_file.append(str(nums[2])+'#'+str(nums[3]+'#'+str(nums[4])))
    # print('#'.join(all_file))
