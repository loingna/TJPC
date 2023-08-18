# -*- coding = utf-8 -*-
# @Time : 2023/6/3
# @author : dsy
# @Software: PyCharm
"""
主要功能：
 (1)连接IPFS接口
 (2)获取IPFS节点的信息（ip，存储，连接状态等）
"""
import json
import ipfshttpclient


# 获取所有的IPFS节点ip
# 输入：需要连接的ip
# 输出：返回与输入ip节点相连的所有ip地址
def get_all_node_ip(ip):
    client = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(ip))
    # 获取得到连接状态
    result = client.swarm.peers()['Peers']
    # 获取所有ip地址
    all_ip_node = []
    for res in result:
        # 以下划线进行分割
        ipaddress = res['Addr'].split('/')
        # 将所有ip加入其中
        all_ip_node.append(str(ipaddress[2]))
    all_ip_node.append(str(ip))
    client.close()
    return all_ip_node


# 获取所有的IPFS节点ip
# 输入：需要连接的ip
# 输出：返回与输入ip节点相连的所有ip地址
def get_allground_node_ip(ip):
    # client = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(ip))
    # # 获取得到连接状态
    # result = client.swarm.peers()['Peers']
    # # 获取所有ip地址
    # all_ip_node = []
    # for res in result:
    #     # 以下划线进行分割
    #     ipaddress = res['Addr'].split('/')
    #     # 将所有ip加入其中
    #     all_ip_node.append(str(ipaddress[2]))
    # all_ip_node.append(str(ip))
    # client.close()
    return ['10.25.9.1', '10.25.9.6', '10.25.9.4', '10.25.9.3', '10.25.9.11','10.25.9.5']


# 获得对应的端口号
# 输入：已经连接了ipfs接口的client
# 输出：返回对应的端口信息
def get_node_port(node_client):
    # 获取端口数据
    node_port = node_client.id()['Addresses'][0].split('/')
    return node_port[4]


# 获取所有星载节点的信息
# 输入：所有ip的列表形式
# 输出：返回所有ip的一些信息
def get_Stellite_node_data(all_ip_node):
    # 获取每一个节点的信息
    all_node = []
    for node in all_ip_node:
        nodes = ['星载节点']
        clients = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(node))
        nodes.append(str(node))
        nodes.append(str(get_node_port(clients)))
        # 获取仓库的大小
        base_repo = clients.repo.stat()
        nodes.append(str(base_repo['Version']))
        nodes.append('10GB')
        # 计算存储占有比例
        proportion = '{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax'])) * 100)
        nodes.append(proportion + '%')
        # 获取文件的数量
        numfile = clients.pin.ls(type='all')['Keys']
        nodes.append(str(len(numfile)))
        all_node.append(nodes)
        clients.close()
    return all_node


# 获取所有地面节点的信息
# 输入：所有ip的列表形式
# 输出：返回所有ip的一些信息
def get_Ground_node_data(all_ip_node):
    # 获取每一个节点的信息
    all_node = []
    for node in all_ip_node:
        nodes = ['地面节点']
        clients = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(node))
        nodes.append(str(node))
        nodes.append(str(get_node_port(clients)))
        # 获取仓库的大小
        base_repo = clients.repo.stat()
        nodes.append(str(base_repo['Version']))
        nodes.append('10GB')
        # 计算存储占有比例
        proportion = '{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax'])) * 100)
        nodes.append(proportion + '%')
        # 获取文件的数量
        numfile = clients.pin.ls(type='all')['Keys']
        nodes.append(str(len(numfile)))
        all_node.append(nodes)
        clients.close()
    return all_node


# 获得指定节点的信息
# 输入：指定的ip地址
# 输出：返回指定的ip的一些信息
def get_ip_node(ip_node, data_id):
    clients = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(ip_node))
    get_node_id = find_id_data(data_id)
    node_detail = []
    # 判断是哪一种节点
    if int(get_node_id[1]) == 0:
        node_detail.append('星载节点')
    else:
        node_detail.append('地面节点')
    # 添加信息到指定id的数组中
    node_detail.append(str(ip_node))
    node_detail.append(str(get_node_port(clients)))
    # 获取仓库的大小
    base_repo = clients.repo.stat()
    node_detail.append(str(base_repo['Version']))
    node_detail.append('10GB')
    proportion = '{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax'])) * 100)
    node_detail.append(proportion + '%')
    node_detail.append(str(get_node_id[0]))
    clients.close()
    return node_detail


# 根据传入的id 获取从json中获得对应的值
# 输入：指定的id(从前端获得的id号)
# 输出：根据json文件的内容返回指定的id的文件大小数和节点类型
def find_id_data(id_index):
    # 打开存放拓扑结构的json文件的位置
    with open(r'E:\TJPC\static\showallnode.json', 'r') as f:
        data = json.load(f)
    # 根据id 找对应的数据
    for node in data['nodes']:
        if int(node['id']) == id_index:
            return [node['value'], node['category']]
    # 如果未找到 id 对应的项，则返回 None
    return None


if __name__ == "__main__":
    # all_nodes = get_all_node_ip('10.25.9.11')
    # print(len(all_nodes))
    # reslut = get_node_data(all_nodes)
    # print(len(reslut))
    all_nd = get_all_node_ip('10.25.9.11')
    print('#'.join(all_nd))
