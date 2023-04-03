import datetime
import math
import time

import numpy
import pandas as pd
# from comtypes.gen._00DD7BD4_53D5_4870_996B_8ADB8AF904FA_0_1_0 import IAgConversionUtility
from numba import none
from tqdm import tqdm

# from STK_linkto_Python.link1 import root

startTime = time.time()
from comtypes.gen import STKObjects, STKUtil
from comtypes.client import CreateObject, GetActiveObject

import os
father_path =os.getcwd()


"""
SET TO TRUE TO USE ENGINE, FALSE TO USE GUI
"""
useStkEngine = False
Read_Scenario = False
############################################################################
# Scenario Setup
############################################################################

if useStkEngine:
    # Launch STK Engine
    print("Launching STK Engine...")
    stkxApp = CreateObject("STKX11.Application")

    # Disable graphics. The NoGraphics property must be set to true before the root object is created.
    stkxApp.NoGraphics = True

    # Create root object
    stkRoot = CreateObject('AgStkObjects11.AgStkObjectRoot')

else:
    # Launch GUI
    print("Launching STK...")
    if not Read_Scenario:
        uiApp = CreateObject("STK11.Application")
    else:
        uiApp = GetActiveObject("STK11.Application")
    uiApp.Visible = True
    uiApp.UserControl = True

    # Get root object
    stkRoot = uiApp.Personality2

# Set date format
stkRoot.UnitPreferences.SetCurrentUnit("DateFormat", "UTCG") # UTCG EpSec
# Create new scenario
print("Creating scenario...")
if not Read_Scenario:
    # stkRoot.NewScenario('Kuiper')
    stkRoot.NewScenario('Iridium')
scenario = stkRoot.CurrentScenario
scenario2 = scenario.QueryInterface(STKObjects.IAgScenario)
Time_Range = 60  # Seconds
Time_Step = 1  # Seconds
# scenario2.StartTime = '17 Feb 2022 16:00:00.00'
# scenario2.StopTime = '17 Feb 2022 17:40:00.00'
# scenario2.SetTimePeriod('17 Feb 2022 16:00:00.00','17 Feb 2022 17:40:00.00')
print(scenario2.StartTime)
print(scenario2.StopTime)
totalTime = time.time() - startTime
splitTime = time.time()
print("--- Scenario creation: {a:4.3f} sec\t\tTotal time: {b:4.3f} sec ---".format(a=totalTime, b=totalTime))

# 创建卫星星系
def Creat_satellite(numOrbitPlanes=6, numSatsPerPlane=11, hight=780, Inclination=86.4, name='Iridium'):
    # Create constellation object
    constellation = scenario.Children.New(STKObjects.eConstellation, name)
    constellation2 = constellation.QueryInterface(STKObjects.IAgConstellation)

    # Insert the constellation of Satellites
    for orbitPlaneNum in range(numOrbitPlanes):  # RAAN in degrees

        for satNum in range(numSatsPerPlane):  # trueAnomaly in degrees
            # Insert satellite
            satellite = scenario.Children.New(STKObjects.eSatellite, f"{name}{orbitPlaneNum}_{satNum}")
            satellite2 = satellite.QueryInterface(STKObjects.IAgSatellite)

            # Select Propagator
            satellite2.SetPropagatorType(STKObjects.ePropagatorTwoBody)

            # Set initial state
            twoBodyPropagator = satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
            keplarian = twoBodyPropagator.InitialState.Representation.ConvertTo(
                STKUtil.eOrbitStateClassical).QueryInterface(STKObjects.IAgOrbitStateClassical)

            keplarian.SizeShapeType = STKObjects.eSizeShapeSemimajorAxis
            keplarian.SizeShape.QueryInterface(
                STKObjects.IAgClassicalSizeShapeSemimajorAxis).SemiMajorAxis = hight + 6371  # km
            keplarian.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeSemimajorAxis).Eccentricity = 0

            keplarian.Orientation.Inclination = int(Inclination)  # degrees
            keplarian.Orientation.ArgOfPerigee = 0  # degrees
            keplarian.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
            RAAN = 120 + 180 / numOrbitPlanes * orbitPlaneNum
            keplarian.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).Value = RAAN  # degrees

            keplarian.LocationType = STKObjects.eLocationTrueAnomaly
            if (orbitPlaneNum % 2) ==0:
                trueAnomaly = 360 / numSatsPerPlane * satNum
            else:
                trueAnomaly = 360 / numSatsPerPlane * satNum + 16
            keplarian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = trueAnomaly

            # Propagate
            satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody).InitialState.Representation.Assign(
                keplarian)
            satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody).Propagate()

            # Add to constellation object
            constellation2.Objects.AddObject(satellite)

# 每个时刻卫星节点
def Export_Satellite_Position():
    # 计算每个卫星的不同时刻的位置
    # sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")

    for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
        X_List = []
        Y_List = []
        Z_List = []
        Time_List = []
        Node_List = []
        slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        time1 = time_slot_num
        for Iri in sat_list:

            # 这里是按照节点存储数据 一个时间及其对应的xyz轴数据，改成按照时间存储，一个时间下所有点的xyz轴位置
            result = Iri.DataProviders.GetDataPrvTimeVarFromPath("Cartesian Position//J2000")

            slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
                                              ElementNames=["Time", "x", "y", "z"])
            time = slot_result.DataSets.GetDataSetByName('Time').GetValues()
            X = slot_result.DataSets.GetDataSetByName('x').GetValues()
            Y = slot_result.DataSets.GetDataSetByName('y').GetValues()
            Z = slot_result.DataSets.GetDataSetByName('z').GetValues()
            X_List.append(X[0])
            Y_List.append(Y[0])
            Z_List.append(Z[0])
            Time_List.append(time[0])
            Node_List.append(str(sat_dic1[Iri.InstanceName]))
        df = pd.DataFrame([Node_List, X_List, Y_List, Z_List])
        df = df.T
        #文件的保存位置可以自己修改

        path = father_path+ "\\Sat_datas\\timeslice" + r'\Iridium_datas_'+str(time1) + '.csv'
        df.to_csv(path,
                  header=['node', 'x', 'y', 'z'], index=False,sep=' ')
        # df.to_csv("C:/Users/hp/PycharmProjects/pythonProject2/venv/Iridium",Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
        # df.to_csv( Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)

def Export_Satellite_Geographic_Position_timeslice_test():
    # 计算每个卫星的不同时刻的位置
    # sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")

    for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):

        # X_List = []
        # Y_List = []
        # Z_List = []
        Time_List = []
        Node_List = []
        Lat_List = []
        Lon_List = []
        # Alt_List = []

        slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        time1 = time_slot_num
        for Iri in sat_list:
            result = Iri.DataProviders.Item('LLA State').QueryInterface(STKObjects.IAgDataProviderGroup).Group.Item(
                'Fixed').QueryInterface(STKObjects.IAgDataPrvTimeVar)

            slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
                                              ElementNames=["Time", "Lat", "Lon", "Alt"])
            time = slot_result.DataSets.GetDataSetByName('Time').GetValues()
            # X = slot_result.DataSets.GetDataSetByName('x').GetValues()
            # Y = slot_result.DataSets.GetDataSetByName('y').GetValues()
            # Z = slot_result.DataSets.GetDataSetByName('z').GetValues()
            Lat = slot_result.DataSets.GetDataSetByName('Lat').GetValues()
            Lon = slot_result.DataSets.GetDataSetByName('Lon').GetValues()
            Alt = slot_result.DataSets.GetDataSetByName('Alt').GetValues()

            # X_List.append(X[0])
            # Y_List.append(Y[0])
            # Z_List.append(Z[0])
            # Time_List.append(time[0])



            Lat_List.append(Lat[0])
            Lon_List.append(Lon[0])
            # Alt_List.append(Alt[0])
            Node_List.append(str(sat_dic1[Iri.InstanceName]))
        df = pd.DataFrame([Node_List, Lon_List,Lat_List])
        df = df.T
        #文件的保存位置可以自己修改

        path = father_path+ "\\Sat_datas\\timeslice\\Lat_Lon" + r'\Iridium_position'+str(time1) + '.csv'
        df.to_csv(path,
                  header=['Node', 'Lon','Lat'], index=False)
        # df.to_csv("C:/Users/hp/PycharmProjects/pythonProject2/venv/Iridium",Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
        # df.to_csv( Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
def Export_Satellite_Geographic_Position_timeslice():
    # 计算每个卫星的不同时刻的位置
    # sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")

    for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):

        # X_List = []
        # Y_List = []
        # Z_List = []
        Time_List = []
        Node_List = []
        Lat_List = []
        Lon_List = []
        Alt_List = []

        slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
            "%d %b %Y %H:%M:%S.%f")[:-3]
        time1 = time_slot_num
        for Iri in sat_list:
            result = Iri.DataProviders.Item('LLA State').QueryInterface(STKObjects.IAgDataProviderGroup).Group.Item(
                'Fixed').QueryInterface(STKObjects.IAgDataPrvTimeVar)

            slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
                                              ElementNames=["Time", "Lat", "Lon", "Alt"])
            time = slot_result.DataSets.GetDataSetByName('Time').GetValues()
            # X = slot_result.DataSets.GetDataSetByName('x').GetValues()
            # Y = slot_result.DataSets.GetDataSetByName('y').GetValues()
            # Z = slot_result.DataSets.GetDataSetByName('z').GetValues()
            Lat = slot_result.DataSets.GetDataSetByName('Lat').GetValues()
            Lon = slot_result.DataSets.GetDataSetByName('Lon').GetValues()
            Alt = slot_result.DataSets.GetDataSetByName('Alt').GetValues()

            # X_List.append(X[0])
            # Y_List.append(Y[0])
            # Z_List.append(Z[0])
            Time_List.append(time[0])
            Lat_List.append(Lat[0])
            Lon_List.append(Lon[0])
            Alt_List.append(Alt[0])
            Node_List.append(Iri.InstanceName)
        df = pd.DataFrame([Node_List, Lat_List,Lon_List,Alt_List])
        df = df.T
        #文件的保存位置可以自己修改

        path = father_path+ "\\Sat_datas\\timeslice\\Lat_Lon" + r'\Iridium_datas_Lat_Lon_'+str(time1) + '.csv'
        df.to_csv(path,
                  header=['Node', 'Lat','Lon','Alt'], index=False)
        # df.to_csv("C:/Users/hp/PycharmProjects/pythonProject2/venv/Iridium",Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
        # df.to_csv( Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
# 为每个卫星加上发射机和接收机
def Add_transmitter_receiver(sat_list):
    for each in sat_list:
        Instance_name = each.InstanceName
        #  new transmitter and receiver
        transmitter = each.Children.New(STKObjects.eTransmitter, "Transmitter_" + Instance_name)
        reciver = each.Children.New(STKObjects.eReceiver, "Reciver_" + Instance_name)
        # sensor = each.Children.New(STKObjects.eSensor, 'Sensor_' + Instance_name)

# 设置发射机参数
def Set_Transmitter_Parameter(transmitter, frequency=30, EIRP=29, DataRate=20):
    transmitter2 = transmitter.QueryInterface(STKObjects.IAgTransmitter)  # 建立发射机的映射，以便对其进行设置
    transmitter2.SetModel('Simple Transmitter Model')
    txModel = transmitter2.Model
    txModel = txModel.QueryInterface(STKObjects.IAgTransmitterModelSimple)
    txModel.Frequency = frequency  # GHz range:10.7-12.7GHz
    txModel.EIRP = EIRP  # dBW
    txModel.DataRate = DataRate  # Mb/sec

# 设置接收机参数
def Set_Receiver_Parameter(receiver, GT=20, frequency=30):
    receiver2 = receiver.QueryInterface(STKObjects.IAgReceiver)  # 建立发射机的映射，以便对其进行设置
    receiver2.SetModel('Simple Receiver Model')
    recModel = receiver2.Model
    recModel = recModel.QueryInterface(STKObjects.IAgReceiverModelSimple)
    recModel.AutoTrackFrequency = False
    recModel.Frequency = frequency  # GHz range:10.7-12.7GHz
    recModel.GOverT = GT  # dB/K
    return receiver2

# 获得接收机示例，并设置其参数
def Get_sat_receiver(sat, GT=20, frequency=12):
    receiver = sat.Children.GetElements(STKObjects.eReceiver)[0]  # 找到该卫星的接收机
    receiver2 = Set_Receiver_Parameter(receiver=receiver, GT=GT, frequency=frequency)
    return receiver2



def Compute_access(access):
    access.ComputeAccess()
    accessDP = access.DataProviders.Item('Link Information')
    accessDP2 = accessDP.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    Elements = ["Time", 'Link Name', 'EIRP', 'Prop Loss', 'Rcvr Gain', "Xmtr Gain", "Eb/No", "BER"]
    results = accessDP2.ExecElements(scenario2.StartTime, scenario2.StopTime, 3600, Elements)
    Times = results.DataSets.GetDataSetByName('Time').GetValues()  # 时间
    EbNo = results.DataSets.GetDataSetByName('Eb/No').GetValues()  # 码元能量

    BER = results.DataSets.GetDataSetByName('BER').GetValues()  # 误码率
    Link_Name = results.DataSets.GetDataSetByName('Link Name').GetValues()
    Prop_Loss = results.DataSets.GetDataSetByName('Prop Loss').GetValues()
    Xmtr_Gain = results.DataSets.GetDataSetByName('Xmtr Gain').GetValues()
    EIRP = results.DataSets.GetDataSetByName('EIRP').GetValues()
    # Range = results.DataSets.GetDataSetByName('Range').GetValues()
    return Times, Link_Name, BER, EbNo, Prop_Loss, Xmtr_Gain, EIRP

def Compute_posation_access(access):
    # stkRoot.UnitPreferences.SetCurrentUnit("DateFormat", "EpSec")
    access.ComputeAccess()
    accessDP = access.DataProviders.Item('Link Information')
    accessDP2 = accessDP.QueryInterface(STKObjects.IAgDataPrvTimeVar)
    Elements = ['Time', 'Link Name', 'Propagation Delay','Propagation Distance']

    # start = stkRoot.ConversionUtility.NewDate('EpSec', str(scenario2.StartTime ))
    # stop = stkRoot.ConversionUtility.NewDate('EpSec', str(scenario2.StopTime ))
    results = accessDP2.ExecElements(scenario2.StartTime, scenario2.StopTime, 1,Elements)

    Times = results.DataSets.GetDataSetByName('Time').GetValues()  # 时间

    Link_Name = results.DataSets.GetDataSetByName('Link Name').GetValues()
    Propagation_Delay = results.DataSets.GetDataSetByName('Propagation Delay').GetValues()
    Propagation_Distance = results.DataSets.GetDataSetByName('Propagation Distance').GetValues()
    return Times,Link_Name,Propagation_Delay,Propagation_Distance

# 创建所有access并计算结果然后将其存储到links 文件里面
def Creating_All_Access():
    # start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")
    #
    # print(start)
    # for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
    #     time1 = time_slot_num

    time1 = 0
    # 首先清空场景中所有的链接
    print('Clearing All Access')
    stkRoot.ExecuteCommand('RemoveAllAccess /')

    # 限制通信经纬度
    # IAgAccessConstraintCollection accessConstraints: Access Constraint collection
    # excludeZone = STKObjects.IAgAccessConstraintCollection.accessConstraints.AddNamedConstraint('ExclusionZone')
    # excludeZone.MaxLat = 70
    # excludeZone.MinLat = -70
    # excludeZone.MinLon = -75
    # excludeZone.MaxLon = -35

    # for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
    Node_List =[]
    # Lat_List = []
    B_Link_Name_List = []
    F_Link_Name_List = []
    L_Link_Name_List = []
    R_Link_Name_List = []

    B_Propagation_Delay_List = []
    F_Propagation_Delay_List = []
    L_Propagation_Delay_List = []
    R_Propagation_Delay_List = []
    B_Propagation_Distance_List = []
    F_Propagation_Distance_List = []
    L_Propagation_Distance_List = []
    R_Propagation_Distance_List = []

    # slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
    #     "%d %b %Y %H:%M:%S.%f")[:-3]
    # print(slot_start_time)
    # print(type(slot_start_time))
    # slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
    #     "%d %b %Y %H:%M:%S.%f")[:-3]
    # print(slot_stop_time)



    # slot_start_time = time1
    # slot_stop_time = time1 + 1
    # 计算某个卫星与其通信的四颗卫星的链路质量，并生成报告

    for each_sat in sat_list:

        now_sat_name = each_sat.InstanceName

        now_plane_num =int(now_sat_name.split('_')[0][7:])
        now_sat_num = int(now_sat_name.split('_')[1])
        now_sat_transmitter = each_sat.Children.GetElements(STKObjects.eTransmitter)[0]  # 找到该卫星的发射机
        Set_Transmitter_Parameter(now_sat_transmitter, EIRP=20)
        # 发射机与接收机相连
        # 与后面的卫星的接收机相连
        access_backward = now_sat_transmitter.GetAccessToObject(
            Get_sat_receiver(sat_dic['Iridium' + str(now_plane_num) + '_' + str((now_sat_num + 1) % 11)]))
        # 与前面的卫星的接收机相连
        access_forward = now_sat_transmitter.GetAccessToObject(
            Get_sat_receiver(sat_dic['Iridium' + str(now_plane_num) + '_' + str((now_sat_num - 1) % 11)]))
        # 与左面的卫星的接收机相连
        access_left = now_sat_transmitter.GetAccessToObject(
            Get_sat_receiver(sat_dic['Iridium' + str((now_plane_num - 1) % 6) + '_' + str(now_sat_num)]))
        # 与右面的卫星的接收机相连
        access_right = now_sat_transmitter.GetAccessToObject(
            Get_sat_receiver(sat_dic['Iridium' + str((now_plane_num + 1) % 6) + '_' + str(now_sat_num)]))
        # result = each_sat.DataProviders.Item('LLA State').QueryInterface(STKObjects.IAgDataProviderGroup).Group.Item(
        #     'Fixed').QueryInterface(STKObjects.IAgDataPrvTimeVar)
        #
        # slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
        #                                   ElementNames=["Time", "Lat", "Lon", "Alt"])
        # lat = slot_result.DataSets.GetDataSetByName('Lat').GetValues()

        # B_Link_Name, B_Propagation_Delay, B_Propagation_Distance = Compute_posation_access(access_backward)
        # F_Link_Name, F_Propagation_Delay, F_Propagation_Distance  = Compute_posation_access(access_forward)
        # L_Link_Name, L_Propagation_Delay, L_Propagation_Distance = Compute_posation_access(access_left)
        # R_Link_Name, R_Propagation_Delay, R_Propagation_Distance = Compute_posation_access(access_right)


        # B_Time,B_Link_Name, B_Propagation_Delay, B_Propagation_Distance = Compute_posation_access(access_backward)
        # F_Time,F_Link_Name, F_Propagation_Delay, F_Propagation_Distance  = Compute_posation_access(access_forward)
        # L_Time,L_Link_Name, L_Propagation_Delay, L_Propagation_Distance = Compute_posation_access(access_left)
        # R_Time,R_Link_Name, R_Propagation_Delay, R_Propagation_Distance = Compute_posation_access(access_right)
            # print('{0}\r', R_Times, R_Link_Name, R_BER, R_EbNo, R_Prop_Loss, R_Xmtr_Gain, R_EIRP)

        # default = None
        # Node_List.append(now_sat_name)
        # B_Link_Name_List.append(B_Link_Name[0]if 0 > len(B_Link_Name[0]) else default)
        # F_Link_Name_List.append(F_Link_Name[0]if 0 > len(F_Link_Name[0]) else default)
        # L_Link_Name_List.append(L_Link_Name[0]if 0 > len(L_Link_Name[0]) else default)
        # R_Link_Name_List.append(R_Link_Name[0]if 0 > len(R_Link_Name[0]) else default)
        # B_Propagation_Delay_List.append(B_Propagation_Delay[0]if 0 > len(B_Propagation_Delay[0]) else default)
        # F_Propagation_Delay_List.append(F_Propagation_Delay[0]if 0 > len(F_Propagation_Delay[0]) else default)
        # L_Propagation_Delay_List.append(L_Propagation_Delay[0]if 0 > len(L_Propagation_Delay[0]) else default)
        # R_Propagation_Delay_List.append(R_Propagation_Delay[0] if 0 > len(R_Propagation_Delay[0]) else default)
        # B_Propagation_Distance_List.append(B_Propagation_Distance[0] if 0 > len(B_Propagation_Distance[0]) else default)
        # F_Propagation_Distance_List.append(F_Propagation_Distance[0] if 0 > len(F_Propagation_Distance[0]) else default)
        # L_Propagation_Distance_List.append(L_Propagation_Distance[0] if 0 > len(L_Propagation_Distance[0]) else default)
        # R_Propagation_Distance_List.append(R_Propagation_Distance[0] if 0 > len(R_Propagation_Distance_List[0]) else default)
        # if now_sat_name == "Iridium0_0":
        #     print(B_Time)
        #     print("换行"+str((B_Time)))
        #     print(B_Propagation_Delay)
        #     print("换行"+str(len(B_Propagation_Delay)))
        #     print(B_Propagation_Distance)
        #     print("换行" + str(len(B_Propagation_Distance)))

    # for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
    #     time1 = time_slot_num
    #     Node_List.append(now_sat_name)
        # Lat_List.append(lat)
    #     B_Link_Name_List.append(B_Link_Name[0])
    #     F_Link_Name_List.append(F_Link_Name[0])
    #     L_Link_Name_List.append(L_Link_Name[0])
    #     R_Link_Name_List.append(R_Link_Name[0])
    #
    #     B_Propagation_Delay_List.append(B_Propagation_Delay[time1] )
    #     F_Propagation_Delay_List.append(F_Propagation_Delay [time1])
    #     L_Propagation_Delay_List.append(L_Propagation_Delay [time1])
    #     R_Propagation_Delay_List.append(R_Propagation_Delay [time1])
    #     B_Propagation_Distance_List.append(B_Propagation_Distance[time1])
    #     F_Propagation_Distance_List.append(F_Propagation_Distance [time1])
    #     L_Propagation_Distance_List.append(L_Propagation_Distance [time1])
    #     R_Propagation_Distance_List.append(R_Propagation_Distance [time1])
    #     # time1+= 1
    # df = pd.DataFrame([Node_List,B_Link_Name_List, F_Link_Name_List, L_Link_Name_List,R_Link_Name_List
    #                    ,B_Propagation_Delay_List,F_Propagation_Delay_List,L_Propagation_Delay_List,R_Propagation_Delay_List
    #                    ,B_Propagation_Distance_List,F_Propagation_Distance_List,L_Propagation_Distance_List,R_Propagation_Distance_List])
    # df = df.T
    # path = father_path + "\\Sat_datas\\timeslice\\links" + r'\Iridium_link_datas_' + str(time1) + '.csv'
    # df.to_csv(path,
    #           header=['Node_List','B_Link_Name_List', 'F_Link_Name_List', 'L_Link_Name_List','R_Link_Name_List'
    #                    ,'B_Propagation_Delay_List','F_Propagation_Delay_List','L_Propagation_Delay_List','R_Propagation_Delay_List'
    #                    ,'B_Propagation_Distance_List','F_Propagation_Distance_List','L_Propagation_Distance_List','R_Propagation_Distance_List'], index=False)
    #

# 主函数部分

Creat_satellite(numOrbitPlanes=6, numSatsPerPlane=11, hight=780, Inclination=86.4, name='Iridium')
sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
sat_dic = {}
print('Creating Satellite Dictionary')
for sat in tqdm(sat_list):
    # now_sat_name = sat.InstanceName# 当前卫星名称
    # now_plane_num = int(now_sat_name.split('_')[0][7:]) # 当前所在平面
    # now_sat_num = int(now_sat_name.split('_')[1]) # 当前所在的卫星编号
    # sat_dic[sat.InstanceName] = now_plane_num * 11 + now_sat_num + 1
    sat_dic[sat.InstanceName] = sat

sat_dic1 = {}
for sat in tqdm(sat_list):
    now_sat_name = sat.InstanceName# 当前卫星名称
    now_plane_num = int(now_sat_name.split('_')[0][7:]) # 当前所在平面
    now_sat_num = int(now_sat_name.split('_')[1]) # 当前所在的卫星编号
    sat_dic1[sat.InstanceName] = now_plane_num * 11 + now_sat_num
print(sat_dic1)

# Export_Satellite_Position()
# Export_Satellite_Geographic_Position_timeslice()
# Export_Satellite_Geographic_Position_timeslice_test()

Add_transmitter_receiver(sat_list)
Creating_All_Access()
'''
def access():
    Add_transmitter_receiver(sat_list)

    # Creating_All_Access(100)

    # 分时隙计算所有access并生成文件

    for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
        time1 = time_slot_num
        Creating_All_Access(time1)
access()
'''