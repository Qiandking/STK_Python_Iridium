import csv
import networkx as nx
import pandas as pd

filepath = 'D:\\Desktop\\软件合集以及资料整理\\Stk11.6\\pythonProject2\\Sat_datas\\timeslice\\links_deal\\'
data = []
file_name = "Iridium_timeslice_link_datas_"
# for i in range (60):

for idx in range(60):
# idx = 1
    filename = filepath +file_name + str(idx)+'.csv'
    x_list =[]
    y_list =[]
    weight_list = []
    with open(filename) as csvfile:
        G = nx.Graph()
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        header = next(csv_reader)  # 读取第一行每一列的标题 跳过表头
        for row in csv_reader:  # 将csv 文件中的数据保存到data中
            for i in range(1,5):

                temp = eval(row[i])
                # 6548
                if temp[3] < '5810' :
                    # temp_list = temp.split(",")
                    # print(eval(temp[3]))
                    # print(type(eval(temp[3])))

                    G.add_edge(int(temp[0]), int(temp[1]),weight = eval(temp[3]))
        # edges_num = G.number_of_edges()
        # nodes_num = G.number_of_nodes()
        # print(edges_num)
        # print(nodes_num)
        # print([e for e in G.edges])
        # print(list(G.nodes))
        # print(4*66)
        print('5节点到33节点最短路径: ', nx.shortest_path(G, source=5, target=33))
        print('5节点到33节点最短路径: ', nx.shortest_path_length(G, source=5, target=33))
        print((nx.path_weight(G,nx.shortest_path(G, source=5, target=33),weight="weight" ))/300)
        # print('5节点到33节点所有最短路径: ', [p for p in nx.all_shortest_paths(G, source=5, target=33)])
        for e in G.edges:
            # print(len(e))
            # print(e[0])
            x_list.append(str(e[0]))
            y_list.append(str(e[1]))
            weight_list.append(G.edges[e[0],e[1]]['weight'])
        df = pd.DataFrame([x_list, y_list, weight_list])
        df = df.T
        # 文件的保存位置可以自己修改

        path = "D:\\Desktop\\软件合集以及资料整理\\Stk11.6\\pythonProject2\\" + \
               "\\result_timeslice" + r'\Iridium_link_datas_' + str(idx) + '.csv'
        df.to_csv(path,
                  header=['x', 'y', 'weight'], index=False, sep=' ')

