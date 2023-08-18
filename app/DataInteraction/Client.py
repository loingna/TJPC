# TCP 客户端程序 client.py
from socket import socket, AF_INET, SOCK_STREAM

import ipfshttpclient

from app.DataInteraction.EnandDecrpty import EncryptDate
from app.DataInteraction.IPFSAPI import get_ip_node

IP = '10.25.3.148'
SERVER_PORT = 9111
BUFLEN = 512
Aes_key = "1111111111111111"
Aes_iv = "9999999999999999"


def GetClient(ip, port):
    # 实例化一个socket对象，指明协议
    dataSocket = socket(AF_INET, SOCK_STREAM)
    # 连接服务端socket
    dataSocket.connect((ip, port))
    print("连接成功！！！")
    return dataSocket


def CloseSocket(dataSocket):
    dataSocket.close()


# 发送指令给星载节点
def Send_onboard_node(data):
    print(data)
    data = data.strip()
    newcommend = data.split("  ")
    print(newcommend)
    if newcommend[0] == 'get_status':
        # 获取状态信息 连接IPFS端口获取
        clients = ipfshttpclient.connect(f'/ip4/10.25.9.%s/tcp/5001/http' % newcommend[1])
        # 获取仓库的大小
        base_repo = clients.repo.stat()
        proportion = '{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax'])) * 100) + '%'
        # 获取文件的数量
        numfile = str(len(clients.pin.ls(type='all')['Keys']))
        clients.close()
        message = f'ip:10.25.9.%s,port:4001,存储文件数量：%s,最大容量：10GB,占用比例：%s,是否在线：是' % (newcommend[1], numfile, proportion)
    else:
        # 接收方的id
        # ip = '10.25.9.' + newcommend[1]
        ip = '10.25.3.182'
        port = 8881
        try:
            dataSocket = GetClient(ip, port)
            print('成功建立')
            print('发送指令'+newcommend[0])
            encrpty_data = EncryptDate(Aes_key, Aes_iv).encrypt(newcommend[0])
            print('加密后指令：'+encrpty_data)
            dataSocket.send(encrpty_data.encode())
            dataSocket.send('finish'.encode())
            print('发送成功')
            datas = dataSocket.recv(512)  # 接收最多512个字节
            print('接收成功')
            message = datas.decode()
            dataSocket.close()
        except Exception as e:
            errors = '出错了：%s' % e
            message = errors
    return message


# 发送指令给地面节点
def Send_ground_node(data):
    print(data)
    data = data.strip()
    newcommend = data.split("  ")
    print(newcommend)
    if newcommend[0] == 'get_status':
        # 获取状态信息 连接IPFS端口获取
        clients = ipfshttpclient.connect(f'/ip4/10.25.9.%s/tcp/5001/http' % newcommend[1])
        # 获取仓库的大小
        base_repo = clients.repo.stat()
        proportion = '{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax'])) * 100) + '%'
        # 获取文件的数量
        numfile = str(len(clients.pin.ls(type='all')['Keys']))
        clients.close()
        message = f'ip:10.25.9.%s,port:4001,存储文件数量：%s,最大容量：10GB,占用比例：%s,是否在线：是' % (newcommend[1], numfile, proportion)
    else:
        # ip = '10.25.9.' + newcommend[1]
        ip = '10.25.3.182'
        port = 8881
        try:
            dataSocket = GetClient(ip, port)
            dataSocket.send(data)
            datas = dataSocket.recv(512)  # 接收最多 512个字节
            message = datas.decode()
            dataSocket.close()
        except Exception as e:
            errors = '出错了：%s' % e
            message = errors
        message = "success"
    return message


def GetData(dataSocket):
    # 定义一次从socket缓冲区最多读入512个字节数据
    BUFLEN = 512
    info = ''
    while True:
        # 尝试读取对方发送的消息
        # BUFLEN 指定从接收缓冲里最多读取多少字节
        recved = dataSocket.recv(BUFLEN)

        # 如果返回空bytes，表示对方关闭了连接
        # 退出循环，结束消息收发
        if not recved:
            break

        # 读取的学节数据是bytes类型，需要解码为字符串
        info = recved.decode()
        print(f'收到对方信息：{info}')
    return info


def SendData(dataSocket, sendmessage):
    # 发送的数据类型必须是bytes，所以要编码
    dataSocket.send(sendmessage.encode())


if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((IP, SERVER_PORT))
    sock.listen(10)
    try:
        # lock.acquire()
        print('---等待用户连接----')
        # 无连接的情况阻塞
        connection, addr = sock.accept()
        print(f"接收到新用户，其地址为:%s " % str(addr))
        print(addr[0])
        rawdata = connection.recv(512)
        revicedata = rawdata.decode()
        chooseoperate = revicedata.split('#')
        print(chooseoperate)
        connection.send('ok'.encode())
    except BlockingIOError:
        pass
    # messagess = Send_onboard_node('destruct  5')
    # print(messagess)
    # print(len(messagess))
