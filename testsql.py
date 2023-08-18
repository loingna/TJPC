
from app.GetConn.DBUtil import get_conn, close_conn
import ipfshttpclient


# 判断是否存在用户
def exist_user(username):
    sql = "SELECT * FROM user WHERE username ='%s'" % username
    conn, cur = get_conn()
    cur.execute(sql)
    result = cur.fetchall()
    print(result)
    print(result[0][1])
    close_conn(conn, cur)
    if len(result) == 0:
        return False
    else:
        return True


if __name__ == '__main__':
    # tyest = 'get_status restart killself ground_node onboard_node'
    # if 'onboard_node ground_node' in tyest:
    #     print(tyest.replace('onboard_node ground_node', ''))
    # elif 'onboard_node' in tyest:
    #     print(tyest.replace('onboard_node', ''))
    # elif 'ground_node' in tyest:
    #     print(tyest.replace('ground_node', ''))
    # else:
    #     print('error')
    # print(tyest.replace(' ','#'))
    client = ipfshttpclient.connect('/ip4/10.25.9.1/tcp/5001/http')
    # file_address = client.add(r'E:\dqq\dqq.txt')
    # 获取得到连接状态
    result = client.swarm.peers()['Peers']
    print(result)
    # 获取所有ip地址
    all_ip_node = []
    for res in result:
        ipaddress = res['Addr'].split('/')
        # print(ipaddress)
        # 将所有ip加入其中
        all_ip_node.append(str(ipaddress[2]))
    print(len(all_ip_node))
    print(all_ip_node)
    # 获取每一个节点的信息
    all_node = []
    for node in all_ip_node:
        nodes = []
        nodes.append('星载节点')
        clients = ipfshttpclient.connect(f'/ip4/%s/tcp/5001/http' % str(node))
        nodes.append(str(node))
        nodes.append('4001')
        # 获取仓库的大小
        base_repo = clients.repo.stat()
        nodes.append(str(base_repo['Version']))
        nodes.append('10GB')
        proportion='{:.4f}'.format((int(base_repo['RepoSize']) / int(base_repo['StorageMax']))*100)
        nodes.append(proportion + '%')
        # 获取文件的数量
        numfile = clients.pin.ls(type='all')['Keys']
        nodes.append(str(len(numfile)))
        print(nodes)
        all_node.append(nodes)
        clients.close()
    print(len(all_node))
    client.close()
    # print(client.bitswap())
