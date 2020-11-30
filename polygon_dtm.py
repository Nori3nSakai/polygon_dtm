# -*- coding: utf-8 -*-
from osgeo import gdal, osr, gdalconst, gdal_array
import numpy as np
import cv2
import pvl
import os
import math
import sys


# polygon_dtm.py
def dtm_polygon(file_path):
    
    # file_pathで入力されたfileから緯度経度、四隅の点を出力させる。
    # ただし、使えるfileは、HiRISE DTMオルソ画像データと呼ばれる火星観測データ。
    # 例:
    #     URL:https://hirise-pds.lpl.arizona.edu/PDS/DTM/PSP/ORB_001300_001399/PSP_001336_1560_PSP_001534_1560/
    #     このURL内の拡張子.JP2のデータを読み込ませる。(データ容量が大きいので、注意)

    # また、このデータは、拡張子.JP2となっているが、画像データ(JP2000)ではない。GeoJP2000というかなり特殊なデータになっている。
    # そのため、画像データの様にオープンさせることができない。

    # このソースコードの使い方
    # １、URL記載の火星観測データ(.JP2と.LBL)をダウンロードする。
    # ２、gdal_translate -of "GTiff" PSP_001336_1560_RED_A_01_ORTHO.JP2 PSP_001336_1560_RED_A_01_ORTHO.tif を実行。（gdalをインストール。ターミナルで実行。）
    # ３、python polygon_dtm.py file_path(PSP_001336_1560_RED_A_01_ORTHO.tif)
    
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    NDV=dataset.GetRasterBand(1).GetNoDataValue()
    Array=dataset.GetRasterBand(1).ReadAsArray()
    # gdalで.tifをopen. NDV=None data Value. Array=データ用の配列.

    arr = [[0 for i in range(len(Array[0])+2)] for j in range(len(Array)+2)]
    xx=int(len(Array))+1
    yy=int(len(Array[0]))+1
    arr_np=np.asarray(arr)
    Array[Array != 0] =225
    Array[Array == 0] =0
    arr_np[1:xx,1:yy]=Array
    Array=arr_np
    Array=Array.astype(np.uint8)
    contours, hierarchy = cv2.findContours(Array,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # Array内にNDVとDVの二値化を作成
    # findContoursで無効値と有効値の輪郭を出している。

    obsArea_i=0
    obsArea=0
    for i in range(len(contours)):
    	area=cv2.contourArea(contours[i]);#輪郭の面積
    	if area>=obsArea:#輪郭の面積が0以上かどうかの判定
    		obsArea_i=i#面積が0以上の輪郭の数


    corners=0
    width = 0.011

    while corners < 4:
    	width = width - 0.001
    	epsilon = width*cv2.arcLength(contours[obsArea_i],True)
    	approx = cv2.approxPolyDP(contours[obsArea_i],epsilon,True)
    	corners = len(approx)

    test_list=[]

    for x,y in approx[:,0]:
    	xi=x-1
    	yi=y-1
    	test_list.append([xi,yi])

    Lbl_path_sub=file_path.rstrip('.tif')+'.LBL'
    lblpvl=pvl.load(Lbl_path_sub).items()
    # 同じディレクトリ内にある.LBLファイルから欲しい値を取得している。

    # print("test_list[0][0]")
    # print(test_list[0][0])
    # print("test_list[0][1]")
    # print(test_list[0][1])
    # print()
    # print("test_list[1][0]"test_list[1][0])
    # print()
    # print("test_list[1][1]"test_list[1][1])
    # print("##################")
    # print("test_list[2][0]"test_list[2][0])
    # print("test_list[2][1]"test_list[2][1])
    # print("##################")
    # print("test_list[3][0]"test_list[3][0])
    # print("test_list[3][1]"test_list[3][1])
    # print("##################")

    center_lat=lblpvl[16][1][9][1][0] #配列が特殊だが、これで.LBL内のデータを取得できる。
    # print("##################")
    # print(center_lat)
    center_lon=lblpvl[16][1][10][1][0]
    # print("##################")
    # print(center_lon)
    a_axis=lblpvl[16][1][3][1][0]
    # print("##################")
    # print(a_axis)
    c_axis=lblpvl[16][1][5][1][0]
    # print("##################")
    # print(c_axis)
    # print("##################")
    a=float(c_axis*math.cos(center_lat))
    b=float(a_axis*math.sin(center_lat))
    R=float(a_axis*c_axis/math.sqrt(a*a+b*b))
    # print(a)
    # print(b)
    # print(R)
    # print("##################")
    # lat=test_list[0][1]/R
    # lon=center_lon+test_list[0][0]/(R*math.cos(center_lat))
    # # lat=math.degrees(lat)
    # # lon=math.degrees(lon)
    # polygon="[[{0:.6f}, {1:.6F}]".format(lon,lat)
    #
    # lat1=test_list[1][1]/R
    # lon1=center_lon+test_list[1][1]/(R*math.cos(center_lat))
    # # lat1=math.degrees(lat1)
    # # lon1=math.degrees(lon1)
    # polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon1,lat1)
    #
    # lat2=test_list[2][1]/R
    # lon2=center_lon+test_list[2][0]/(R*math.cos(center_lat))
    # # lat2=math.degrees(lat2)
    # # lon2=math.degrees(lon2)
    # polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon2,lat2)
    #
    # lat3=test_list[3][1]/R
    # lon3=center_lon+test_list[3][0]/(R*math.cos(center_lat))
    # # lat3=math.degrees(lat3)
    # # lon3=math.degrees(lon3)
    # polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon3,lat3)


    Scale=lblpvl[16][1][17][1][0]/1000
    L0=-lblpvl[16][1][20][1][0]
    S0=lblpvl[16][1][21][1][0]
    # print(Scale)
    # print(S0)
    # print(L0)
    # print("##################")
    # Sample=test_list[0][0]/Scale+S0+1
    # Line=-test_list[0][1]/Scale-L0+1
    # Sample=test_list[0][0]
    # Line=test_list[0][1]
    Sample=test_list[0][0]
    Line=test_list[0][1]
    # print(Sample)
    # print(Line)
    # print("##################")
    lat=(1-L0-Line)*Scale/R

    # P=math.sqrt(test_list[0][0]*test_list[0][0]+test_list[0][1]*test_list[0][1])
    # C=2*math.atan(P/2*c_axis)
    # lat=math.asin(math.cos(math.radians(C))*math.sin(math.radians(center_lat))+test_list[0][1]*math.sin(math.radians(C))*math.cos(math.radians(center_lat))/P)

    lon=math.radians(center_lon)+(Sample-S0-1)*Scale/(R*math.cos(math.radians(center_lat)))

    lat=math.degrees(lat)
    lon=math.degrees(lon)
    # if(test_list[0][0]==0):
    #     lon=center_lon+math.atan(0)
    #
    # else :
    #     lon=center_lon+math.atan(test_list[0][0]/test_list[0][1])
    # lon=center_lon+math.atan(0)

    polygon="[[{0:.6f}, {1:.6F}]".format(lon,lat)

    # Sample=test_list[1][0]/Scale+S0+1
    # Line=-test_list[1][1]/Scale-L0+1
    # Sample=test_list[1][0]
    # Line=test_list[1][1]
    Sample=test_list[1][0]
    Line=test_list[1][1]
    # print(Sample)
    # print(Line)
    # print("##################")
    lat=(1-L0-Line)*Scale/R

    # P=math.sqrt(test_list[1][0]*test_list[1][0]+test_list[1][1]*test_list[1][1])
    # C=2*math.atan(P/2*c_axis)
    # lat=math.asin(math.cos(math.radians(C))*math.sin(math.radians(center_lat))+test_list[1][1]*math.sin(math.radians(C))*math.cos(math.radians(center_lat))/P)

    lon=math.radians(center_lon)+(Sample-S0-1)*Scale/(R*math.cos(math.radians(center_lat)))

    lat=math.degrees(lat)
    lon=math.degrees(lon)
    # if(test_list[1][0]==0):
    #     lon=center_lon+math.atan(0)
    #
    # else :
    #     lon=center_lon+math.atan(test_list[1][0]/test_list[1][1])
    #

    polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon,lat)

    # Sample=test_list[2][0]/Scale+S0+1
    # Line=-test_list[2][1]/Scale-L0+1
    # Sample=test_list[2][0]
    # Line=test_list[2][1]
    Sample=test_list[2][0]
    Line=test_list[2][1]
    # print(Sample)
    # print(Line)
    # print("##################")
    lat=(1-L0-Line)*Scale/R

    # P=math.sqrt(test_list[2][0]*test_list[2][0]+test_list[2][1]*test_list[2][1])
    # C=2*math.atan(P/2*c_axis)
    # lat=math.asin(math.cos(math.radians(C))*math.sin(math.radians(center_lat))+test_list[2][1]*math.sin(math.radians(C))*math.cos(math.radians(center_lat))/P)

    lon=math.radians(center_lon)+(Sample-S0-1)*Scale/(R*math.cos(math.radians(center_lat)))

    lat=math.degrees(lat)
    lon=math.degrees(lon)

    # if(test_list[2][0]==0):
    #     lon=center_lon+math.atan(0)
    #
    # else :
    #     lon=center_lon+math.atan(test_list[2][0]/test_list[2][1])

    polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon,lat)

    # Sample=test_list[3][0]/Scale+S0+1
    # Line=-test_list[3][1]/Scale-L0+1
    # Sample=test_list[3][0]
    # Line=test_list[3][1]
    Sample=test_list[3][0]
    Line=test_list[3][1]
    # print(Sample)
    # print(Line)
    # print("##################")
    lat=(1-L0-Line)*Scale/R

    # P=math.sqrt(test_list[3][0]*test_list[3][0]+test_list[3][1]*test_list[3][1])
    # C=2*math.atan(P/2*c_axis)
    # lat=math.asin(math.cos(math.radians(C))*math.sin(math.radians(center_lat))+test_list[3][1]*math.sin(math.radians(C))*math.cos(math.radians(center_lat))/P)

    lon=math.radians(center_lon)+(Sample-S0-1)*Scale/(R*math.cos(math.radians(center_lat)))

    lat=math.degrees(lat)
    lon=math.degrees(lon)

    # if(test_list[3][0]==0):
    #     lon=center_lon+math.atan(0)
    #
    # else :
    #     lon=center_lon+math.atan(test_list[3][0]/test_list[3][1])

    polygon=polygon+"[[{0:.6f}, {1:.6F}]".format(lon,lat)

    bound_flag=2
    return polygon, bound_flag

    # footprint作成のための四隅の緯度経度を出している。出し方は、このデータ固有のものになっている。



if __name__ == '__main__':
    if sys.argv[1]:
        file_path = sys.argv[1]
    else:
        print("please set a arg which is dataset(themis, crism...).")
        exit()
    # データの入力されていない場合、エラー処理。

    if os.path.exists(file_path):
        polygon_data = dtm_polygon(file_path)
        print(polygon_data)
    else:
        print("file not exist.")
        exit()

