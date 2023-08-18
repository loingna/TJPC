import threading
from socket import *
from flask import Flask, request, render_template, redirect, url_for

from app.Anomaly.AnmalyDetection import operation_detection, Clear_Alarm, killself
from app.DataInteraction.Changejosn import get_node_josn  # 实现拓扑节点的json文件的修改
from app.DataInteraction.Client import *  # 客户端通信的一些操作
from app.DataInteraction.IPFSAPI import get_all_node_ip, get_Stellite_node_data, get_ip_node, \
    get_allground_node_ip, get_Ground_node_data  # IPFS节点的信息获取
from app.UserLogin.logincheck import *  # 管理员登录时的验证操作
from app.UserLogin.Sqloperation import *  # 登录等操作用到的sql数据库操作
from app.UserLogin.terminal_user_mange import *  # 终端节点的管理操作
from app.Logs import pc_all_event_log  # 所有操作日志记录操作
from flask_socketio import SocketIO
from flask_paginate import Pagination, get_page_parameter  # 实现一个页面展示多条数据的库

"""
（1）支持在线注册、管理普通用户节点账户；
（2）可向星载节点和地面节点下达控制命令；
（3）支持在线查询、统计、展示设备的状态信息； //统计  实时的节点状态（在不在线）
（4）具有各类操作日志记录、查询统计功能；  //查询统计功能 针对日志的查询统计
 (5)
"""
# 网页启动的配置信息，template_folder网页启动目录，所有的html网页都在该目录下。static_folder和static_url_path存放静态文件的地方
app = Flask(__name__, template_folder=r'.\templates', static_folder=r'.\static', static_url_path='/static')
# socket进程通信的线程配置
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# socket线程的申请
sock = socket(AF_INET, SOCK_STREAM)
CLIENT = []  # 存储当前有多少通信线程
Flag = False  # 线程退出的flag
Global_Users = 'test'  # 申请一个全局用户名变量，用于保存当前管理员登录的信息(后面扩展可以写成User类)
# socket线程的ip 换成本机
Ip = '10.25.2.177'
# 端口号
Port = 8900
# 每次通信的最大读取字节数
Buflen = 1024
# 线程锁，防止出现写后写，读后写等资源冲突的情况
lock = threading.Lock()
Alarmlevel = 0
Alarmdetail = '安全'


# 连接线程，用于实现连接操作
def connect():
    print('---连接线程----')
    # 持续接受用户连接
    while True:
        global Flag
        if Flag:
            break
        try:
            # lock.acquire()
            print('---等待连接----')
            # 无连接的情况阻塞
            connections, addrs = sock.accept()
            CLIENT.append((connections, addrs))
            print(f"接收到新用户，其地址为:%s 目前有%d个连接" % (addrs, len(CLIENT)))
        except BlockingIOError:
            pass
        # finally:
        #     lock.release()
    print('----资源释放-----')


# 处理数据函数,用于处理连接之后的交互
def receive():
    print('----处理数据线程-----')
    while True:
        global Buflen
        global Flag, Alarmlevel, Alarmdetail
        if Flag:
            break
        if len(CLIENT) > 0:
            print('---有用户连接-----')
            # lock.acquire()
            for c_socket, c_addr in CLIENT:
                print('----处理数据----')
                try:
                    # 读取链接方发送的数据
                    rawdatas = c_socket.recv(Buflen)
                    # 发送到都是以字节流的形式接受，所有需要转为字符串
                    revicedatas = rawdatas.decode()
                    # 发送的指令是以‘#’为分割的多个指令，所以需要分割
                    chooseoperates = revicedatas.split('#')
                    for datas in chooseoperates:
                        Alarmlevel, Alarmdetail = operation_detection(datas)
                    if Alarmlevel == 0 or Alarmlevel == 1:
                        # 调用处理指令的函数进行处理
                        Processing_Instructions(c_socket, c_addr, chooseoperates, CLIENT)
                    else:
                        print('存在安全行为，拒绝访问')
                        c_socket.close()
                        print(str(c_addr) + '断开连接')
                        # CLIENT保存有当前连接的情况，注册操作完成以后就不需要再继续连接，所以将其移除
                        CLIENT.remove((c_socket, c_addr))
                except (BlockingIOError, ConnectionResetError):
                    print('接受线程 error')
                    pass
            # lock.release()
    print('---接收结束-----')


# 初始登录界面
@app.route('/')  # 必须加上路由，否则访问和函数没有关联,当访问到127.0.0.1：5000/，执行函数
def start():
    return render_template('login.html')  # 跳转哪一个界面


# 登录路由
@app.route("/login", methods=['POST', 'GET'])
def login():
    global Global_Users
    username = request.form.get('username')  # 接收form表单传参
    password = request.form.get('password')
    if request.method == 'POST':
        # 查询是否有该用户
        if is_null(username, password):
            login_massage = "温馨提示：账号和密码是必填"
            return render_template('login.html', message=login_massage)
        # 判断账号密码是否正确 正确就跳转到主界面
        elif is_existed(username, password):
            Global_Users = username
            # 记录用户登录事件
            pc_event_information = {'pc_event': '用户登录', 'detail_description': Global_Users + '成功登录PC管理系统'}
            pc_all_event_log.save_to_pc_all_event(pc_event_information)
            return redirect(url_for('index'))
        elif exist_user(username):
            login_massage = "温馨提示：密码错误，请输入正确密码"
            return render_template('login.html', message=login_massage)
        else:
            login_massage = "温馨提示：不存在该用户，请先注册"
            return render_template('login.html', message=login_massage)
    return render_template('login.html')


# 注册地址
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果请求为post
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        if repassword == password:
            if is_null(username, password):
                login_massage = "温馨提示：账号和密码是必填"
                return render_template('register.html', message=login_massage)
            elif exist_user(username):
                login_massage = "温馨提示：用户已存在，请直接登录"
                # return redirect(url_for('user_login'))
                return render_template('register.html', message=login_massage)
            else:
                add_user(username, password)
                return render_template('login.html', username=username)
    # 请求为get
    return render_template('register.html')


# 主界面
@app.route("/index")
def index():
    # 获取用户名
    global Global_Users, Ip, Port, Alarmlevel, Alarmdetail
    # 启动线程处理数据
    sock.bind((Ip, Port))
    sock.listen(10)  # 最多同时连接10个用户
    print(f'服务端启动成功，在{Port}端口等待客户端连接...')
    connect_run = threading.Thread(target=connect)  # 连接客户端线程
    receive_run = threading.Thread(target=receive)  # 接收数据线程
    connect_run.start()  # 启动连接客户端线程
    receive_run.start()  # 启动接收数据线程
    print('线程启动成功')

    return render_template('index.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail)


# 管理节点查看个人信息
@app.route("/personal_information")
def personal_information():
    global Global_Users, Alarmlevel, Alarmdetail
    userdata = getUserdata(Global_Users)
    # 记录事件
    pc_event_information = {'pc_event': '查询信息', 'detail_description': Global_Users + '查看个人信息'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('personal_information.html', username=Global_Users, userdata=userdata, num=Alarmlevel,
                           Alarmdetail=Alarmdetail)


# 修改管理界面密码
@app.route("/generate_password", methods=['GET', 'POST'])
def generate_password():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    if request.method == 'POST':
        newpassword = request.form.get('new_password')
        Alarmlevel, Alarmdetail = operation_detection(newpassword)
        if Alarmlevel > 1:
            print('存在危险行为')
            return redirect(url_for('Alarm_show'))
        # 更新数据库--更新密码
        result = updata_password(Global_Users, newpassword)
        if result:
            # 记录事件
            pc_event_information = {'pc_event': '密码修改', 'detail_description': Global_Users + '修改密码'}
            pc_all_event_log.save_to_pc_all_event(pc_event_information)
            message = '修改密码成功'
    return render_template('generate_password.html', username=Global_Users, message=message, num=Alarmlevel,
                           Alarmdetail=Alarmdetail)


# 管理终端用户界面
@app.route("/manage_terminal_user")
def manage_terminal_user():
    global Global_Users, Alarmlevel, Alarmdetail
    # 查询所有的用户信息
    userdata = show_all_Terminal_user()
    pc_event_information = {'pc_event': '终端用户数据查询',
                            'detail_description': Global_Users + '查询了终端用户表'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('manage_terminal_user.html', username=Global_Users, userdata=userdata, num=Alarmlevel,
                           Alarmdetail=Alarmdetail)


# 添加用户
@app.route("/submit_insert_user")
def submit_insert_user():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    return render_template('submit_insert_user.html', username=Global_Users, message=message, num=Alarmlevel,
                           Alarmdetail=Alarmdetail)


# 手动添加终端用户界面
@app.route("/insert_user", methods=['GET', 'POST'])
def insert_user():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    if request.method == 'POST':
        username = request.form.get('Terminal_username')
        modules = request.form.get('Terminal_module')
        power = request.form.get('Terminal_power')
        userip = request.form.get('Terminal_ip')
        checks = [username, modules, power, userip]
        for data in checks:
            Alarmlevel, Alarmdetail = operation_detection(data)
        if Alarmlevel > 1:
            print('存在危险行为')
            return redirect(url_for('Alarm_show'))
        # 写入数据库
        uids = add_Terminal_user(username, modules, power, userip)
        if uids:
            pc_event_information = {'pc_event': '终端用户主动添加',
                                    'detail_description': Global_Users + '添加终端用户' + str(username)}
            pc_all_event_log.save_to_pc_all_event(pc_event_information)
            message = "终端用户添加成功！！！"
    return render_template('submit_insert_user.html', username=Global_Users, message=message, num=Alarmlevel,
                           Alarmdetail=Alarmdetail)


# 修改终端用户的信息
@app.route("/submit_update_user")
def submit_update_user():
    # 获取需要修改的用户信息
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    ids = request.args.get("id")
    # 获取指定用户的数据
    terminal_result = check_id_Terminal_user(ids)
    return render_template('submit_update_user.html', username=Global_Users, terminal_result=terminal_result[0],
                           num=Alarmlevel,
                           Alarmdetail=Alarmdetail, message=message)


# 更新终端用户的信息
@app.route("/update_user", methods=['GET', 'POST'])
def update_user():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    userdatas = []
    if request.method == 'POST':
        # 获得表单数据
        username = request.form.get('Terminal_username')
        modules = request.form.get('Terminal_module')
        power = request.form.get('Terminal_power')
        ids = request.form.get('Terminal_id')
        userip = request.form.get('Terminal_ip')
        userdatas = [username, modules, power, ids, userip]
        # 异常检测
        for data in userdatas:
            Alarmlevel, Alarmdetail = operation_detection(data)
        if Alarmlevel > 1:
            print('存在危险行为')
            return redirect(url_for('Alarm_show'))
        # 修改终端用户的信息
        update_terminal_user(username, modules, power, ids, userip)
        pc_event_information = {'pc_event': '终端用户信息修改',
                                'detail_description': Global_Users + '修改' + str(ids) + '的信息'}
        pc_all_event_log.save_to_pc_all_event(pc_event_information)
        message = "终端用户信息修改成功！！！"
    return render_template('submit_update_user.html', username=Global_Users, num=Alarmlevel,
                           Alarmdetail=Alarmdetail, message=message, terminal_result=userdatas)


# 删除指定用户
@app.route("/delete_user")
def delete_user():
    global Global_Users
    # 获取需要删除的用户id
    ids = request.args.get("id")
    # 删除用户
    delete_terminal_user(ids)
    pc_event_information = {'pc_event': '终端用户信息删除',
                            'detail_description': Global_Users + '删除' + str(ids) + '的信息'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    # 重定向到管理界面
    return redirect(url_for('manage_terminal_user'))


# 在线生成指令并发送
@app.route('/inline_command', methods=['GET', 'POST'])
def inline_command():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    onboard_node = 'onboard_node'
    ground_node = 'ground_node'  # 地面节点
    all_node = 'onboard_node ground_node'
    who_get = ''
    if request.method == 'POST':
        # 获取表单的所有选项对应的值
        command = request.form
        command = command.to_dict()
        inline_commands = ''
        for k, v in command.items():
            inline_commands = inline_commands + v + ' '
        # 该指令获得前端value里面的值
        inline_commands = inline_commands.strip()
        print('在线指令发送：' + inline_commands)
        # 判断发送给哪个节点并将指令提取处理 然后发送给指定的节点
        if all_node in inline_commands:  # 同时发给地面和星载
            inline_commands = inline_commands.replace(all_node, '')  # 去掉接收者的信息 只保留指令信息
            who_get = all_node
            # 通过socket发送给指定节点
            message1 = '星载节点：' + Send_onboard_node(inline_commands)
            message2 = '\n地面节点' + Send_ground_node(inline_commands)
            message = message1 + message2
        elif onboard_node in inline_commands:  # 只发给星载节点
            inline_commands = inline_commands.replace(onboard_node, '')
            who_get = onboard_node
            print('发送给星载节点')
            # 将指令发送给星载节点
            message = Send_onboard_node(inline_commands)
        elif ground_node in inline_commands:  # 只发给地面节点
            inline_commands = inline_commands.replace(ground_node, '')
            who_get = ground_node
            print('发送给地面节点')
            # 将指令发送给地面节点
            message = Send_ground_node(inline_commands)
        else:
            print('error')
            message = '请选择要发送的节点'
        pc_event_information = {'pc_event': '在线指令发送',
                                'detail_description': inline_commands + '发送到' + who_get}
        pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('inline_command.html', username=Global_Users, num=Alarmlevel,
                           Alarmdetail=Alarmdetail, message=message)


# 展示星载节点的信息
@app.route('/manage_Satellite_borne')
def manage_Satellite_borne():
    global Global_Users, Alarmlevel, Alarmdetail
    main_ip = '10.25.9.1'
    all_node_ip = get_all_node_ip(main_ip)
    all_node = get_Stellite_node_data(all_node_ip)
    pc_event_information = {'pc_event': '节点信息查询',
                            'detail_description': Global_Users + '查看了星载节点信息'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('manage_Satellite_borne.html', username=Global_Users, num=Alarmlevel,
                           Alarmdetail=Alarmdetail, all_node=len(all_node_ip), all_inline_node=len(all_node_ip),
                           onboard_node=all_node)


# 展示地面节点的信息
@app.route('/manage_Ground_nodes')
def manage_Ground_nodes():
    global Global_Users, Alarmlevel, Alarmdetail
    main_ip = '10.25.9.1'
    all_node_ip = get_allground_node_ip(main_ip)
    all_node = get_Ground_node_data(all_node_ip)
    pc_event_information = {'pc_event': '节点信息查询',
                            'detail_description': Global_Users + '查看了地面节点信息'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('manage_Ground_nodes.html', username=Global_Users, num=Alarmlevel,
                           Alarmdetail=Alarmdetail, all_node=len(all_node_ip), all_inline_node=len(all_node_ip),
                           onboard_node=all_node)


# 展示网络拓扑图
@app.route('/show_topology')
def show_topology():
    global Global_Users, Alarmlevel, Alarmdetail
    # 启动处理json文件的函数
    main_ip = '10.25.9.1'
    get_node_josn(main_ip)
    pc_event_information = {'pc_event': '网络拓扑查询',
                            'detail_description': Global_Users + '查看了网络拓扑状态'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('show_topology.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail)


# 展示具体节点的信息
@app.route('/show_node_detail')
def show_node_detail():
    global Global_Users, Alarmlevel, Alarmdetail
    # 从前端获得查看哪个节点的信息 ip+id
    ip = request.args.get("ip")
    dataIndex = int(request.args.get("dataIndex"))
    # 获得指定id的具体信息
    node_detail = get_ip_node(ip, dataIndex)
    pc_event_information = {'pc_event': '查看节点信息',
                            'detail_description': Global_Users + '查看了' + ip + '的状态信息'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    return render_template('show_node_detail.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail,
                           node_detail=node_detail)


# 展示用户操作内容日志
@app.route('/log_check')
def log_check(page=None):
    global Global_Users, Alarmlevel, Alarmdetail
    if not page:
        page = 1
    user_all_history_data = pc_all_event_log.pc_all_event()
    PER_PAGE = 10
    total = len(user_all_history_data)
    # 只展示前两百条记录
    if total > 200:
        router_all_history_data = user_all_history_data[:200]
        total = len(router_all_history_data)
    page = int(request.args.get(get_page_parameter(), 1))
    starts = (page - 1) * PER_PAGE
    end = starts + PER_PAGE
    paginate = Pagination(bs_version=4, page=page, total=total, per_page=PER_PAGE)
    every_user_history_data = user_all_history_data[starts:end]
    return render_template('log_check.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail,
                           paginate=paginate, every_user_history_data=every_user_history_data)


# 展示功能运行的操作
@app.route('/function_run_detail')
def function_run_detail(page=None):
    global Global_Users, Alarmlevel, Alarmdetail
    if not page:
        page = 1
    function_all_history_data = pc_all_event_log.function_all_event()
    PER_PAGE = 10
    total = len(function_all_history_data)
    # 只展示前两百条记录
    if total > 200:
        router_all_history_data = function_all_history_data[:200]
        total = len(router_all_history_data)
    page = int(request.args.get(get_page_parameter(), 1))
    starts = (page - 1) * PER_PAGE
    end = starts + PER_PAGE
    paginate = Pagination(bs_version=4, page=page, total=total, per_page=PER_PAGE)
    every_function_history_data = function_all_history_data[starts:end]
    return render_template('function_run_detail.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail,
                           paginate=paginate, every_function_history_data=every_function_history_data)


# 状态自检信息展示
@app.route('/router_history_data')
def router_history_data(page=None):
    global Global_Users, Alarmlevel, Alarmdetail
    if not page:
        page = 1
    detect_all_history_data = pc_all_event_log.detect_all_event()
    PER_PAGE = 10
    total = len(detect_all_history_data)
    # 只展示前两百条记录
    if total > 200:
        router_all_history_data = detect_all_history_data[:200]
        total = len(router_all_history_data)
    page = int(request.args.get(get_page_parameter(), 1))
    starts = (page - 1) * PER_PAGE
    end = starts + PER_PAGE
    paginate = Pagination(bs_version=4, page=page, total=total, per_page=PER_PAGE)
    every_detect_history_data = detect_all_history_data[starts:end]
    return render_template('router_history_data.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail,
                           paginate=paginate, detect_all_history_data=every_detect_history_data)


# 应急响应
@app.route('/Alarm_show')
def Alarm_show():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    return render_template('Alarm_show.html', username=Global_Users, num=Alarmlevel, Alarmlevel=Alarmlevel,
                           Alarmdetail=Alarmdetail, message=message)


@app.route('/clear_Alarm', methods=['GET', 'POST'])
def clear_Alarm():
    global Global_Users, Alarmlevel, Alarmdetail
    message = None
    if request.method == 'POST':
        # 获取表单的所有选项对应的值
        command = request.form
        command = command.to_dict()
        result = ''
        for k, v in command.items():
            result = result + v + ' '
        result = result.strip()
        if result == 'clear':
            Alarmlevel = 0
            Alarmdetail = '安全'
        elif result == 'alarmhandle':
            # 做出相应的保护措施
            message = Clear_Alarm(Alarmdetail)
            print(message)
            # 强制退出
            return redirect(url_for('login'))
        else:
            # 设备自毁
            killself()
    # 返回到主界面
    return render_template('index.html', username=Global_Users, num=Alarmlevel, Alarmdetail=Alarmdetail)


# 登出界面
@app.route('/logout')  # 登出
def logout():
    global Global_Users, Flag
    pc_event_information = {'pc_event': '用户登出', 'detail_description': Global_Users + '成功登出PC管理系统'}
    pc_all_event_log.save_to_pc_all_event(pc_event_information)
    # 强制关闭线程
    Flag = True
    for c_socket, c_addr in CLIENT:
        c_socket.close()
        CLIENT.remove((c_socket, c_addr))
    sock.close()
    return redirect(url_for('login'))


if __name__ == "__main__":
    socketio.run(
        app,
        host="127.0.0.1",
        port=8888,
        debug=True)
