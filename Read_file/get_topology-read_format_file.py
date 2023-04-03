import csv
import pandas as pd

# 卫星编号字典
sat_dic1 = {'Iridium0_0': 0, 'Iridium0_1': 1, 'Iridium0_2': 2, 'Iridium0_3': 3, 'Iridium0_4': 4, 'Iridium0_5': 5, 'Iridium0_6': 6, 'Iridium0_7': 7, 'Iridium0_8': 8, 'Iridium0_9': 9, 'Iridium0_10': 10,
            'Iridium1_0': 11, 'Iridium1_1': 12, 'Iridium1_2': 13, 'Iridium1_3': 14, 'Iridium1_4': 15, 'Iridium1_5': 16, 'Iridium1_6': 17, 'Iridium1_7': 18, 'Iridium1_8': 19, 'Iridium1_9': 20, 'Iridium1_10': 21,
            'Iridium2_0': 22, 'Iridium2_1': 23, 'Iridium2_2': 24, 'Iridium2_3': 25, 'Iridium2_4': 26, 'Iridium2_5': 27, 'Iridium2_6': 28, 'Iridium2_7': 29, 'Iridium2_8': 30, 'Iridium2_9': 31, 'Iridium2_10': 32,
            'Iridium3_0': 33, 'Iridium3_1': 34, 'Iridium3_2': 35, 'Iridium3_3': 36, 'Iridium3_4': 37, 'Iridium3_5': 38, 'Iridium3_6': 39, 'Iridium3_7': 40, 'Iridium3_8': 41, 'Iridium3_9': 42, 'Iridium3_10': 43,
            'Iridium4_0': 44, 'Iridium4_1': 45, 'Iridium4_2': 46, 'Iridium4_3': 47, 'Iridium4_4': 48, 'Iridium4_5': 49, 'Iridium4_6': 50, 'Iridium4_7': 51, 'Iridium4_8': 52, 'Iridium4_9': 53, 'Iridium4_10': 54,
            'Iridium5_0': 55, 'Iridium5_1': 56, 'Iridium5_2': 57, 'Iridium5_3': 58, 'Iridium5_4': 59, 'Iridium5_5': 60, 'Iridium5_6': 61, 'Iridium5_7': 62, 'Iridium5_8': 63, 'Iridium5_9': 64, 'Iridium5_10': 65}


filepath = 'D:\\Desktop\\软件合集以及资料整理\\Stk11.6\\pythonProject2\\Sat_datas\\timeslice\\'
data = []
link_file_name = "links\\Iridium_link_datas_"
lat_file_name ="Lat_lon\\Iridium_position"
# Iridium_link_datas_0.csv
for i in range (60):
    latfilename = filepath +lat_file_name + str(i) + '.csv'
    lat_dict = {}
    with open(latfilename) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        header = next(csv_reader)  # 读取第一行每一列的标题 跳过表头
        for row in csv_reader:  # 将csv 文件中的数据保存到data中
            lat_dict[row[0]] = float(row[2])
    print(lat_dict)
    linkfilename = filepath +link_file_name + str(i)+'.csv'
    with open(linkfilename) as csvfile:
        node_list =[]
        back_link_list =[]
        front_link_list =[]
        left_link_list =[]
        right_link_list =[]

        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        header = next(csv_reader)        # 读取第一行每一列的标题 跳过表头
        for row in csv_reader:  # 将csv 文件中的数据保存到data中

            # 此处为数据读取
            # 第一列表示当前卫星
            cur_sat = sat_dic1[row[0]]
            lat = lat_dict[str(cur_sat)]
            # 第二、三、四、五行表示的是连接的边， 就是两个点 可以用tuple 数组表示
            for j in range(4):

                link_node = row[j+1].split(" ")[0].split("/")[0]
                cur_node = row[j+1].split(" ")[-1].split("/")[0]
                delay = row[j+5]
                distances = row[j+9]
                tup_link_temp = (sat_dic1[cur_node],sat_dic1[link_node],delay,distances)
                if j == 0:
                    back_link_list.append(tup_link_temp)
                elif j == 1:
                    front_link_list.append(tup_link_temp)
                elif j == 2:
                    if lat >= -60 and lat <= 60:
                        left_link_list.append(tup_link_temp)
                    else :
                        temp = (sat_dic1[cur_node], sat_dic1[link_node], delay, '6666')
                        left_link_list.append(temp)
                else:
                    if lat >= -60 and lat <= 60:
                        right_link_list.append(tup_link_temp)
                    else :
                        temp = (sat_dic1[cur_node], sat_dic1[link_node], delay, '6666')
                        right_link_list.append(temp)

            #后面的都是数据就不写了
            node_list.append(cur_sat)
        df = pd.DataFrame([node_list ,back_link_list, front_link_list, left_link_list,right_link_list])
        df = df.T
        # 文件的保存位置可以自己修改

        path = "D:\\Desktop\\软件合集以及资料整理\\Stk11.6\\pythonProject2\\"+ \
               "\\Sat_datas\\timeslice\\links_deal" + r'\Iridium_timeslice_link_datas_' + str(i) + '.csv'
        df.to_csv(path,
                  header=['Node', 'back_link','front_link','left_link','right_link'], index=False)


