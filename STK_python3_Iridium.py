import datetime
import time
from tqdm import tqdm
import pandas as pd
startTime = time.time()
from comtypes.gen import STKObjects, STKUtil, AgStkGatorLib
from comtypes.client import CreateObject, GetActiveObject, GetEvents, CoGetObject, ShowEvents
from ctypes import *
import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0
from comtypes import GUID
from comtypes import helpstring
from comtypes import COMMETHOD
from comtypes import dispid
from ctypes.wintypes import VARIANT_BOOL
from ctypes import HRESULT
from comtypes import BSTR
from comtypes.automation import VARIANT
from comtypes.automation import _midlSAFEARRAY
from comtypes import CoClass
from comtypes import IUnknown
import comtypes.gen._00DD7BD4_53D5_4870_996B_8ADB8AF904FA_0_1_0
import comtypes.gen._8B49F426_4BF0_49F7_A59B_93961D83CB5D_0_1_0
from comtypes.automation import IDispatch
import comtypes.gen._42D2781B_8A06_4DB2_9969_72D6ABF01A72_0_1_0
from comtypes import DISPMETHOD, DISPPROPERTY, helpstring


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
stkRoot.UnitPreferences.SetCurrentUnit("DateFormat", "UTCG")
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
# scenario2.StopTime = '18 Feb 2022 16:00:00.00'

totalTime = time.time() - startTime
splitTime = time.time()
print("--- Scenario creation: {a:4.3f} sec\t\tTotal time: {b:4.3f} sec ---".format(a=totalTime, b=totalTime))

# 创建卫星星系
def Creat_satellite(numOrbitPlanes=6, numSatsPerPlane=11, hight=780, Inclination=84, name='Iridium'):
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
            RAAN = 180 / numOrbitPlanes * orbitPlaneNum
            keplarian.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).Value = RAAN  # degrees

            keplarian.LocationType = STKObjects.eLocationTrueAnomaly
            trueAnomaly = 360 / numSatsPerPlane * satNum
            keplarian.Location.QueryInterface(STKObjects.IAgClassicalLocationTrueAnomaly).Value = trueAnomaly

            # Propagate
            satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody).InitialState.Representation.Assign(
                keplarian)
            satellite2.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody).Propagate()

            # Add to constellation object
            constellation2.Objects.AddObject(satellite)


def Export_Satellite_Position():
    # 计算每个卫星的不同时刻的位置
    # sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")
    for Iri in sat_list:
        X_List = []
        Y_List = []
        Z_List = []
        Time_List = []
        # Lat_List = []
        # Lon_List = []
        # Alt_List = []
        result = Iri.DataProviders.GetDataPrvTimeVarFromPath("Cartesian Position//J2000")
        for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
            slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
                "%d %b %Y %H:%M:%S.%f")[:-3]
            slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
                "%d %b %Y %H:%M:%S.%f")[:-3]
            slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
                                              ElementNames=["Time", "x", "y", "z"])
            time = slot_result.DataSets.GetDataSetByName('Time').GetValues()
            X = slot_result.DataSets.GetDataSetByName('x').GetValues()
            Y = slot_result.DataSets.GetDataSetByName('y').GetValues()
            Z = slot_result.DataSets.GetDataSetByName('z').GetValues()
            # Lat = slot_result.DataSets.GetDataSetByName('Lat').GetValues()
            # Lon = slot_result.DataSets.GetDataSetByName('Lon').GetValues()
            # Alt = slot_result.DataSets.GetDataSetByName('Alt').GetValues()

            X_List.append(X[0])
            Y_List.append(Y[0])
            Z_List.append(Z[0])
            Time_List.append(time[0])
            # Lat_List.append(Lat[0])
            # Lon_List.append(Lon[0])
            # Alt_List.append(Alt[0])
        df = pd.DataFrame([Time_List, X_List, Y_List, Z_List])
        df = df.T
        #文件的保存位置可以自己修改

        path = father_path+ "\\Sat_datas\\satellites" + r'\Iridium_position_datas_'+Iri.InstanceName + '.csv'
        df.to_csv(path,
                  header=['Time', 'x', 'y', 'z'], index=False)
        # df.to_csv("C:/Users/hp/PycharmProjects/pythonProject2/venv/Iridium",Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)
        # df.to_csv( Iri.InstanceName + '.csv',
        #           header=['Time', 'x', 'y', 'z'], index=False)

def Export_Satellite_Geographic_Position():
    # 计算每个卫星的不同时刻的位置
    # sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
    start = datetime.datetime.strptime(scenario2.StartTime, "%d %b %Y %H:%M:%S.%f")
    for Iri in sat_list:
        # X_List = []
        # Y_List = []
        # Z_List = []
        Time_List = []
        Lat_List = []
        Lon_List = []
        Alt_List = []
        result = Iri.DataProviders.Item('LLA State').QueryInterface(STKObjects.IAgDataProviderGroup).Group.Item('Fixed').QueryInterface(STKObjects.IAgDataPrvTimeVar)
        for time_slot_num in tqdm(range(int(Time_Range / Time_Step))):
            slot_start_time = (start + datetime.timedelta(seconds=Time_Step * time_slot_num)).strftime(
                "%d %b %Y %H:%M:%S.%f")[:-3]
            slot_stop_time = (start + datetime.timedelta(seconds=Time_Step * (time_slot_num + 1))).strftime(
                "%d %b %Y %H:%M:%S.%f")[:-3]
            slot_result = result.ExecElements(slot_start_time, slot_stop_time, StepTime=0.01,
                                              ElementNames=["Time","Lat","Lon","Alt"])
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
        df = pd.DataFrame([Time_List, Lat_List,Lon_List,Alt_List])
        df = df.T
        #文件的保存位置可以自己修改

        path = father_path+ "\\Sat_datas\\Lat_Lon" + r'\Iridium_geo_position_datas_'+Iri.InstanceName + '.csv'
        df.to_csv(path,
                  header=['Time', 'Lat','Lon','Alt'], index=False)
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
def Set_Transmitter_Parameter(transmitter, frequency=12, EIRP=20, DataRate=14):
    transmitter2 = transmitter.QueryInterface(STKObjects.IAgTransmitter)  # 建立发射机的映射，以便对其进行设置
    transmitter2.SetModel('Simple Transmitter Model')
    txModel = transmitter2.Model
    txModel = txModel.QueryInterface(STKObjects.IAgTransmitterModelSimple)
    txModel.Frequency = frequency  # GHz range:10.7-12.7GHz
    txModel.EIRP = EIRP  # dBW
    txModel.DataRate = DataRate  # Mb/sec

# 设置接收机参数
def Set_Receiver_Parameter(receiver, GT=20, frequency=12):
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

Creat_satellite(numOrbitPlanes=6, numSatsPerPlane=11, hight=780, Inclination=84, name='Iridium')
sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
# for time_slot_num in tqdm(range(int(Time_Range / Time_Step) - 2)):
Export_Satellite_Geographic_Position()