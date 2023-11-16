#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 10:31:35 2023

@author: suzanne
"""

import os, re
import pandas as pd
import numpy as np
import UpTempO_BuoyMaster as BM
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import islice
import statistics
import itertools

figs_path = '/Users/suzanne/Google Drive/UpTempO/level2/Nov2023'
level2_path = '/Users/suzanne/Google Drive/UpTempO/level2'
colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','gold','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
last = 'Nov2023'

buoyIDs = ['300234060340370',   # 2014 11   2 pres   was lost, but now is found, ridging
           '300234060236150',   # 2014 13   3 pres   was lost, but now is found, ridging
           '300234062491420',   # 2016 04
           '300234063991680',   # 2016 07   3 pres
           '300234064737080',   # 2017 04

           '300234067936870',   # 2019 W9   1 pres Warm buoys are made by PG
           '300234068514830',   # 2019 01  SIZRS short string OP at 20m (not the normal 25m), ridging
           '300234068519450',   # 2019 02  SIZRS 3 pres, ridging
           '300234068719480',   # 2019 03  SIZRS 1 pres, ridging, tilt data
           '300234060320930',   # 2019 04  Mosaic, 1 pres, ridging
           '300234060320940',   # 2019 05   3 pres Mosaic are made by Marlin-Yug 

           '300234061160500',   # 2020 01   3 pres Mirai by Marlin-Yug

           '300534060649670',   # 2021 01   4 pres, ridging
           '300534060251600',   # 2021 02   3 pres, ridging
           '300534060051570',   # 2021 03   1 pres, ridging
           '300534062158480',   # 2021 04   salinity ball, no pres
           '300534062158460',   # 2021 05   salinity ball, no pres

            '300534062898720',  # 2022 01  SASSIE
           # '300534062897730',  # 2022 02  SASSIE
            '300534063704980',  # 2022 03  SASSIE  long
            '300534063807110',  # 2022 04  SASSIE
            '300534063803100',  # 2022 05  SASSIE  long
            '300534062892700',  # 2022 06  SASSIE  no pressures
           # '300534062894700',  # 2022 07  SASSIE  no pressures
           # '300534062894740',  # 2022 08  SASSIE
           # '300534062896730',  # 2022 09  SASSIE  long
            '300534062894730',  # 2022 10  SASSIE
            '300534062893700',  # 2022 11  SASSIE
           # '300534062895730',  # 2022 12  SIZRS 3 press

            '300434064041440',  # 2023 01  NOAA 
            '300434064042420',  # 2023 02  NOAA 
            '300434064046720',  # 2023 03  NOAA 
            '300434064042710',  # 2023 04  NOAA 
           # '300534062891690',  # 2023 05 Healy
           # '300534062893740',  # 2023 06 Healy
           # '300534062895700',  # 2023 07 Healy
           # '300534063449630',  # 2023 08 Mirai
            '300434064040440',  # 2023 09 NOAA
           # '300434064048220',  # 2023 10 NOAA
           # '300434064044730',  # 2023 11 NOAA
           # '300434064045210'  # 2023 12 NOAA
           # '300534062897690'  # 2023 13 SIZRS
           ]


generalEdits = ['DuplicateRows','InitialAdjustment','BuoyLocationsFlagged']
# generalEdits = {}
# dataCriteria = ['WrappedTemperatures','TemperaturesTooWarm20','TemperaturesTooWarmDeep','TemperaturesTooWarmWinter',
#                 'ConstantValue','OtherUnphysicalValues','PressureSpikesReplaced','TemperatureSpikesRemoved',]
# dataEdits = {}


numP,numT,numS = 0,0,0
for ii,bid in enumerate(buoyIDs):
    # if ii<2:
        binf = BM.BuoyMaster(bid)
        try:
            name = f'{binf["name"][0]}_{int(binf["name"][1]):02d}'
        except:
            name = f'{binf["name"][0]}_{binf["name"][1]}'
        efile = os.path.join(level2_path,f'{name}/EditingStats_{name}.csv') 
           
        dfEdit = pd.read_csv(efile, index_col=0)
        print(dfEdit.head(15))
        if dfEdit.loc['Processed'].lt(0).any(axis=0):
            print(f'Buoy {name} has some negative processed values')
            exit()
            
        # added composite stats columns
        dfEdit[['sumGeo','maxValue']] = np.nan
        
        if ii==0:
            dfAll= pd.DataFrame(columns=[name])
         
        Pcols = [col for col in dfEdit.columns if col.startswith('P')]
        Tcols = [col for col in dfEdit.columns if col.startswith('T')]
        Scols = [col for col in dfEdit.columns if col.startswith('S')]
        PTScols = list(itertools.chain(*[Pcols,Tcols,Scols]))  # columns to sum
        # print('len',len(PTScols))

        Gedits = ['DuplicateRows','InitialAdjustment','BuoyLocationsFlagged']
        # Tedits = [ed for ed in dfEdit.index if 'Temperature' in ed]
        # Pedits = [ed for ed in dfEdit.index if 'Pressure' in ed]
        # Oedits = ['RawActual','BuoyLocationsFlagged','ConstantValue','OtherUnphysicalValues']
        # initialCounts = dfEdit.index[:3]
        Aedits = dfEdit.index  #[3:]
        dfEdit.loc[Aedits,'sumGeo'] = dfEdit.loc[Aedits,PTScols].sum(axis=1)
        dfEdit.loc[Gedits,'sumGeo'] = dfEdit.loc[Gedits,'Lat']
        dfAll[name] = dfEdit['sumGeo']

print(dfAll.head(15))
dfAll.to_csv(f'{figs_path}/AllStatsSum.csv',float_format='%.0f',index=False)
        # exit()
# names = [col for col in dfAll.columns]
# nullFig='nullFig'
for editname in dfAll.index:
    print(editname)
    # print(dfAll.loc[[editname]].max(axis=1))
    # print(dfAll.loc[[editname]])
    # exit(-1)
    fig,ax = plt.subplots(1,1,figsize=(20,8))
    ax.grid(color='lightsteelblue')
    eras = ['historical','2019','2020','2021','2022','2023']
    erasX = [1,6.8,10.65,13.5,19.5,26]
    bnds = [4.5,10.5,11.5,16.5,23.5]
    
    ax.text(erasX[0],dfAll.loc[[editname]].max(axis=1)*1.1,eras[0],fontsize=10)    
    for ii,(bnd,era) in enumerate(zip(bnds,eras[1:])):
        ax.plot([bnd,bnd],[0,dfAll.loc[[editname]].max(axis=1)*1.1],color='tan',linewidth=3)
        ax.text(erasX[ii+1], dfAll.loc[[editname]].max(axis=1)*1.1,era,fontsize=10)
    
        if 'Processed' in editname:
            ax.plot(dfAll.loc[['RawActual']].T,'o-',color='lightgray',markersize=10)
            
        ax.plot(dfAll.loc[[editname]].T,'o-',color='navy',markersize=10)
        
        if 'RawActual' in editname:
             ax.set_title('RawActual = Raw - Duplicate Rows - InitialAdjustment',fontsize=14)
        else:
            ax.set_title(editname,fontsize=14)
 
    plt.xticks(rotation=90)
    plt.savefig(f'{figs_path}/{editname}.png')
    plt.show()
    # exit()






# ax.plot(names,np.array([generalEdits[name]['BLFpercentage'] for name in names]),'o-',markersize=16)
# ax.set_title('BuoyLocationsFlagged over (Raw-InitialAdustment-DuplicateRow): percentage',fontsize=24)
# ax.axvspan(names[names.index('2021_01')],names[-3],color='g',alpha=0.2)
# ax.set_ylabel('% buoy locations flagged',fontsize=20)
# ax.grid()
# ax.text(names[0],9.5,f"mean {statistics.mean(np.array([generalEdits[name]['BLFpercentage'] for name in names])):.2f}",fontsize=16)
# ax.text(names[0],9.0,f"median {statistics.median(np.array([generalEdits[name]['BLFpercentage'] for name in names])):.2f}",fontsize=16)
# ax.text(names[0],8.5,f"stdev {statistics.stdev(np.array([generalEdits[name]['BLFpercentage'] for name in names])):.2f}",fontsize=16)
# plt.xticks(rotation=60,ha='right')
# plt.show()
# exit()
# dfBig = pd.DataFrame(columns=['Mean','Median','StandardDeviation'])

# loc = np.array([generalEdits[name]['BuoyLocationsFlagged'] for name in generalEdits.keys()])
# dfBig.loc['BuoyLocationsFlagged'] = [statistics.mean(loc),statistics.median(loc),statistics.stdev(loc)]
# # adj = np.array([generalEdits[name]['InitialAdjustment'] for name in generalEdits.keys()])
# # dfBig.loc['InitialAdjustment'] = [statistics.mean(adj),statistics.median(adj),statistics.stdev(adj)]
# # dup = np.array([generalEdits[name]['DuplicateRows'] for name in generalEdits.keys()])
# # dfBig.loc['DuplicateRows'] = [statistics.mean(dup),statistics.median(dup),statistics.stdev(dup)]
# print(dfBig.head())

# fig,ax = plt.subplots(3,1,figsize=(20,8),sharex=True)
# ax[0].plot(generalEdits.keys(),loc,'bo-',markersize=10);ax[0].grid()
# ax[1].plot(generalEdits.keys(),adj,'bo-',markersize=10);ax[1].grid()
# ax[2].plot(generalEdits.keys(),dup,'bo-',markersize=10);ax[2].grid()
# ax[0].set_title('Number of BuoyLocationsFlagged(top), InitialAdjustment(mid), DuplicateRows(bot) for each buoy',fontsize=25)
# plt.xticks(rotation=60,ha='right')
# fig.savefig(f'{level2_path}/BuoyLocationsFlagged_DuplicateRows_{last}.jpg')

# fig,ax = plt.subplots(2,1,figsize=(20,8),sharex=True)
# raw = np.array([generalEdits[name]['Raw'] for name in generalEdits.keys()])
# proc= np.array([generalEdits[name]['Processed'] for name in generalEdits.keys()])
# ax[0].plot(generalEdits.keys(),raw,'bo-',markersize=10);ax[0].grid()
# ax[0].set_title('Raw number of data points for each buoy')
# ax[1].plot(generalEdits.keys(),proc/raw*100,'bo-',markersize=10);ax[1].grid()
# ax[1].set_title('Percentage of data points processed for each buoy',fontsize=25)
# plt.xticks(rotation=60,ha='right')
# fig.savefig(f'{level2_path}/Raw_Processed_{last}.jpg')

# # unphysical values
# psum = np.zeros([len(name),])
# praw = np.zeros([len(name),])
# figP,axP = plt.subplots(numP+1,1,figsize=(20,12),sharex=True)
# for ii in range(numP):
#     pun = np.array([dataEdits[name]['UnphysicalValues'][f'P{ii+1}'] if f'P{ii+1}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()])
#     psum = np.nansum([pun,psum],axis=0)
    
#     pra = np.array([dataEdits[name]['Raw'][f'P{ii+1}'] if f'P{ii+1}' in dataEdits[name]['Raw'].keys() else np.nan for name in generalEdits.keys()])
#     praw = np.nansum([pra,praw],axis=0)
    
#     axP[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#     axP[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#     axP[ii].set_title(f'UnphysicalValues for P{ii+1}')
#     axP[ii].grid()
#     plt.xticks(rotation=60,ha='right')
# axP[ii+1].plot(name,psum/praw *100,'d-',color=colorList[ii],markersize=12)
# figP.savefig(f'{level2_path}/UnphysicalValues_pressures_{last}.jpg')



# plt.show()
# exit()

# # temperature spikes removed
# figT,axT = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numT):
#     pun = [dataEdits[name]['TemperatureSpikesRemoved'][f'T{ii}'] if f'T{ii}' in dataEdits[name]['TemperatureSpikesRemoved'].keys() else np.nan for name in generalEdits.keys()]
#     print(pun)
#     if ii<4:
#         axT[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#         axT[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#         axT[ii].set_title(f'TemperatureSpikesRemoved for T{ii}')
#         axT[ii].grid()
#         plt.xticks(rotation=60,ha='right')
#     else:
#         axT[3].plot(name,pun,'o-',color=colorList[ii],markersize=12+2-ii)
#         axT[3].set_title(f'TemperatureSpikesRemoved for T3 to deepest')
# figT.savefig(f'{level2_path}/TemperatureSpikesRemoved_temperatures_{last}.jpg')

# # pressure spikes replaced
# figP,axP = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numP):
#     pun = [dataEdits[name]['PressureSpikesReplaced'][f'P{ii+1}'] if f'P{ii+1}' in dataEdits[name]['PressureSpikesReplaced'].keys() else np.nan for name in generalEdits.keys()]
#     axP[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#     axP[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#     axP[ii].set_title(f'PressureSpikesReplaced for P{ii+1}')
#     axP[ii].grid()
#     plt.xticks(rotation=60,ha='right')
# figP.savefig(f'{level2_path}/PressureSpikesReplaced_pressures_{last}.jpg')



# plt.show()
# exit()




# # unphysical values
# figP,axP = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numP):
#     pun = [dataEdits[name]['UnphysicalValues'][f'P{ii+1}'] if f'P{ii+1}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()]
#     axP[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#     axP[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#     axP[ii].set_title(f'UnphysicalValues for P{ii+1}')
#     axP[ii].grid()
#     plt.xticks(rotation=60,ha='right')
# figP.savefig(f'{level2_path}/UnphysicalValues_pressures_{last}.jpg')

# figP,axP = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numP):
#     pun = [dataEdits[name]['UnphysicalValues'][f'P{ii+1}'] if f'P{ii+1}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()]
#     axP[ii].plot(name[1:],pun[1:],'o-',color=colorList[ii],markersize=12)
#     axP[ii].set_xlim(name[1],name[-1])
#     axP[ii].set_title(f'UnphysicalValues for P{ii+1}')
#     axP[ii].grid()
#     plt.xticks(rotation=60,ha='right')
# figP.savefig(f'{level2_path}/UnphysicalValues_pressures_{last}_not2014_11.jpg')

# figT,axT = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numT):
#     pun = [dataEdits[name]['UnphysicalValues'][f'T{ii}'] if f'T{ii}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()]
#     print(pun)
#     if ii<4:
#         axT[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#         axT[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#         axT[ii].set_title(f'UnphysicalValues for T{ii}')
#         axT[ii].grid()
#         plt.xticks(rotation=60,ha='right')
#     else:
#         axT[3].plot(name,pun,'o-',color=colorList[ii],markersize=12+2-ii)
#         axT[3].set_title(f'UnphysicalValues for T3 to deepest')
# figT.savefig(f'{level2_path}/UnphysicalValues_temperatures_{last}.jpg')

# figT,axT = plt.subplots(numP,1,figsize=(20,8),sharex=True)
# for ii in range(numT):
#     pun = [dataEdits[name]['UnphysicalValues'][f'T{ii}'] if f'T{ii}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()]
#     print(pun)
#     if ii<4:
#         axT[ii].plot(name[1:],pun[1:],'o-',color=colorList[ii],markersize=12)
#         axT[ii].set_xlim(name[1],name[-1])
#         axT[ii].set_title(f'UnphysicalValues for T{ii}')
#         axT[ii].grid()
#         plt.xticks(rotation=60,ha='right')
#     else:
#         axT[3].plot(name[1:],pun[1:],'o-',color=colorList[ii],markersize=12+2-ii)
#         axT[3].set_title(f'UnphysicalValues for T3 to deepest')
# figT.savefig(f'{level2_path}/UnphysicalValues_temperatures_{last}_not2014_11.jpg')

# figS,axS = plt.subplots(numS,1,figsize=(20,8),sharex=True)
# for ii in range(numS):
#     pun = [dataEdits[name]['UnphysicalValues'][f'S{ii}'] if f'S{ii}' in dataEdits[name]['UnphysicalValues'].keys() else np.nan for name in generalEdits.keys()]
#     print(pun)
#     axS[ii].plot(name,pun,'o-',color=colorList[ii],markersize=12)
#     axS[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))
#     axS[ii].set_title(f'UnphysicalValues for S{ii}')
#     axS[ii].grid()
#     plt.xticks(rotation=60,ha='right')
# figS.savefig(f'{level2_path}/UnphysicalValues_sainities_{last}.jpg')
# axS[ii].set_xlim(min(dataEdits.keys()),max(dataEdits.keys()))

# # collect means, medians, standard deviations
# buoyLocmn = np.mean()


# plt.show()
# exit()



