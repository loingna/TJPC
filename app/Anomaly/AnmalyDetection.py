# -*- coding = utf-8 -*-
# @Time : 2023/6/19
# @author : dsy
# @Software: PyCharm
"""
主要功能：
 (1)实现对每个操作的异常检测
"""
import os
import random
import time

from app.DataInteraction.IPFSAPI import get_all_node_ip
from app.Logs.pc_all_event_log import save_detect_all_event


# 异常检测
def operation_detection(data):
    main_ip = '10.25.9.11'
    Alarmlevel = 0
    Alarmdetail = '安全'
    newdata = str(data) + '\n'
    # 查询节点的在线状态，如果离线就发出异常告警
    # 后续可以在此添加更多的状态检测
    get_ip_num = get_all_node_ip(main_ip)
    if len(get_ip_num) != 12:
        Alarmlevel = 1
        Alarmdetail = '有节点离线！！！'
    # 对每次操作的语句和输入进行比较判断是否有恶意操作例如sql注入等
    # 判断是否有sql注入
    # 同样，如果有其他的检测可以在此添加
    with open(r'E:\TJPC\static\xssPayloads.txt', 'r') as f:
        xss = f.readlines()
    if newdata in xss:
        Alarmlevel = 2
        Alarmdetail = '危险！！发现潜在的xss攻击'
    with open(r'E:\TJPC\static\sql.txt', 'r') as f:
        sqlinject = f.readlines()
    if newdata in sqlinject:
        Alarmlevel = 3
        Alarmdetail = '危险！！发现潜在的sql注入行为'
    pc_event_information = {'detect_name': "状态自检", 'detect_item': "节点状态，恶意操作", 'detect_statement': str(data),
                            'Alarmlevel': str(Alarmlevel), 'Alarmdetail': str(Alarmdetail)}
    save_detect_all_event(pc_event_information)
    return Alarmlevel, Alarmdetail


# 应急响应
def Clear_Alarm(Alarmdetail):
    # 在这里实现响应的处理 例如删除指定的一个文件
    directory = r"E:\TJPC\testfile"  # 指定目录后面换成存放数据库的地方
    if not os.path.exists(directory):
        print(f"目录 '{directory}' 不存在")
        return
    files = os.listdir(directory)
    if not files:
        print(f"目录 '{directory}' 下没有文件可供删除")
        return
    file_to_delete = random.choice(files)
    file_path = os.path.join(directory, file_to_delete)
    try:
        os.remove(file_path)
        print(f"成功删除文件 '{file_to_delete}'")
    except OSError as e:
        print(f"删除文件 '{file_to_delete}' 时发生错误: {e}")
    return '处理结束'


# 应急自毁
def killself():
    # 实现应急自毁
    # 下面的是删除目录下的所有文件
    directory = r"E:\TJPC\testfile"
    file_list = os.listdir(directory)
    # 随机打乱文件列表顺序
    random.shuffle(file_list)
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            print(f"正在删除文件: {file_path}")
            os.remove(file_path)
        else:
            print(f"跳过目录: {file_path}")


if __name__ == '__main__':
    start = time.time()
    killself()
    time.sleep(4.5)
    endtime = time.time()
    print(f'应急自毁删除关键数据测试时间：%s秒' % (endtime - start))
    # a, s = operation_detection(datas)
    # print(a)
    # print(s)
