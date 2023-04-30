#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:48:43 2022

@author: suzanne
"""
import re, sys, os, shutil
import numpy as np
import pandas as pd
from scipy import interpolate, stats, signal
from collections import deque
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor

from matplotlib.widgets import Button
from matplotlib.text import Annotation
from mpl_point_clicker import clicker
import CalculateDepths as CD
import UpTempO_BuoyMaster as BM
import UpTempO_PlotsLevel2 as uplotsL2

from functools import reduce
import ProcessFields as pfields
sys.path.append('/Users/suzanne/git_repos/polarstereo-lonlat-convert-py/polar_convert')
# from polar_convert.constants import NORTH
# from polar_convert import polar_lonlat_to_xy
import netCDF4 as nc
from scipy.signal import medfilt
from scipy.optimize import curve_fit
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime as dt
# from waterIce import getL1, getL2, plotL1vL2, getOPbias, getBuoyIce, getRidging, getRidgeDates
from waterIce import *
from haversine import haversine

cList=['k','purple','blue','deepskyblue','cyan','limegreen','darkorange','red'] #'lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

# assign paths. L2 data brought in for comparison
L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'
figspath = '/Users/suzanne/Google Drive/UpTempO/level2'

###### make buoy name-number an argument
# 
# buoys that need conversion
# bid = '300234060340370'   # 2014 11   2 pres   was lost, but now is found, ridging
# bid = '300234060236150'   # 2014 13   3 pres   was lost, but now is found, ridging
# bid = '300234062491420'   # 2016 04
# bid = '300234063991680'   # 2016 07   3 pres
# bid = '300234064737080'   # 2017 04
# bid = '300234068514830'   # 2019 01  SIZRS short string OP at 20m (not the normal 25m), ridging
# bid = '300234068519450'   # 2019 02  SIZRS 3 pres, ridging
# bid = '300234068719480'   # 2019 03  SIZRS 1 pres, ridging, tilt data
# bid = '300234060320930'   # 2019 04  Mosaic, 1 pres, ridging
# bid = '300234060320940'   # 2019 05   3 pres Mosaic are made by Marlin-Yug 
# # bid = '300234067936870'   # 2019 W9   2 pres Warm buoys are made by PG
# # bid = '300234061160500'   # 2020 01   3 pres Mirai by Marlin-Yug
# bid = '300534060649670'   # 2021 01   4 pres, ridging
# bid = '300534060251600'   # 2021 02   3 pres, ridging
# bid = '300534060051570'   # 2021 03   1 pres, ridging
# bid = '300534062158480'   # 2021 04   salinity ball, no pres
bid = '300534062158460'   # 2021 05   salinity ball, no pres


# buoys already converted and used for writing/testing code. 
# bid = '300234064735100'    # 2018 02  3 pres
# bid = '300234065419120'   # 2017 05   3 pres
# bid = '300234064739080'   # 2017 W6   2 pres
# bid = '300234064734090'   # 2017 W5   1 pres
# bid = '300234063861170'   # 2016 05   3 pres
# bid = '300234061160500'   # 2020 01
# bid = '300234063994900'   # 2016 03 
# bid = '300234063993850'    # 2016 06 
# bid = '300234066712490'    # 2018 01
# bid = '300234064735100'   # pressure no sal
# bid = '300534062158460'     # sal no pressure

binf = BM.BuoyMaster(bid)

# make unique buoy figures path
try:
    figspath = os.path.join(figspath,f'{binf["name"][0]}_{int(binf["name"][1]):02d}')
except:
    figspath = os.path.join(figspath,f'{binf["name"][0]}_{binf["name"][1]}')
if not os.path.exists(figspath):
    os.mkdir(figspath)

try:
    level1File = f'{L1path}/UpTempO_{binf["name"][0]}_{int(binf["name"][1]):02d}_{binf["vessel"]}-FINAL.dat'
except:
    level1File = f'{L1path}/UpTempO_{binf["name"][0]}_{binf["name"][1]}_{binf["vessel"]}-FINAL.dat'
try:
    level2File = f'{L2path}/UTO300234062491420_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'
except:
    level2File = f'{L2path}/UTO_{binf["name"][0]}-{binf["name"][1]}_{bid}_L2.dat'
try:
    level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'
except:
    level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{binf["name"][1]}_{bid}_L2.dat'

if '300234060340370' in bid:   # 2014 11
    dt1 = dt.datetime(2014,8,28)
    dt2 =  dt.datetime(2017,5,7)
    dt2a = dt.datetime(2014,10,15)
if '300234060236150' in bid:   # 2014 13
    dt1 = dt.datetime(2014,9,4)
    dt2 =  dt.datetime(2016,2,4)
    # dt2a = dt.datetime(2014,10,15)
if '300234062491420' in bid:   # 2016 04
    dt1=dt.datetime(2016,8,22)
    dt2=dt.datetime(2016,11,3)
if '300234063861170' in bid:   # 2016 05
    dt1 = dt.datetime(2016,8,31)
    dt2 = dt.datetime(2016,11,1)    
if '300234063991680' in bid:   # 2016 07
    dt1 = dt.datetime(2016,9,4)
    dt2 =  dt.datetime(2016,10,24)
if '300234064737080' in bid:   # 2017 04
    dt1 = dt.datetime(2017,9,10)
    dt2a = dt.datetime(2018,1,15)
    dt2 = dt.datetime(2019,5,19)
if bid in '300234065419120':   # 2017 05
    dt1 = dt.datetime(2017,10,1)
    dt2 = dt.datetime(2017,11,15)
if '300234062491420' in bid:
    dt1 = dt.datetime(2016,8,22)
    dt2 = dt.datetime(2016,11,3)
if '300234064739080' in bid:   # 2017-W6
    dt1 = dt.datetime(2017,3,1)
    dt2 = dt.datetime(2018,3,1)
if bid in '300234064735100':   # 2018 02
    dt1 = dt.datetime(2018,9,18)
    dt2 = dt.datetime(2018,11,5)
if '300234067936870' in bid:  # 2019 W9
    dt1=dt.datetime(2019,4,1)
    dt2=dt.datetime(2019,12,15)
if '300234060320940' in bid:  # 2019 05 Mosaic
    dt1=dt.datetime(2019,10,27)
    dt2=dt.datetime(2020,8,20)
if '300234060320930' in bid:  # 2019 04 Mosaic
    dt1=dt.datetime(2019,10,27)
    dt2=dt.datetime(2020,8,20)
if '300234068719480' in bid:  # 2019 03 SIZRS
    dt1=dt.datetime(2019,9,12)
    dt2=dt.datetime(2019,12,19)
if '300234068519450' in bid:  # 2019 02 SIZRS
    dt1=dt.datetime(2019,8,13)
    dt2=dt.datetime(2022,11,8)
    # dt1=dt.datetime(2019,12,10)  # for looking at ridging time
    # dt2=dt.datetime(2020,1,1)
if '300234068514830' in bid:  # 2019 01 SIZRS
    dt1=dt.datetime(2019,7,30)
    dt2=dt.datetime(2020,11,2)
    dt2a=dt.datetime(2021,8,2)
if '300234061160500' in bid:  # 2020 01 SIZRS
    dt1=dt.datetime(2020,11,10)
    dt2=dt.datetime(2021,10,3)
if '300534060649670' in bid:  # 2021 01 SIZRS
    dt1=dt.datetime(2021,8,24)
    dt2=dt.datetime(2022,2,28)
if '300534060251600' in bid:  # 2021 02 SIZRS
    dt1=dt.datetime(2021,9,14)
    dt2=dt.datetime(2021,12,24)
if '300534060051570' in bid:  # 2021 03 SIZRS
    dt1=dt.datetime(2021,9,29)
    dt2=dt.datetime(2021,11,2)
if '300534062158480' in bid:  # 2021 04 SIZRS
    dt1=dt.datetime(2021,10,12)
    dt2=dt.datetime(2021,10,24)
if '300534062158460' in bid:  # 2021 05 SIZRS
    dt1=dt.datetime(2021,11,1)
    dt2=dt.datetime(2021,11,24)

print('level 1 file',level1File)
f1 = open(level1File,'r')
if bid in ['300234064737080','300234064739080','300234067936870','300234068519450', '300234068514830','300534060251600','300534062897730','300534062894700']:
    ########  2017-04, 2017-W6, 2019_W9, 2019-02, 2019-01, 2021-02, 2022-02, 2022-07
    WrapCorr = 'YES'
else:
    WrapCorr = 'NO'
    
f2 = open(level2Draft,'w')
df1,pdepths,tdepths,sdepths,ddepths,tiltdepths = getL1(level1File,bid,figspath)
print('tdepths',tdepths)
print(len(df1))
print(df1.columns)

# 2019 04,05  track locs in .dat files don't match website
if bid in ['300234060320940','300234060320930','300234068519450']:   
    # 2019-05, 2019-04, 2019-02
    uplotsL2.TrackMaps2Atlantic(bid,figspath)
# exit(-1)
Tcols = [col for col in df1.columns if col.startswith('T') and 'Ta' not in col and 'Tilt' not in col]
#### plot temps individually on their own plot
for ii,tcol in enumerate(Tcols):
    print(tcol,df1.loc[df1[tcol].notna()[::-1].idxmax(),'Dates'],df1.loc[df1[tcol].notna()[::-1].idxmax(),tcol])

plotT = input('Do you want to plot temperatures individually? : y for Yes, n for No ')
if plotT.startswith('y'):
    for ii,tcol in enumerate(Tcols):
        fig,ax = plt.subplots(1,1,figsize=(15,5))
        ax.plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.9,-1.9],'--',color='gray')
        ax.plot(df1['Dates'],df1[tcol],'*',color=colorList[ii],ms=3)
        # ax.plot([dt.datetime(2019,12,13,8,0,0),dt.datetime(2019,12,13,8,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2019,12,16,21,0,0),dt.datetime(2019,12,16,21,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2019,12,17,9,0,0),dt.datetime(2019,12,17,9,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2019,12,27,19,0,0),dt.datetime(2019,12,27,19,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2019,12,29,20,0,0),dt.datetime(2019,12,29,20,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2019,12,30,5,0,0),dt.datetime(2019,12,30,5,0,0)],[0,7],'r--')
        # ax.plot([dt.datetime(2020,3,14,14,0,0),dt.datetime(2020,3,14,14,0,0)],[0,7],'r--')
        # ax.set_title(f'Level 1 {binf["name"][0]}-{int(binf["name"][1]):02d} {tcol}')
        ax.grid()
        # try:
        #     ax.set_xlim([dt1,dt2a])
        # except:
        if bid in ['300234060340370','300234064737080']:
            # 2014-11
            if tcol in 'T0':
                ax.set_xlim([dt1,dt2])
            else:
                ax.set_xlim([dt1,dt2a])
        else:
            ax.set_xlim([dt1,dt2])
        # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))        
        plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{tcol}.png')
        plt.show()

Pcols = [col for col in df1.columns if col.startswith('P')]
#### plot all press on one plot
plotP = input('Do you want to plot pressures all on one figure? : y for Yes, n for No ')
if plotP.startswith('y'):
    fig,ax = plt.subplots(1,1,figsize=(15,5))
    for ii,col in enumerate(Pcols):
        ax.plot(df1['Dates'],-1*df1[col],'*',color=colorList[ii],ms=3)
    ax.set_title(f'Level 1 {binf["name"][0]}-{int(binf["name"][1]):02d} Pressures')
    ax.grid()
    try:
        ax.set_xlim([dt1,dt2a])
    except:
        ax.set_xlim([dt1,dt2])
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_Pressures.png')
    plt.show()
 
Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
#### plot salis individually on their own plot
plotS = input('Do you want to plot salinities individually? : y for Yes, n for No ')
if plotS.startswith('y'):
    for ii,scol in enumerate(Scols):
        fig,ax = plt.subplots(1,1,figsize=(15,5))
        ax.plot(df1['Dates'],df1[scol],'*',color=colorList[ii],ms=3)
        ax.set_title(f'Level 1 {binf["name"][0]}-{int(binf["name"][1]):02d} {scol}')
        ax.grid()
        # try:
        #     ax.set_xlim([dt1,dt2a])
        # except:
        ax.set_xlim([dt1,dt2])
        
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))        
        plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{scol}.png')
        plt.show()


        
# find pressure spikes and invalidate them, interpolate through
print(binf['brand'])
if len(pdepths)>0:
    df1 = removePspikes(bid,df1,pdepths,figspath,brand=binf['brand'],dt1=dt1,dt2=dt2)

print(len(df1.columns))
# start making output .dat file, header is same as LEVEL 1 file
outputCols = {}
lines = f1.readlines()
nn=0
for ii,line in enumerate(lines):
    if line.startswith('%') and '%END' not in line and 'Estimated depth' not in line:
        print('line 284',line)
        if 'Air Temperature' in line and bid in ['300234061160500','300234060340370']:  # ?, 2014 11
            print()
        if 'GPS' in line:
            print()
        else:
            # 
            ColNum = re.findall(r'(\d+) =',line)
            print(ColNum)
            if len(ColNum)>0:
                print(line.split('=',1)[-1])  # split on first instance of '='
                outputCols[nn] = df1.columns[nn]  #int(ColNum[0])
                print(df1.columns[nn],nn)
                newline = f"% {nn} = {line.split('=',1)[-1]}"
                print(newline)
                f2.write(newline)
                nn += 1
            else:
                f2.write(line)
    if '%END' in line:
        break
# nextColNum = int(ColNum[0]) + 1
nextColNum = nn
print('output columns',outputCols)
# f2.close()
# exit(-1)
# # drop columns from L2 that won't be in L2
# print(df1.columns[df1.columns.str.startswith('Dest')])
# df1.drop(df1.columns[df1.columns.str.startswith('Dest')],axis=1,inplace=True)
    
# get indices of tdepths where pdepths in intersects
if len(pdepths)>0 and len(tdepths)>0:
    indT = dict((k,i) for i,k in enumerate(tdepths))
    inter = set(indT).intersection(pdepths)  # intersection of the keys
    indP = sorted([indT[x] for x in inter])  # intersection of the values (indices)
    print('indices of tdepths at pdepths',indP)

# # uncomment if you want to compare to one of Wendy's L2s
# compareL2 = input('Do you want to compare L1 to Wendys L2? : y for Yes, n for No ')
# if compareL2.startswith('y'):
#     df2, pdepths, tdepths, ddepths, sdepths, biodepths = getL2(level2File,bid)
#     print(df2.columns)
#     Pcols = [col for col in df2.columns if col.startswith('P')]
#     Tcols = [col for col in df2.columns if col.startswith('T')]
#     Dcols = [col for col in df2.columns if col.startswith('D') and 'Da' not in col]
    
#     fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
#     for ii,dcol in enumerate(Dcols):
#         ax8.plot(df2['Dates'],-1*df2[dcol],'.',color=colorList[ii],label=f'{tdepths[ii]}')
#     ax8.xaxis.set_major_locator(mdates.DayLocator(interval=10))
#     ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     ax8.grid()
#     ax8.legend(loc='best')
#     ax8.set_xlim(dt1,dt2)
#     try:
#         ax8.set_title(f'Calculated Depths Wendy Level2 {binf["name"][0]}_{int(binf["name"][1]):02d}')
#         fig8.savefig(f'{figspath}/CalculatedDepths_WendyL2_{binf["name"][0]}_{int(binf["name"][1]):02d}.png')
#     except:
#         ax8.set_title(f'Calculated Depths Wendy Level2 {binf["name"][0]}_{binf["name"][1]}')
#         fig8.savefig(f'{figspath}/CalculatedDepths_WendyL2_{binf["name"][0]}_{binf["name"][1]}.png')
#     plt.show()

#     fig1,ax1 = plt.subplots(1,1,figsize=(25,10))
#     for ii,pcol in enumerate(Pcols):
#         ax1.plot(df2['Dates'],-1*df2[pcol],'.-',color='lightgray')
#     ax1.set_xlim([df2['Dates'].iloc[0],df1['Dates'].iloc[-1]])
#     ax1.set_ylabel('Ocean Pressure',color='lightgray',fontsize=14)
#     secax=ax1.twinx()
#     secax.spines['right'].set_color('blue')
#     secax.set_ylabel('Temperatures',color='b',fontsize=14)
#     secax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
#     secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
#     for ii,tcol in enumerate(Tcols):
#         print(ii,tcol)
#         secax.plot(df2['Dates'],df2[tcol],color=colorList[ii],alpha=0.7,label=f'{tdepths[ii]}')
#     secax.legend()  
#     secax.set_ylim([-25,15])    
#     secax.grid()  
#     try:
#         ax1.set_xlim([dt1,dt2a])
#     except:
#         ax1.set_xlim([dt1,dt2])
            
#     fig1.savefig(f'{figspath}/PressureTemperature_WendyL2.png')
#     plt.show()


# inventory columns, make calculated depth columns
Pcols = [col for col in df1.columns if col.startswith('P')]
Tcols = [col for col in df1.columns if col.startswith('T') and not col.startswith('Tilt')]
Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
if Pcols:
    Dcols = [f'D{col[1:]}' for col in df1.columns if col.startswith('T') and not col.startswith('Tilt')]
    # Dcols = [f'D{col[1:]}' for col in df1.columns if col.startswith('D') and not col.startswith('Dest')]
Tiltcols = [col for col in df1.columns if col.startswith('Tilt')]
print(Pcols)
print(Tcols)
print(Scols)
if Pcols:
    print(Dcols)
print(Tiltcols)
print('pdepths',pdepths)
print('tdepths',tdepths)
print('sdepths',sdepths)
print('ddepths',ddepths)
print('tiltdepths',tiltdepths)
print()

# df1['FirstTpod'] = df1.apply(lambda row: (row[Tcols].gt(-1.9).idxmax()[1:]),axis=1)
# df1['sst'] = df1.apply(lambda row: (row[Tcols[int(row['FirstTpod'])]]),axis=1)


### find and remove Ocean pressure bias
if len(pdepths)>0:
    try:
        biasname = f'{figspath}/OPbias_{binf["name"][0]}_{int(binf["name"][1]):02d}.csv'
    except:
        biasname = f'{figspath}/OPbias_{binf["name"][0]}_{binf["name"][1]}.csv'

    findBias = input('Do you want to find ocean pressure biases?  (y for Yes, n for No) ')
    if findBias.startswith('y'):
        global coords
        OPbias=[]
        # automatically saves when finding bias(es)
        dfbias = pd.DataFrame(columns=['pdepths','OPbias'])
        for ii,pcol in enumerate(Pcols):
            # df1 pressure columns are 'corrected for bias' and returned 
            df1, bias = getOPbias(pcol,pdepths[ii],df1,bid,figspath)
            OPbias.append(bias)  # this is for writing to L2 file ???
        print(f'ocean pressure biases:{[bias for bias in OPbias]}')
        dfbias['pdepths'] = pdepths
        dfbias['OPbias'] = OPbias
        dfbias['Pcols'] = Pcols
        dfbias.to_csv(biasname,float_format='%.2f')
    else:
        if bid == '300234067936870':   # 2019 W9
            dfbias = pd.DataFrame(columns=['pdepths','OPbias'])
            dfbias['pdepths'] = pdepths
            dfbias['OPbias'] = 0.0
        else:
            dfbias = pd.read_csv(biasname)
            OPbias = dfbias['OPbias']
            # plot pressures before and after, to check.  Apply the bias
            for ii,pcol in enumerate(dfbias['Pcols']):
                fig,ax = plt.subplots(1,1,figsize=(15,5))
                ax.plot(df1['Dates'],-1*df1[pcol],'r.')
                df1[pcol] -= dfbias['OPbias'].iloc[ii]
                ax.plot(df1['Dates'],-1*df1[pcol],'b.')
                ax.grid()
                ax.set_title(f'{pcol} before(r) and after(b) bias correction of {dfbias["OPbias"].iloc[ii]:.2f}')
                fig.savefig(f'{figspath}/{pcol}_biasCorrection.png')
                plt.show()
    if len(dfbias['OPbias']) == 0:
        print('You need a bias to continue')
        exit(-1)

# when pressure is deeper than nominal, set it to nominal, except for WARM buoys
if len(pdepths)>0:
    if not binf['name'][1].startswith('W'): 
        fig,ax = plt.subplots(len(Pcols),1,figsize=(15,3*len(Pcols)),sharex=True)
        if len(Pcols)==1:
            df1.loc[(df1['P1']>pdepths[0]),'P1'] = pdepths[0]
            ax.plot(df1['Dates'],-1*df1[pcol],'.-')
            ax.set_title(f'Bias corrected Pressures, nominal depth {int(pdepths[ii])}',fontsize=16)
            ax.grid()
        else:    
            for ii,pcol in enumerate(Pcols):
                print(ii,pcol)
                df1.loc[(df1[pcol]>pdepths[ii]),pcol] = pdepths[ii]
                ax[ii].plot(df1['Dates'],-1*df1[pcol],'.-')
                ax[ii].set_title(f'Bias corrected Pressures, nominal depth {int(pdepths[ii])}',fontsize=16)
                ax[ii].grid()
        plt.savefig(f'{figspath}/PresSetDeeper2Nominal.png')
        plt.show()
    
print(df1.columns)

fig1,ax1 = plt.subplots(1,1,figsize=(25,10))
for ii,pcol in enumerate(Pcols):
    ax1.plot(df1['Dates'],-1*df1[pcol],'.-',color='lightgray')
ax1.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
ax1.set_ylabel('Ocean Pressure',color='lightgray',fontsize=14)
secax=ax1.twinx()
secax.spines['right'].set_color('blue')
secax.set_ylabel('Temperatures (b), WaterIce(r)',color='b',fontsize=14)
if '300234068519450' in bid:
    secax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
else:
    secax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
for ii,tcol in enumerate(Tcols):
    print(ii,tcol)
    secax.plot(df1['Dates'],df1[tcol],color=colorList[ii],alpha=0.7,label=f'{tdepths[ii]}')
secax.plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.8,-1.8],'--',color='gray')
secax.legend()  
secax.set_ylim([-25,15])    
secax.grid() 
try:    
    ax1.set_xlim([dt1,dt2a])
except:
    ax1.set_xlim([dt1,dt2])

# make column for Water/Ice indicator (before depths)
df1['WaterIce'] = np.nan

# depth column values to NaNs
if len(pdepths)>0:
    for col in Dcols:
        df1[col] = np.nan
    df1['D0'] = 0.0
print('line 340',df1.columns)

### determine water/ice
print('Determining Water/Ice values')
IceInd = 'YES'
indicator = []
mindist = []

for index, row in df1.iterrows():
    indi,mind = getBuoyIce(df1['Lon'].iloc[index],df1['Lat'].iloc[index],
                            df1['Year'].iloc[index],df1['Month'].iloc[index],df1['Day'].iloc[index],
                            df1['T0'].iloc[index],plott=0,bid=bid,figspath=figspath)
    indicator.append(indi)
    mindist.append(mind/1000) # in km

# df1.insert(nextColNum,'WaterIce',indicator)
df1['WaterIce'] = indicator
secax.plot(df1['Dates'],df1['WaterIce'],'r')
fig1.savefig(f'{figspath}/PressureTemperature.png')
plt.show()

# fig3,ax3 = plt.subplots(4,1,figsize=(15,15),sharex=True)
# ax3[0].plot(df1['Dates'],df1['WaterIce'])
# ax3[0].set_title('Water Ice indicator (1=ice, 2=water)')
# ax3[1].plot(df1['Dates'],df1['T0'])
# ax3[1].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.8,-1.8],'r')
# ax3[1].set_title('T0')

print(df1.columns)

# df1['mindist'] = mindist
f2.write(f'% {nextColNum} =  Open Water or Ice Indicator (1=ice, 2=water)\n')
nextColNum += 1
print(nextColNum)

# find FWT based on temperatures, straight up
FirstTpodInd = 'YES'
SSTInd = 'YES'

if '300234068519450' in bid:   # 2019 02
    fig88,ax88 = plt.subplots(1,1,figsize=(15,5))
    ax88.plot(df1['Dates'],-1*df1['P1'],'.-',color='gray')
    secax = ax88.twinx()
    secax.plot(df1['Dates'],df1['T2'],'.-',color=cList[2])
    secax.plot(df1['Dates'],df1['T3'],'.-',color=cList[3])
    ax88.set_title('P1(gray), T2(darker blue), T3(lighter blue)')
    plt.show()

# assume no ridging, unless we answer yes to questions below
df1['ridged'] = 0

if len(pdepths)>0:
    fig0,ax0 = plt.subplots(1,1,figsize=(15,5))
    ax0.plot(df1['Dates'],-1*df1['P1'],'b.-')
    ax0.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
    ax0.set_ylabel('Pressure',color='b')
    
    secax=ax0.twinx()
    secax.spines['right'].set_color('red')
    # secax.set_ylim(940.0,1080)
    secax.set_ylabel('Water(2), Ice(1)',color='r')
    secax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    secax.plot(df1['Dates'],df1['WaterIce'],color='r',alpha=0.7)
    ax0.set_xlim([dt1,dt2])
    ax0.set_title(f'Ocean Pressure nominal depth {pdepths[0]} (b), Water(2)/Ice(1) indicator (r)')
    ax0.grid()
    fig0.savefig(f'{figspath}/P1_WaterIce.png')
    # plt.show()

# find ridging times (besides indicated by Water/Ice indicator), put on .csv file
iceday = input('Do you want to look at ice conc to find ridging times? : y for Yes, n for No ')
if iceday.startswith('y'):
    icedate = input('which day? (in yyyymmdd format) ')
    strdate,ice,icexx,iceyy = pfields.getICE(icedate,src='g02202') # default is nsicd-0081 (nrt)
    # print(dt1,dt2)
    icecolors=['0.4','0.5','0.6','0.725','0.85','1.0']
    icelevels=[0.2,0.3,0.4,0.5,0.75]

    fig1, ax1 = plt.subplots(1,figsize=(8.3,10))
    ax1 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
    ax1.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
    ax1.add_feature(cfeature.LAND,facecolor='gray')
    # ax1.add_feature(cfeature.OCEAN,facecolor='lightblue')
    ax1.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
    kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
    # both of these set_extent commands work well
    # ax1.set_extent([-180,180,65,90],crs=ccrs.PlateCarree())
    ax1.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
    ax1.contourf(icexx,iceyy,ice, colors=icecolors, levels=icelevels, vmin=0, vmax=0.9, extend='both',
                          transform=ccrs.Stereographic(**kw))
    # ax1.plot(df1.loc[(df1['Dates']>=dt1) & (df1['Dates']<=dt2),'Lon'],
    #          df1.loc[(df1['Dates']>=dt1) & (df1['Dates']<=dt2),'Lat'],'r.',transform=ccrs.PlateCarree())
    ax1.plot(df1['Lon'],df1['Lat'],'r.',transform=ccrs.PlateCarree())
    ax1.plot(df1.loc[(df1['Dates']>=dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:]))) &
                     (df1['Dates']<=dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:])+1)),'Lon'],
             df1.loc[(df1['Dates']>=dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:]))) &
                     (df1['Dates']<=dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:])+1)),'Lat'],
                     'b.',transform=ccrs.PlateCarree())
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    ax1.set_title(f'IceConc and track(b) on {dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:]))}. Red shows entire track.')
    fig1.savefig(f'{figspath}/IceConc_Buoytrack_{icedate}.png')
    plt.show()
    exit(-1)

# find riding times (besides indicated by Water/Ice indicator), put in .csv file
rTimes = input('Do you want to make ridging time periods file? : y for Yes, n for No ')
if rTimes.startswith('y'):
    fig1,ax1 = plt.subplots(len(Pcols),1,figsize=(15,3*len(Pcols)),sharex=True)
    for ii,ax in enumerate(np.array(ax1).reshape(-1)):  # allows the looping on one subplot
        ax.plot(df1['Dates'],-1*df1[Pcols[ii]],'b.-')
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
        ax.grid()
    if bid == '300234068719480':   # 2019 03
        ax1.set_xlim([dt.datetime(2019,12,1),dt.datetime(2019,12,19)])
    if bid == '300234060320930':   # 2019 04
        ax1.set_xlim([dt.datetime(2020,6,30),dt.datetime(2020,8,2)])
    plt.show()
    # exit(-1)


rFile = input('Do you want to READ ridging time periods file? : y for Yes, n for No ')
if rFile.startswith('y'):
    ridgeFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridging{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'
    dfr = pd.read_csv(ridgeFile)
    dfr['dt1'] = pd.to_datetime(dfr['dt1'],format='%m/%d/%y %H:%M')
    dfr['dt2'] = pd.to_datetime(dfr['dt2'],format='%m/%d/%y %H:%M')
    dfr.dropna(axis=0,how='all',inplace=True)
    print(dfr)
    print(len(dfr))

    # plot to ensure the ridged areas
    rcols = ['m','c','r','g','orange','k','m','c','r','g','orange','k','m','c','r','g','orange','k','m','c','r','g','orange','k']
    # fig3,ax3 = plt.subplots(4,1,figsize=(15,12),sharex=True)
    # ax3[0].plot(df1['Dates'],-1*df1['P1'],'b.')

    df1['ridged'] = 0  # make columns pertaining to ridging
    df1['ridgedPressure'] = pdepths[0]
    fig0,ax0 = plt.subplots(len(Pcols),1,figsize=(15,3*len(Pcols)),sharex=True)
    # secax0=ax0.twinx()
    for jj,ax in enumerate(np.array(ax0).reshape(-1)):  # allows the looping on one subplot
        # print('line 533',jj,pcol)
        ax.plot(df1['Dates'],-1*df1[Pcols[jj]],'b.-')
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
        ax.grid()
        secax=ax.twinx()
        secax.spines['right'].set_color('red')
        secax.set_ylabel('Water(2), Ice(1)',color='r')
        secax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
        secax.plot(df1['Dates'],df1['WaterIce'],color='r',alpha=0.7)
        for ii,row in dfr.iterrows():      
            print(ii,row,pdepths[0],pdepths[jj])
            ridgedAmount = pdepths[0]-dfr['OPlimit'].iloc[ii]
            if '300534060649670' in bid and ii==len(dfr)-1 and jj>0:
                ridgedAmount = 8.7
            ax.plot(df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'Dates'],
                    -1*df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),Pcols[jj]],
                    '.',color=rcols[ii])
            ax.plot([dfr['dt1'].iloc[ii],dfr['dt2'].iloc[ii]],[-1*(pdepths[jj]-ridgedAmount),-1*(pdepths[jj]-ridgedAmount)],'k')
            df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridged'] = 1
            df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridgedPressure'] = dfr['OPlimit'].iloc[ii]
        ax.set_yticks(np.arange(np.floor(-1*df1[Pcols[jj]].max()),np.ceil(-1*df1[Pcols[jj]].min()),1))
        ax.set_title(f'OP corrected for bias {Pcols[jj]}, colors for ridge levels')
    fig0.savefig(f'{figspath}/P1_WaterIce_ridging.png')
    
plt.show()


if 'ridgedPressure' in df1.columns:
    try:
        ridgedPresFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridgedPressure{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'
    except:
        ridgedPresFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridgedPressure{binf["name"][0]}-{binf["name"][1]}.csv'
            
    # apply ridged pressures at times of ridging
    df1['ridgedPressure'] = -1*pdepths[-1]
    for ii in range(len(dfr)):
        df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridgedPressure'] = dfr['OPlimit'][ii]

# to determine if buoy is dragging on ocean bottom
# set dragging variable
df1['dragging'] = 0
df1['bathymetry'] = np.nan
#  get bathymetry along the track and plot
df1 = getBuoyBathyPoint(df1)

# plot buoy track over bathymetry.    SUZANNE add bathymetry
fig2, ax2 = plt.subplots(1,figsize=(8.3,10))
ax2 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
ax2.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
ax2.add_feature(cfeature.LAND,facecolor='gray')
ax2.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
ax2.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
# ch = ax2.scatter(df1.loc[(df1['bathymetry']>=-75),'Lon'],
#                  df1.loc[(df1['bathymetry']>=-75),'Lat'],s=5,
#                c=df1.loc[(df1['bathymetry']>=-75),'bathymetry'],cmap='turbo',
#                transform=ccrs.PlateCarree(),vmin=-75,vmax=0) #norm=mpl.colors.LogNorm(vmin=0,vmax=20))
ch = ax2.scatter(df1['Lon'],df1['Lat'],s=5,c=df1['bathymetry'],cmap='turbo',
               transform=ccrs.PlateCarree()) #norm=mpl.colors.LogNorm(vmin=0,vmax=20))
fig2.colorbar(ch,ax=ax2)
ax2.set_title('Bathymetry along track')
fig2.savefig(f'{figspath}/Bathymetry_track.png')
    

if len(pdepths)>0:
    fig0,ax0 = plt.subplots(1,1,figsize=(15,5))
    ax0.plot(df1['Dates'],-1*df1[Pcols[-1]],'b.-')
    ax0.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
    ax0.set_ylabel('Ocean Pressure',color='b',fontsize=14)

    secax=ax0.twinx()
    secax.spines['right'].set_color('red')
    # secax.set_ylim(940.0,1080)
    secax.set_ylabel('Bathymetry',color='r',fontsize=14)
    secax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    for pdepth in pdepths:
        secax.plot([dt1,dt2],[-1*pdepth,-1*pdepth],'k--')
    secax.plot(df1['Dates'],df1['bathymetry'],color='r',alpha=0.7)
    
    ax0.set_xlim([dt1,dt2])
    ax0.set_title(f'Ocean Pressure nominal depth {pdepths[-1]} (b), Bathymetry (GEBCO 2019) (r)',fontsize=15)
    ax0.grid()
    fig0.savefig(f'{figspath}/P1_Bathymetry.png')
    plt.show()      
else:
    fig0,ax0 = plt.subplots(1,1,figsize=(15,5))
    secax=ax0.twinx()
    secax.spines['right'].set_color('red')
    secax.set_ylabel('Bathymetry',color='r',fontsize=14)
    secax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    secax.plot(df1['Dates'],df1['bathymetry'],color='r',alpha=0.7)
    
    ax0.set_xlim([dt1,dt2])
    ax0.set_title(f'Bathymetry (GEBCO 2019) (r)',fontsize=15)
    ax0.grid()
    fig0.savefig(f'{figspath}/Bathymetry_timeSeries.png')
    plt.show()      
    
    
startdrag = input('Enter start date of dragging as yyyymmdd (press return if None)')
enddrag = input('Enter end date of dragging as yyyymmdd (press return if None)')
if '300234064737080' in bid:
    startdrag = '20170916'
    enddrag   = '20170923'
print(startdrag)
print(enddrag)
# if startdrag is not None and enddrag is not None:
if startdrag and enddrag:
    df1.loc[(df1['Dates']>=startdrag) & (df1['Dates']<=enddrag),'dragging'] = 1
    fig3,ax3 = plt.subplots(1,1,figsize=(15,5))
    ax3.plot(df1['Dates'],-1*df1['P1'],'b')
    secax=ax3.twinx()
    secax.spines['right'].set_color('red')
    secax.set_ylabel('Dragging indicator',color='r',fontsize=14)
    secax.plot(df1['Dates'],df1['dragging'],'r*')  
# plt.show()


### calculate thermistor depths
if len(pdepths)>0:
    print('Interpolating calculated depths...')
    Pcols.insert(0,'D0')
    pdepths.insert(0,0.0)
    tcalcdepths=np.full([len(df1),len(tdepths)],np.nan)
    print('tcalc depths shape',tcalcdepths.shape)
    print('Pcols',Pcols)
    print(pdepths)

    for ii, row in df1.iterrows():
        pmeas = [df1[col].iloc[ii] for col in Pcols]
        valid = np.where(~np.isnan(pmeas))[0].tolist()
                   
        if len(valid)<2:  # meaning we only have pmeas=0, the rest NaNs
            tcalcdepths[ii,:] = np.nan
            tcalcdepths[ii,0] = 0
            # print(pmeas)
            # print(tcalcdepths[ii,:])
            # print(df1['Dates'].iloc[ii])
        else:
            if not df1['ridged'].iloc[ii] and not df1['dragging'].iloc[ii]:
                fi = interpolate.interp1d([pdepths[i] for i in valid],[pmeas[i] for i in valid],fill_value = 'extrapolate')            
                tcalcdepths[ii,:] = fi(tdepths)
                
            elif df1['ridged'].iloc[ii]:
                # deepestZero = df1['FirstTpod'].iloc[ii]
                ridgedAmount = pdepths[1] - df1['ridgedPressure'].iloc[ii]
                pdepthsRidged = [pdepth-ridgedAmount for pdepth in pdepths[1:]]
                pdepthsRidged.insert(0,0)
                tdepthsRidged = [x - ridgedAmount for x in tdepths]  
                deepestZero = tdepthsRidged.index
                print(df1['Dates'].iloc[ii],ridgedAmount,pdepthsRidged,tdepthsRidged)
                # print(deepestZero)
    
                if '300534060649670' in bid and df1['Dates'].iloc[ii]>=dt.datetime(2022,1,12,23,0,0):  # two levels of riding
                    pdepthsRidged = [pdepth-8.8 for pdepth in pdepths[-2:]]
                    pdepthsRidged.insert(0, pdepths[1] - df1['ridgedPressure'].iloc[ii])
                    pmeas = [df1['P1'].iloc[ii],df1['P3'].iloc[ii],df1['P4'].iloc[ii]]
                    tdepthsRidged = [tdepth-8.8 for tdepth in tdepths[-3:]]
                    tdepthsRidged.insert(0, tdepths[2] - df1['ridgedPressure'].iloc[ii])
                    fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')
                    tcalcdepths[ii,4:] = fi(tdepthsRidged)
                    tcalcdepths[ii,:2] = tdepths[0]
                    tcalcdepths[ii,2:4] = tcalcdepths[ii,4]
                    # fig,ax = plt.subplots(1,1,figsize=(6,8))
                    # ax.plot(-1*np.array(tdepths),-1*tcalcdepths[ii,:],'o-')
                    # ax.plot(-1*tdepths[2],-1*tcalcdepths[ii,2],'ro')
                    # ax.plot(-1*tdepths[6],-1*tcalcdepths[ii,6],'ro')
                    # ax.plot(-1*tdepths[7],-1*tcalcdepths[ii,7],'ro')
                    # ax.grid()
                    # ax.set_xlabel('Nominal thermistor depths')
                    # ax.set_ylabel('Measured(r), calculated(b) thermistor depths')
                    # plt.show()
                    # exit(-1)
                else:

                    fi = interpolate.interp1d([pdepthsRidged[i] for i in valid],[pmeas[i] for i in valid],fill_value = 'extrapolate')
                    # tcalcdepths[ii,:] = fi(tdepthsRidged)
                    # print('tcalcdepths',tcalcdepths[ii,:])
                    # tcalcdepths[ii,:deepestZero] = tdepths[0]
                    tcalc = fi(tdepthsRidged)
                    tcalc[tcalc<0] = tdepths[0]
                    tcalcdepths[ii,:] = tcalc
                    print('tcalcdepths',tcalcdepths[ii,:])
                  # tcalcdepths[ii,:deepestZero] = tdepths[0]
                  #   tcalcdepths[ii,0] = tdepths[0]   # re-apply in case deepestZero is zero (near open water, but pressure is ridged)
                
            elif df1['dragging'].iloc[ii]:
                dragged = len(tdepths) - len([x for x in tdepths if x>df1['P1'].iloc[ii]])
                tcalcdepths[ii,dragged:] = df1['P1'].iloc[ii]
                # print(ii,df1['P1'].iloc[ii])
                # print(dragged)
                # print(tcalcdepths[ii,:])
                if dragged < len(tdepths)-1:
                    pdepthsDragging = [tdepths[dragged]]
                    pdepthsDragging.insert(0,0)
                    fi = interpolate.interp1d(pdepthsDragging,pmeas,fill_value = 'extrapolate')
                    tcalcdepths[ii,:dragged+1] = fi(tdepths[:dragged+1])
                else:
                   fi = interpolate.interp1d(pdepths,pmeas,fill_value = 'extrapolate')
                   tinvolved = tdepths
                   tcalcdepths[ii,:] = fi(tinvolved)
                
    tcalcdepths = np.array(tcalcdepths)
    print(tcalcdepths.shape)
    print(Dcols)
    print(tdepths)
    CalcDepths = 'YES'
else:
    CalcDepths = 'NO'

# remove extremely warm temperatures
if len(pdepths)>0:
    for tcol,dcol in zip(Tcols,Dcols):
        df1.loc[(df1[tcol]>10) & (df1[dcol]<20),tcol] = np.nan
        

print('line 772',df1.head())
print()
if len(pdepths)>0: 
    for ii,dcol in enumerate(Dcols):
        df1[dcol] = tcalcdepths[:,ii]
        f2.write(f'% {nextColNum} =  Calculated Depth at nominal depth {tdepths[ii]} (m)\n')
        nextColNum += 1

    fig10,ax10 = plt.subplots(2,1,sharex=True)
    dfD = df1[[col for col in Dcols]]
    # dfDslice = dfD[:2500]
    # ch10 = ax10[0].imshow(dfDslice.T.to_numpy())
    ch10 = ax10[0].imshow(dfD.T.to_numpy())
    ax10[0].set_title('depths')
    ax10[0].set_aspect('auto')
    fig10.colorbar(ch10,ax=ax10[0])

    dfT = df1[[col for col in Tcols]]
    dfTslice = dfT[:2500]
    ch10 = ax10[1].imshow(dfTslice.T.to_numpy())
    # dfTslice = dfT[:2500]
    # ch10 = ax10[0].imshow(dfTslice.T.to_numpy())
    ch10 = ax10[1].imshow(dfT.T.to_numpy())
    ax10[1].set_title('temps')
    ax10[1].set_aspect('auto')
    fig10.colorbar(ch10,ax=ax10[1])
    fig10.savefig(f'{figspath}/TempsDepths_np.arrays.png')
    plt.show()
    
    # fig,ax = plt.subplots(2,1,figsize=(10,6),sharex=True)
    # for dcol,tcol in zip(Dcols,Tcols):
    #     ax[0].plot(df1['Dates'].iloc[2500],df1[tcol].iloc[2500])
    #     ax[0].xaxis.set_major_locator(mdates.DayLocator(interval=2))
    #     ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #     ax[1].plot(df1['Dates'].iloc[2500],-1*df1[dcol].iloc[2500])
    # exit(-1)
    # removing temperature spikes
    # Tsp = input('Do you want to remove T spikes? : y for Yes, n for No ')
    # if Tsp.startswith('y'):
        
        ###
  ##############  # df1 = removeTspikes(bid,df1,tdepths,figspath)


# if buoy is a 'salinity ball', there is only hull temperature
if bid in ['300534062158480','300534062158460']:
#            2021 04           2021 05
    df1['FirstTpod'] = 0
    df1['sst'] = df1['T0']
    df1['Dsst'] = tdepths[0]
    df1.loc[(df1['sst']<-1.9),['FWT','sst','Dsst']] = np.nan


else:
    # FWT is first thermistor reading warmer than freezing as you go down the chain
    df1['FirstTpod'] = df1.apply(lambda row: (int(row[Tcols].gt(-1.9).idxmax()[1:])),axis=1)
    # if FWT = 0, but W/I says we're near ice, set FWT=1
    df1.loc[(df1['FirstTpod']==0) & (df1['WaterIce']==1),'FirstTpod'] = 1
    
    # if ridging, can't use ridged thermistors.
    try:
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
    except:
        pass
    
    # when T0 look reasonable (not on ice, not in melt pond on summer ice, not in air)
    if bid in '300234060340370':   #2014 11
        # use T0 before ridging
        df1.loc[(df1['Dates']<dt.datetime(2014,9,16,9,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        # summer 2015
        df1.loc[(df1['Dates']>=dt.datetime(2015,9,15,0,0,0)) & (df1['Dates']<=dt.datetime(2015,10,4,6,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        # summer 2016
        df1.loc[(df1['Dates']>=dt.datetime(2016,8,16,6,0,0)) & (df1['Dates']<=dt.datetime(2016,9,1,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0

    if bid in '300234060236150':   #2014 13
        # use T0 before ridging
        df1.loc[(df1['Dates']<dt.datetime(2014,10,12,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        # use T0 after ridging
        df1.loc[(df1['Dates']>dt.datetime(2014,10,25,23,0,0)) & (df1['Dates']<dt.datetime(2014,11,15)) & (df1['T0']>-1.9),'FirstTpod'] = 0
    
    if bid in '300234063991680':   # 2016 07
        df1.loc[(df1['Dates']<dt.datetime(2016,11,23)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        df1.loc[(df1['Dates']>=dt.datetime(2017,8,8,6,0,0)) & (df1['Dates']<dt.datetime(2017,10,9,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        df1.loc[(df1['Dates']>=dt.datetime(2018,7,27,6,0,0)) & (df1['Dates']<dt.datetime(2018,9,23,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        df1.loc[(df1['Dates']>=dt.datetime(2019,7,31,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        
    if bid in '300234062491420':   # 2016 04
        df1.loc[(df1['Dates']<dt.datetime(2016,11,14,12,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        df1.loc[(df1['Dates']>=dt.datetime(2017,8,1,21,0,0)) & (df1['Dates']<dt.datetime(2017,11,30)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        
    if bid in '300234064737080':   # 2017 04
        df1.loc[(df1['Dates']<=dt.datetime(2017,11,20)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        df1.loc[(df1['Dates']>=dt.datetime(2018,8,15,14,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
            
    if bid in '300234060320940':   # 2019 05 
        df1['FirstTpod'] = 1       # T0 temps too warm to be in water
        # df1.loc[(df1['Dates']>=dt.datetime(2020,8,9,9,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0  # except at end
        
    if bid in '300234060320930':   # 2019 04
        # can't use T1 during ridging
        df1.loc[(df1['Dates']>=dt.datetime(2020,7,11,23,0,0)),'FirstTpod'] = 2
        
    if bid in '300234068719480':   # 2019 03
       df1.loc[(df1['Dates']<=dt.datetime(2019,12,5)) & (df1['T0']>-1.9),'FirstTpod'] = 0
       # Ensure that SST comes from no 'ridged' thermistors, there are a couple of points that aren't ridged within the ridging, but we'll use T1 for SST anyway
       # df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
       df1.loc[(df1['Dates']>=dt.datetime(2019,12,1,17,0,0)),'FirstTpod'] = 1
       
    if bid in '300234068519450':   # 2019 02
        # Ensure that SST comes from no 'ridged' thermistors
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
        # manual edit around ridging, summer 2019
        df1.loc[(df1['Dates']<=dt.datetime(2019,12,3)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        # summer 2020
        df1.loc[(df1['Dates']>=dt.datetime(2020,7,28,8,0,0)) & (df1['Dates']<=dt.datetime(2020,10,23)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        # summer 2021, use T4 for all
        # summer 2022
        df1.loc[(df1['Dates']>=dt.datetime(2022,9,13,6,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0

    if bid in '300234068514830':   # 2019 01
        # Ensure that SST comes from no 'ridged' thermistors
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
        # manual edit.
        df1.loc[(df1['Dates']<=dt.datetime(2019,12,28,18,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0
        
    if bid in '300534060649670':   # 2021 01
        df1.loc[(df1['Dates']<=dt.datetime(2021,10,16,17,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0  
        # Ensure that SST comes from no 'ridged' thermistors
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
        
    if bid in '300534060251600':   # 2021 02
        df1.loc[(df1['Dates']<=dt.datetime(2021,10,13,23,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0  
        # Ensure that SST comes from no 'ridged' thermistors
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
        
    if bid in '300534060051570':   # 2021 03
        # before ridging
        df1.loc[(df1['Dates']<dt.datetime(2021,10,16,15,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0  
        # after ridging
        df1.loc[(df1['Dates']>dt.datetime(2021,10,20,18,0,0)) & (df1['T0']>-1.9),'FirstTpod'] = 0  
        # Ensure that SST comes from no 'ridged' thermistors
        df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
    
    
    # sst is the temperature from the FWT
    df1['sst'] = df1.apply(lambda row: (row[Tcols[int(row['FirstTpod'])]]),axis=1)
    df1.loc[(df1['sst']<-1.9),'sst'] = np.nan
    print('line 951 wtf')
    # if sst is invalid, look down the chain for the next good value.
    for ii,row in df1.iterrows():
        if df1['sst'].isnull().iloc[ii]:
            while df1['sst'].isnull().iloc[ii] and df1['FirstTpod'].iloc[ii]<len(tdepths)-1:
                # print(ii,df1['Dates'].loc[ii],pdepths[1]-df1['ridgedPressure'].iloc[ii])
                # print(df1['sst'].iloc[ii],df1['FirstTpod'].iloc[ii])
                # print()
                df1['FirstTpod'].iloc[ii] += 1
                df1['sst'].iloc[ii] = df1[Tcols[df1['FirstTpod'].iloc[ii]]].iloc[ii]
                if df1['sst'].iloc[ii] < -1.9:
                    df1['sst'].iloc[ii] = np.nan
                # if df1['Dates'].loc[ii]>=dt.datetime(2022,2,5): # and df1['Dates'].loc[ii]<=dt.datetime(2020,3,14):
                #     print(df1['Dates'].loc[ii],df1['sst'].iloc[ii],df1['FirstTpod'].iloc[ii],df1['T3'].iloc[ii],df1['T5'].iloc[ii])
                #     input('Press enter to continue...')
                #     print()
    
    # set depth of SST to depth of FWT
    df1['Dsst'] = df1.apply(lambda row: (row[Dcols[int(row['FirstTpod'])]]),axis=1)
    if bid in '300234061160500':   # 2020 01
        df1.loc[(df1['Dsst']==0),'FirstTpod'] = 2  # assuming T1 is in ice
        df1['sst'] = df1.apply(lambda row: (row[Tcols[int(row['FirstTpod'])]]),axis=1)
        df1['Dsst'] = df1.apply(lambda row: (row[Dcols[int(row['FirstTpod'])]]),axis=1)
        
    # for some reason T0<-1.9 sneak through.
    df1.loc[(df1['sst']<-1.9),['FirstTpod','sst','Dsst']] = np.nan
    # if there are no valid temperature data at the FWT, set FWT and depth to invalid as well
    df1.loc[(df1['sst'].isnull()),['FirstTpod','Dsst']] = np.nan
    # ax.plot(df1['Dates'],df1['FirstTpod'],'.')
    plt.show()
    print(df1['sst'].min())
    print(df1.loc[(df1['sst']<-1.9),'Dates'])

fig45,ax45 = plt.subplots(4,1,figsize=(15,10),sharex=True)
for ii,col in enumerate(Tcols):
    if ii<6:
        ax45[0].plot(df1['Dates'],df1[col],'*',color=colorList[ii],ms=3)
        if ii==0:
          ax45[0].plot(df1['Dates'],df1[col],'*-',color=colorList[ii],ms=3)  
# plot T0 on top so we can see it
ax45[0].plot(df1['Dates'],df1[Tcols[0]],'*-',color=colorList[0],ms=3) 
ax45[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.9,-1.9],'--',color='gray')
secax = ax45[0].twinx()
secax.plot(df1['Dates'],df1['WaterIce'],'r')
secax.set_ylim([0.8,2.2])
ax45[0].set_title(f'Buoy {binf["name"][0]}_{int(binf["name"][1]):02d} Temperatures (left), Water/Ice indicator (right)')

ax45[1].plot(df1['Dates'],df1['FirstTpod'],'.')
try:
    for ii,row in dfr.iterrows():
        ax45[1].plot([dfr['dt1'].iloc[ii],dfr['dt1'].iloc[ii]],[0,5],'r--')
        ax45[1].plot([dfr['dt2'].iloc[ii],dfr['dt2'].iloc[ii]],[0,5],'r--')
except:
    pass
ax45[1].set_title('FWT')

ax45[2].plot(df1['Dates'],df1['sst'],'.')
ax45[2].set_title('SST')
ax45[2].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.9,-1.9],'--',color='gray')

ax45[3].plot(df1['Dates'],-1*df1['Dsst'],'rd')
ax45[3].set_ylabel('depth of SST')
ax45[3].set_title('Depth of SST (red), measured P1 (gray)')
# ax45[3].xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax45[3].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax45[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# if 'P1' in df1.columns:
#     secax3 = ax45[3].twinx()
#     secax3.plot(df1['Dates'],-1*df1['P1'],'.',color='gray')
#     secax3.set_ylabel('Measured Pressure')

fig45.savefig(f'{figspath}/TempsWI_FWT_SST_Dsst.png')
plt.show()
# exit(-1)


try:
    fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
    for ii,dcol in enumerate(Dcols):
        ax8.plot(df2['Dates'],-1*df2[dcol],'.',color=colorList[ii],label=f'{tdepths[ii]}')
    ax8.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # ax8.set_yticks(np.arange(-26,1))
    ax8.set_title('Wendy s calculated depths ')
    ax8.grid()
    ax8.legend(loc='lower center')
    ax8.set_xlim(dt1,dt2)
except NameError:
    pass

if len(pdepths)>0:
    fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
    for ii,dcol in enumerate(Dcols):
        ax8.plot(df1['Dates'],-1*df1[dcol],'.-',color=colorList[ii],label=f'{tdepths[ii]}')
    ax8.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # ax8.set_xlim([dt.datetime(2019,12,8),dt.datetime(2019,12,10)])
    # ax8.set_yticks(np.arange(-26,1))
    try:
        ax8.set_title(f'Calculated Depths {binf["name"][0]}-{int(binf["name"][1]):02d}')
    except:
        ax8.set_title(f'Calculated Depths {binf["name"][0]}-{binf["name"][1]}')
        
    ax8.grid()
    ax8.legend(loc='best')
    ax8.set_xlim(dt1,dt2)
    try:
        fig8.savefig(f'{figspath}/CalcDepths_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    except:
        fig8.savefig(f'{figspath}/CalcDepths_{binf["name"][0]}-{binf["name"][1]}.png')
    

# remove columns no longer needed
if 'dragging' in df1.columns:
    df1.drop(columns=['dragging'],inplace=True)
if 'bathymetry' in df1.columns:
    df1.drop(columns=['bathymetry'],inplace=True)
if 'ridgedPressure' in df1.columns:
    df1.drop(columns=['ridgedPressure'],inplace=True)
if 'GPSquality' in df1.columns:
    df1.drop(columns=['GPSquality'],inplace=True)
if 'FWT' in df1.columns:
    df1.drop(columns=['FWT'],inplace=True)
df1.drop(columns=['ridged'],inplace=True) 

print(df1.columns)
print()
print(df1.head())

OPcorr4SLP = 'NO'
OPcorr4drift = 'NO'
Capped999 = 'YES'    
DataFilt = 'YES'
f2.write(f'% {nextColNum} =  First Wet Thermistor\n')
f2.write(f'% {nextColNum+1} =  Sea Surface Temperature\n')
f2.write(f'% {nextColNum+2} =  Sea Surface Temperature Depth\n')
f2.write(f'%\n')
f2.write(f'%LEVEL 2 Quality Control Modifications:\n')
f2.write(f'%For definitions and details about these modifications visit: psc.apl.washington.edu/UpTempO/Level2_QC_doc.php\n')
f2.write(f'% BUOY QC\n')
f2.write(f'%1. Sensor Bias\n')
f2.write(f'%    Ocean Pressure Sensors\n')
print()
print()
print('line 750')
print(pdepths)
print(Pcols)
for ii,pcol in enumerate(Pcols[1:]):
    f2.write(f'%        {int(pdepths[ii+1])}m OP sensor: subtracted  {OPbias[ii]:.2f} dB from Level 1 data\n')
f2.write(f'%        Ocean Pressure Values corrected for SLP? {OPcorr4SLP}\n')
f2.write(f'%    Thermistor Values\n')
if bid in ['300234060320940','300234060320930']:  # 2019 05, 2019 04  
    f2.write(f'%        Bias of 0.2C added to temperature data\n')
else:
    f2.write(f'%        Overall bias and std not available\n')
f2.write(f'%2. Sensor Drift\n')
f2.write(f'%    Ocean Pressure Values corrected for drift? {OPcorr4drift}\n')
f2.write(f'%3. Range Checks\n')
f2.write(f'%    Capped and Unphysical Values set to -999? {Capped999}\n')
f2.write(f'%    Wrap correction needed and applied      ? {WrapCorr}\n')
f2.write(f'%4. Miscellaneous\n')
f2.write(f'%    Data filtered for noisy values, initial adjustment, steady values, and spikes? {DataFilt}\n')
f2.write(f'% ADDED QUANTITIES\n')
f2.write(f'%    Open Water/Ice indicator              ? {IceInd}\n')
f2.write(f'%    Calculated Depths for thermistors     ? {CalcDepths}\n')
f2.write(f'%    First Wet Thermistor Indicator        ? {FirstTpodInd}\n')
f2.write(f'%    Sea Surface Temperature Determination ? {SSTInd}\n')
f2.write(f'%    Sea Surface Temperature Depth (m)     ? {SSTInd}\n')

if bid in '300234060340370':   # 2014 11
    f2.write(f'%  NOTE: Air Temperature data in Level1 file empty so no column in Level2 file.\n')
if bid in '300234064737080':   # 2017-04 
    f2.write(f'%  NOTE: Abrupt decrease in pressure in Sep, 2017 due to buoy dragging on ocean bottom.\n')
    f2.write(f'%  NOTE: Not sure what is going on with the decrease in pressure in Oct, 2017. Treating it as a wind event.\n')
if bid in '300234060320930':   # 2019 04  Mosaic
    f2.write(f'%  NOTE: No position data were reported by this buoy. The lat/lon position data in this file were interpolated from the concurrently deployed buoy WMO 300234067707750.\n')
if bid in '300234060320940':   # 2019-05 
    f2.write(f'%  NOTE: Hull temperatures (T0 values) are all very warm and highly variable when the Water/Ice indicator says open water. This is solar heating of the buoy hull. SST set to T1.\n')
    f2.write(f'%  NOTE: No position data were reported by this buoy. The lat/lon position data in this file were interpolated from the concurrently deployed buoy WMO 300234067705760.\n')
elif bid in '300534060649670':   # 2021 01 
    f2.write(f'%  NOTE: Ridging after mid-Januray 2022 is ~3m for P1 and ~9m for P3 and P4. It is assumed T2, T3 and T4 are knotted up with P1. The sensors deeper in the water column hang down from there.\n')
    f2.write(f'%  NOTE: Temperature and Salinity data from sensor at 10m nominal depth all suspect. Set to invalid.\n')
f2.write(f'END\n')

print('line 773')
print(df1.columns)
# plot L2 similar to L1 in waterIce.py, getL1
remcols = []
for col in df1.columns:
    fig,ax = plt.subplots(1,1,figsize=(15,5))
    if col.startswith('P'):
        ax.plot(df1['Dates'],-1*df1[col],'.')
    elif 'Lat' in col:
        if '300234064737080' in bid:
            df1.loc[(df1['Lon'])<0,'Lon'] += 360
        ax.plot(df1['Lon'],df1[col],'.')
        ax.plot(df1['Lon'].iloc[0],df1[col].iloc[0],'go')
        ax.plot(df1['Lon'].iloc[-1],df1[col].iloc[-1],'ro')
    elif 'Lon' in col:
        remcols.append(col)
        
    elif 'T0' in col:
        for ii,tcol in enumerate(Tcols):
            ax.plot(df1['Dates'],df1[tcol],'o',color=colorList[ii],ms=1)
    elif col.startswith('T') and 'T0' not in col:
        remcols.append(col)
        
    elif 'S0' in col:
        for ii,scol in enumerate(Scols):
            ax.plot(df1['Dates'],df1[scol],'o',color=colorList[ii],ms=1)
    elif col.startswith('S') and 'S0' not in col and not 'SUB' in col:
        remcols.append(col)
        
    elif 'D0' in col:
        for ii,dcol in enumerate(Dcols):
            ax.plot(df1['Dates'],-1*df1[dcol],'o',color=colorList[ii],ms=1)
    elif col.startswith('D') and 'D0' not in col and 'Day' not in col and 'Dsst' not in col:
        remcols.append(col)
        
    elif 'Tilt0' in col:
        for ii,tiltcol in enumerate(Tiltcols):
            ax.plot(df1['Dates'],df1[tiltcol],'o',color=colorList[ii],ms=1)
    elif col.startswith('Tilt') and 'Tilt0' not in col:
        remcols.append(col)
        
    elif 'Dsst' in col:
        ax.plot(df1['Dates'],-1*df1[col],'.')
        ax.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
    else:
        ax.plot(df1['Dates'],df1[col],'.')
        if col in ['WaterIce','FirstTpod','sst']:
            ax.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
    if 'Year' in col:
        try:
            ax.set_title(f'Level 2 {binf["name"][0]}-{int(binf["name"][1]):02d} {col}, Number of Data {len(df1)}')
        except:
            ax.set_title(f'Level 2 {binf["name"][0]}-{binf["name"][1]} {col}, Number of Data {len(df1)}')
    else:
        try:
            ax.set_title(f'Level 2 {binf["name"][0]}-{int(binf["name"][1]):02d} {col}')
        except:
            ax.set_title(f'Level 2 {binf["name"][0]}-{binf["name"][1]} {col}')
    ax.grid()
    try:
        plt.savefig(f'{figspath}/L2_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}.png')
    except:
        plt.savefig(f'{figspath}/L2_{binf["name"][0]}_{binf["name"][1]}_{col}.png')
    plt.show()
for col in remcols:
    try:
        os.remove(f'{figspath}/L2_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}.png')
    except:
        os.remove(f'{figspath}/L2_{binf["name"][0]}_{binf["name"][1]}_{col}.png')

print('df1 columns before outputing',df1.columns)

df1.drop(columns=['Dates'],inplace=True)
if 'D0SLP' in df1.keys():
    df1.drop(columns=[dcol for dcol in DcolsSLP],inplace=True)
print('df1 columns ready for outputing',df1.columns)

# write data to .csv for making webplots, including nominal depths
df1['tdepths'] = np.NaN
df1['tdepths'].iloc[:len(tdepths)] = tdepths
if len(sdepths)>0:
    df1['sdepths'] = np.NaN
    df1['sdepths'].iloc[:len(sdepths)] = sdepths
if len(pdepths)>0:
    df1['pdepths'] = np.NaN
    df1['pdepths'].iloc[:len(pdepths)] = pdepths
if len(tiltdepths)>0:
    df1['tiltdepths'] = np.NaN
    df1['tiltdepths'].iloc[:len(tiltdepths)] = tiltdepths
df1.to_csv(f'{figspath}/QualityControlled_{bid}.csv', float_format='%.4f', index=False)

# make new plots for website with QCd data
uplotsL2.TimeSeriesPlots(bid,figspath)
df1.drop(columns=['tdepths'],inplace=True)
if 'sdepths' in df1.columns:
    uplotsL2.TimeSeriesPlots(bid,figspath,quan='Salinity')
    df1.drop(columns=['sdepths'],inplace=True)
if 'pdepths' in df1.columns:
    uplotsL2.TimeSeriesPlots(bid,figspath,quan='Pressure')
    df1.drop(columns=['pdepths'],inplace=True)
if 'tiltdepths' in df1.columns:
    uplotsL2.TimeSeriesPlots(bid,figspath,quan='Tilt')
    df1.drop(columns=['tiltdepths'],inplace=True)
if 'SUB' or 'BATT' in df1.columns:
    uplotsL2.Batt_Sub(bid,figspath)
# if '300234064737080' in bid:
#     df1.loc[(df1['Lon'])>360,'Lon'] -= 360
#     print('line 973',df1['Lon'].max(),df1['Lon'].min())
uplotsL2.VelocitySeries(bid,figspath)

# 2019 04,05  track locs in .dat files don't match website
if bid in ['300234060320940','300234060320930','300234068519450']:   
    # 2019-05, 2019-04, 2019-02
    uplotsL2.TrackMaps2Atlantic(bid,figspath)
    
# convert NaNs back to -999.
df1.fillna(-999.,inplace=True)
if df1.isnull().values.any():
    print(df1.isnull().values.sum())

# write data columns to L2.dat file
data = df1.to_numpy()
np.savetxt(f2,data,fmt='%.4f')
f1.close()
f2.close()

exit(-1)







mergedf = pd.merge(df1,df2,how='inner', on=['Dates'])
print(mergedf.columns)
