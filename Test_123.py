# def shabi(who):
#     print("我是"+who+"我是傻逼")
import numpy as np
# import h5py
# with h5py.File('pems-bay.h5',"r") as f:
#     for key in f.keys():
#         #print(f[key], key, f[key].name, f[key].value) # 因为这里有group对象它是没有value属性的,故会异常。另外字符串读出来是字节流，需要解码成字符串。
#         print(f[key], key, f[key].name)
#         '''
#         <HDF5 dataset "axis0": shape (325,), type "<i8"> /speed/axis0
#         <HDF5 dataset "axis1": shape (52116,), type "<i8"> /speed/axis1
#         <HDF5 dataset "block0_items": shape (325,), type "<i8"> /speed/block0_items
#         <HDF5 dataset "block0_values": shape (52116, 325), type "<f8"> /speed/block0_values
#         '''
#         speeds_group =  f["speed"]
#         for dkey in speeds_group.keys():
#             print(dkey, speeds_group[dkey], speeds_group[dkey].name, speeds_group[dkey][()])

str = '4029.435310156447'
if str > '4039':
    print(True)
print(type(str))