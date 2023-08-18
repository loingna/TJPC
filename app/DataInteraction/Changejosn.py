# -*- coding = utf-8 -*-
# @Time : 2023/6/3
# @author : dsy
# @Software: PyCharm
"""
主要功能：
 (1)随机生成拓扑结构展示需要的json文件的信息
"""
import json
import random
import time
# 导入IPFS接口
from app.DataInteraction.IPFSAPI import get_all_node_ip, get_Stellite_node_data


# 获取所有节点的文件总和
# 输入：所有保存每一个IPFS节点的二维列表
# 输出：文件总和
def get_node_sum_file(all_nodes):
    result = 0
    for node in all_nodes:
        # 第七个是文件个数
        result = result + int(node[6])

    return result


# 随机生成一个连接状态（source,target）
# 输入：待连接的点和节点总数
# 输出：目标点 target
def get_node_links(source, max_num):
    # 随机生成一个点
    target = random.randint(1, max_num - 1)
    # 判断是否生成与source一样，一样就重新生成一个
    while int(source) == target:
        target = random.randint(1, max_num - 1)
    return target


# 实现拓扑结构需要的json文件格式并根据实际连接状况赋值
# 输入：待连接主ip节点
# 输出：无(直接对写入的文件进行操作了，用的时候直接读文件即可)
def get_node_josn(main_ip):
    # 获取节点信息
    all_node_ip = get_all_node_ip(main_ip)
    all_node = get_Stellite_node_data(all_node_ip)
    nodes = []
    likes = []
    categories = [{"name": "Satellite"}, {"name": "Ground"}]
    sum_num_file = get_node_sum_file(all_nodes=all_node)
    # 记录总共有多少节点
    ids = 0
    # 创建星载节点的基本信息
    for node in all_node:
        one_node = {'id': str(ids), 'name': str(node[1]),
                    'symbolSize': float(int(node[6]) / sum_num_file) * 100.0 + 15.0,
                    'x': float('{:.6f}'.format(random.uniform(-800, 800))),
                    'y': float('{:.6f}'.format(random.uniform(-700, 700))), 'value': int(node[6]), 'category': 0}
        nodes.append(one_node)
        ids = ids + 1
    # 创建地面节点的信息
    for i in range(6):
        one_node = {'id': str(ids), 'name': '10.25.9.' + str(random.randint(1, 8)),
                    'symbolSize': float(random.randint(1, 1000) / sum_num_file) * 100.0 + 15.0,
                    'x': float('{:.6f}'.format(random.uniform(-800, 800))),
                    'y': float('{:.6f}'.format(random.uniform(-700, 700))), 'value': random.randint(1, 1000),
                    'category': 1}
        nodes.append(one_node)
        ids = ids + 1
    # 终端节点的信息(如果用得到的话)
    # for i in range(2):
    #     one_node = {'id': str(ids), 'name': '10.25.9.' + str(random.randint(1, 14)),
    #                 'symbolSize': float(random.randint(1, 1000) / sum_num_file) * 100.0+15.0,
    #                 'x': float('{:.6f}'.format(random.uniform(-800, 800))),
    #                 'y': float('{:.6f}'.format(random.uniform(-700, 700))), 'value': random.randint(1, 1000),
    #                 'category': 2}
    #     nodes.append(one_node)
    #     ids = ids + 1
    # 为每个节点随机赋予一个连接边
    # 生成连接状态，用于表示连接的状态
    for j in range(ids):
        one_link = {'source': str(j), 'target': str(get_node_links(j, ids - 1))}
        likes.append(one_link)
    # 将基本信息保存到json中
    all_node_map = {'nodes': nodes, 'links': likes, 'categories': categories}
    # 得到json形式的数据
    josn_path = r'E:\TJPC\static\showallnode.json'  # 换成你的绝对地址
    with open(josn_path, 'w') as f:
        json.dump(all_node_map, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    print('-start-')
    start = time.perf_counter()
    get_node_josn('10.25.9.11')
    end = time.perf_counter()
    print("运行时间：", end - start, "秒")
    # get_josn = json.dumps(getresult, ensure_ascii=False, indent=4)
    # print(get_josn)
