# TCP 服务端端程序 server.py
# 导入socket库
import threading
from socket import *

from app.UserLogin.terminal_user_mange import add_Terminal_user

CLIENT = []
sock = socket(AF_INET, SOCK_STREAM)
# ip
IP = '10.25.3.148'
# 端口号
PORT = 8900
def SetServer():
    # 主机地址为0.0.0.0，表示绑定本机所有网络接口ip地址
    # 等待客户端来连接
    # 接收客户端连接，无客户端连接时，就处于睡眠状态
    print('---wait---')
    dataSocket, addr = sock.accept()
    print('接受一个客户端连接：', addr)
    CLIENT.append((dataSocket, addr))


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

# 接收数据函数
def receive():
    print('----接收数据线程-----')
    flag=True
    while flag:
        if len(CLIENT) > 0:
            print('---有用户连接-----')
            # lock.acquire()
            for c_socket, c_addr in CLIENT:
                print('----接收数据----')
                try:
                    rawdata = c_socket.recv(1024)
                    revicedata = rawdata.decode()
                    chooseoperate = revicedata.split('#')
                    print(chooseoperate)
                    # 终端用户
                    if chooseoperate[0] == '1':
                        # 注册操作
                        if chooseoperate[1] == 'register':
                            username = chooseoperate[2]
                            Terminal_model = chooseoperate[3]
                            # 添加到终端用户数据库中
                            add_Terminal_user(username, Terminal_model)
                except (BlockingIOError, ConnectionResetError):
                    pass
            flag=False
            # lock.release()
    print('---接收结束----')

def SendData(dataSocket, sendmessage):
    # 发送的数据类型必须是bytes，所以要编码
    dataSocket.send(sendmessage.encode())


def CloseSocket(dataSocket, listenSocket):
    dataSocket.close()
    listenSocket.close()


if __name__ == '__main__':
    sock.bind((IP, PORT))
    sock.listen(10)
    print(f'服务端启动成功，在{PORT}端口等待客户端连接...')
    connect_run = threading.Thread(target=SetServer)  # 连接客户端线程
    receive_run = threading.Thread(target=receive)  # 接收数据线程
    connect_run.start()  # 启动连接客户端线程
    receive_run.start()  # 启动接收数据线程
    print('线程启动成功')
    while True:
        pass
