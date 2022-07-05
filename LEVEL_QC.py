#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:48:43 2022

@author: suzanne
"""
import re, sys, os
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
from functools import reduce
import ProcessFields as pfields
sys.path.append('/Users/suzanne/git_repos/polarstereo-lonlat-convert-py/polar_convert')
# from polar_convert.constants import NORTH
# from polar_convert import polar_lonlat_to_xy
import netCDF4 as nc
from scipy.signal import medfilt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime as dt
from waterIce import getL1, getL2, plotL1vL2, getOPbias, getBuoyIce, getRidging, getRidgeDates
# from waterIce import * 

log = 0

cList=['k','purple','blue','deepskyblue','cyan','limegreen','darkorange','red'] #'lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'
figspath = '/Users/suzanne/Google Drive/UpTempO/level2/figs'

nopresbids=['300534062158460','300534062158480']
nosalibids=['300534060051570','300534060251600','300234068519450']
# bid = '300234063994900'   # 2016 03
bid = '300234063993850'    # 2016 06
# bid = '300234064735100'   # pressure no sal
# bid = '300534062158460'     # sal no pressure
binf = BM.BuoyMaster(bid)
if log:
    log_file = f'level2/{bid}_{dt.datetime.now().date()}.log'
    fhlog = open(log_file,'w')

# prepend a 0m to pdepths
pdepths = list(itertools.chain.from_iterable([[0],binf['pdepths']]))
tdepths = binf['tdepths']

# readCSV = input('Do you want to read in ridgePressure .csv now? : y for yes, n for no ')
# ridgedPresFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridgedPressure{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'
# print(ridgedPresFile)
# df1a = pd.read_csv(ridgedPresFile)
# print(df1a.columns)
# fig4,ax4 = plt.subplots(1,1,figsize=(15,6))
# ax4.plot(df1a['Dates'],-1*df1a['P1corr'],'b.')
# ax4.plot(df1a['Dates'],df1a['ridgedPressure'],'r.-')
# ax4.xaxis.set_major_locator(mdates.DayLocator(interval=1))
# ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
# ax4.set_yticks(np.arange(np.floor(-1*df1a['P1corr'].max()),np.ceil(-1*df1a['P1corr'].min()),0.1))
# ax4.set_title('manually edited Ridged Pressures (r)')
# plt.show()    
# exit(-1)

level1File = f'{L1path}/UpTempO_{binf["name"][0]}_{int(binf["name"][1]):02d}_{binf["vessel"]}-FINAL.dat'
level2File = f'{L2path}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'

# let's take a look 
df1 = getL1(level1File,bid)
df2 = getL2(level2File,bid)
print('length df1',len(df1))
print('length df2',len(df2))

ds1 = set(df1['Dates'])
ds2 = set(df2['Dates'])
print('Dates in L1 that are not in L2',ds1.difference(ds2))  # not the same as ds2.difference(ds1)
# print(ds1.difference(ds2).Year)
print(df1.loc[df1['Dates']=='2017-10-19 17:00:00'])
print()
print('Number of data rows that have invalid BPs',df1['BP'].isna().sum())

Pcols = [col for col in df1.columns if col.startswith('P')]
Pcolscorr = [col+'corr' for col in df1.columns if col.startswith('P') and not col.endswith('0')]
Tcols = [col for col in df1.columns if col.startswith('T')]
Dcols = [f'D{col[1:]}' for col in df1.columns if col.startswith('T')]
print(Dcols)
print(Tcols)
print(Pcols[1:])
print('Pcolscorr',Pcolscorr)
print('pdepths',pdepths)
print(df1.columns)
# exit(-1)
# invalidate P1 zero values 
df1.loc[df1['P1']==0,'P1'] = np.nan
# This command locates when all Pcols in a row equal NaN, and set all temperatures to NaN, except SST
# print(df1.loc[:,Pcols[1]].isna())  # logical output  using .eq(np.nan) DOES NOT WORK
# invalidate all temps and all calc depths if all pdepths[1:] = NaN
df1.loc[df1.loc[:,Pcols[1:]].isna().apply(lambda x: all(x), axis=1),Tcols[1:]] = np.nan  # ASSUMES Tcols[0] = 'T0'
print(df1.head(20))

# keep all temperature less than -1.8, set correcsponding calc dpths = 0
# for ii,tcol in enumerate(Tcols):
#     df1[tcol].where(df1[tcol]>=-1.8, np.nan, inplace=True) # args are cond, other (so acts like 'or')

# remove Ocean pressure bias
print('Finding ocean pressure bias...')
global coords
for ii,pcol in enumerate(Pcols):
    if pcol != 'P0':
        print()
        print(ii,pcol,pdepths[ii])
        df1, OPbias = getOPbias(pcol,pdepths[ii],df1,bid,figspath)
           
        if log:
            fhlog.write(f'Ocean Pressure bias for nominal depth {pdepths[ii]}m is {OPbias:.2f}m.\n')
if log:
    fhlog.close()
print('ocean pressure bias',OPbias)
if np.isnan(OPbias):
    print('You need a bias to continue')
    exit(-1)


# print(df1.tail())
### determine water/ice
print('Determining Water/Ice values')
indicator = []
mindist = []
for index, row in df1.iterrows():
    # if df2['WaterIce'].iloc[index]==2:
        indi,mind = getBuoyIce(df1['Lon'].iloc[index],df1['Lat'].iloc[index],
                                df1['Year'].iloc[index],df1['Month'].iloc[index],df1['Day'].iloc[index],
                                df1['T0'].iloc[index],plott=0)
        indicator.append(indi)
        mindist.append(mind/1000) # in km
df1['WaterIce'] = indicator
df1['mindist'] = mindist

# find FWT only based on W/I indicator    
# establish a new column
df1['FirstTpod'] = 0
df1.loc[df1['WaterIce']==1,'FirstTpod'] = 1
# print(df1.columns)
# fig4,ax4 = plt.subplots(2,1,figsize=(15,8))
# ax4[0].plot(df1['Dates'],df1['WaterIce'],'b.')
# ax4[0].set_title('Water/Ice indicator')
# ax4[1].plot(df1['Dates'],df1['FirstTpod'],'r.--')
# ax4[1].set_title('First Wet Thermistor, based only on Water/Ice indicator')
# ax4[1].set_ylim([-0.2,5.2])
# for ax in ax4:
#     ax.grid()
#     ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# plt.show()

# # press and dp/dt
# fig1,ax1 = plt.subplots(2,1,figsize=(15,5))
# ax1[0].plot(df1['Dates'],-1*df1['P1corr'],'b.-')
# ax1[0].xaxis.set_major_locator(mdates.DayLocator(interval=1))
# ax1[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
# ax1[0].set_title('Bias corrected Measured Pressure')
# df1['dpdt'] = -1*df1['P1corr'].diff() / (df1['Dates'].diff().apply(lambda x: x/ np.timedelta64(1,'h')))
# print(df1.head())
# print(df1.tail())

# # df1['P1corrRM'] = df1.groupby(pd.Grouper(key='Dates',freq='h'))['P1corr'].mean().rolling(3,center=True).median()
# df1['P1corrRM'] = df1['P1corr'].rolling(3,center=True).mean()

# ax1[1].plot(df1['Dates'],df1['dpdt'],'b.-')
# ax1[1].plot(df1.loc[(df1['dpdt'].abs()>0.2),'Dates'],df1.loc[(df1['dpdt'].abs()>0.2),'dpdt'],'r.')
# ax1[0].plot(df1.loc[(df1['dpdt'].abs()>0.2),'Dates'],-1*df1.loc[(df1['dpdt'].abs()>0.2),'P1corr'],'r.')
# ax1[1].xaxis.set_major_locator(mdates.DayLocator(interval=1))
# ax1[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
# ax1[1].set_title('change in Bias corrected Measured Pressure in m/hour')
# plt.show()
# # for ii in range(2):
# #     if ii==0:
# #         dt1 = dt.datetime(2016,11,7)
# #         dt2 = dt.datetime(2016,11,11)
# #     elif ii==1:
# #         dt1 = dt.datetime(2017,7,21)
# #         dt2 = dt.datetime(2017,7,24)
        
# #     for ax in ax1:
# #         ax.set_xlim([dt1,dt2])
# #         ax.grid()
# #     plt.show()
# exit(-1)
 
# find riding times (besides indicated by Water/Ice indicator), put on .csv file
rTimes = input('Do you want to make ridging time periods file? : y for Yes, n for No ')
if rTimes.startswith('y'):
    fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
    ax1.plot(df1['Dates'],-1*df1['P1corr'],'b.-')
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    # defining the cursor
    cursor = Cursor(ax1,color='r',useblit=True)
    # creating annotate box
    annot = ax1.annotate('',xy=(0,0),xytext=(1,1),xycoords='data',textcoords='offset points',
                        bbox={'boxstyle':'round4','fc':'linen','ec':'k','linewidth':1},
                        arrowprops={'arrowstyle':'-|>'})
    annot.set_visible(False)
    # function for showing and storing the clicks.
    coord=[]
    def onclick(event):
        global coord
        x = event.xdata
        y = event.ydata
        coord.append((mdates.num2date(x).strftime('%Y-%m-%d %H:%M:%S'),y))
        print([mdates.num2date(x).strftime('%Y-%m-%d %H:%M:%S'),y])
        annot.xy = (x,y)
        text = f'{mdates.num2date(x).strftime("%Y-%m-%d %H:%M:%S")}, {y:.2f}'
        annot.set_text(text)
        annot.set_visible(True)
        fig1.canvas.draw()
    
    cid = fig1.canvas.mpl_connect('button_press_event',onclick)
    plt.show()
    fig1.canvas.mpl_disconnect(cid)
    plt.close()

# manually fill this file
ridgeFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridging{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'
dfr = pd.read_csv(ridgeFile)
dfr.dropna(axis=0,how='all',inplace=True)

# plot to ensure the ridged areas
rcols = ['m','c','r','g','orange','m']
fig3,ax3 = plt.subplots(4,1,figsize=(15,12))
ax3[0].plot(df1['Dates'],-1*df1['P1corr'],'b.')

df1['ridged'] = 0  # binary whether riding or no
for ii,row in dfr.iterrows():
    # if ii==1:
    #     print(df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'Dates'])
        print(ii,row)
        ax3[0].plot(df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'Dates'],
                -1*df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'P1corr'],
                '.',color=rcols[ii])
        df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridged'] = 1
ax3[0].set_yticks(np.arange(np.floor(-1*df1['P1corr'].max()),np.ceil(-1*df1['P1corr'].min()),1))
ax3[0].set_title('OP corrected for bias, colors for ridge levels')
ax3[1].plot(df1['Dates'],df1['ridged'],'b.')
ax3[1].set_title('Ridged: 0 = no, 1 = yes')
ax3[2].plot(df1['Dates'],df1['WaterIce'],'b.')
ax3[2].set_title('Water (2), Ice (1)')

# looking at ridged areas and set FirstTpod (FWT)
for ii,row in dfr.iterrows():
    for index,ridgerow in df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii])].iterrows():
        # how much ridging?
        metersofRidge = pdepths[1] - df1['P1corr'].iloc[index]
        numZeros = len([x for x in tdepths if x<metersofRidge])

        # set calculated depths  'shallower' than FWT as 0        
        for dcol in Dcols[:numZeros]:
            df1.loc[index,dcol] = 0
        df1.loc[index,'FirstTpod'] = numZeros

ax3[3].plot(df1['Dates'],df1['FirstTpod'],'r.')
ax3[3].set_title('First Wet Thermistor (zero based)')
for ax in ax3:
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.grid()
plt.show()

# find SST based on first wet thermistor, or actually temperature of FWT
df1['sst']= np.nan
# last time of max FWT.  As we 'de-ridge' we want only declining, no popping around.
fwtmax = df1['FirstTpod'][::-1].idxmax()
print('maximum fwt',fwtmax)
for ii,row in df1.iterrows():
    if ii>fwtmax:
        if df1.loc[ii,'FirstTpod'] > df1.loc[ii-1,'FirstTpod']:
            df1.loc[ii,'FirstTpod'] = df1.loc[ii-1,'FirstTpod']
    fwt = df1.loc[ii,'FirstTpod']
    # log temperature of FWT
    df1.loc[ii,'sst' ] = df1.loc[ii,Tcols[fwt]]

# fig4,ax4 = plt.subplots(3,1,figsize=(15,12))
# ax4[0].plot(df1['Dates'],-1*df1['P1corr'],'b.')
# ax4[0].set_yticks(np.arange(np.floor(-1*df1['P1corr'].max()),np.ceil(-1*df1['P1corr'].min()),1))
# ax4[0].set_title('Bias Corrected OP')
# ax4[1].plot(df1['Dates'],df1['FirstTpod'],'r.--')
# ax4[1].set_title('First Wet Thermistor')
# ax4[2].plot(df1['Dates'],df1['sst'],'b.')
# ax4[2].set_title('SST as determined from FWT')
# dt1=dt.datetime(2017,7,18)
# dt2=dt.datetime(2017,7,23)
# for ax in ax4:
#     ax.grid()
#     ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
#     ax.set_xlim([dt1,dt2])
# plt.show()

ridgedPresFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridgedPressure{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'

writeCSV = input('Do you want to make a new ridgePressure .csv now? : y for yes, n for no ')
if writeCSV.startswith('y'):
    df1['ridgedPressure'] = -1*pdepths[-1]
    
    for ii in range(len(dfr)):
        df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridgedPressure'] = dfr['OPlimit'][ii]

    col2move = df1.pop('Dates')
    df1.insert(0,'Dates',col2move)
    col2move = df1.pop('P1corr')
    df1.insert(1,'P1corr',col2move)
    col2move = df1.pop('ridgedPressure')
    df1.insert(2,'ridgedPressure',col2move)
    print(df1.head())

    df1.to_csv(ridgedPresFile)
        
    # fig4,ax4 = plt.subplots(1,1,figsize=(15,6))
    # ax4.plot(df1['Dates'],-1*df1['P1corr'],'b.')
    # ax4.plot(df1['Dates'],df1['ridgedPressure'],'r.-')
    # ax4.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    # ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    # ax4.set_yticks(np.arange(np.floor(-1*df1['P1corr'].max()),np.ceil(-1*df1['P1corr'].min()),0.1))
    # ax4.set_title('original ridefs pressures ')
    # ax4.grid()
    # ax4.set_title('Bias Corrected OP(b), RidgedPressure(r)')
    # plt.show()
    
    # # move column ridgedPressure to be next to Dates, for each editing.
    # plt.show()
    
dt1 = dt.datetime(2016,11,1)
dt2 = dt.datetime(2016,11,5)
readCSV = input('Do you want to read in ridgePressure .csv now? : y for yes, n for no ')
if readCSV.startswith('y'):
    print(ridgedPresFile)
    df1a = pd.read_csv(ridgedPresFile)
    print(df1a.columns)
    fig4,ax4 = plt.subplots(1,1,figsize=(15,6))
    ax4.plot(df1['Dates'],-1*df1['P1corr'],'b.')
    ax4.plot(df1['Dates'],df1a['ridgedPressure'],'r.-')
    # ax4.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #%Y-%m-%dT%H:%M
    ax4.set_yticks(np.arange(np.floor(-1*df1['P1corr'].max()),np.ceil(-1*df1['P1corr'].min()),1))
    ax4.set_xlim(dt1,dt2)
    ax4.set_title('manually edited Ridged Pressures (r), bias corrected OP (b)')
    fig4.savefig(f'{figspath}/ManuallyRigedPressures_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    plt.show()    

print('Interpolating calculated depths...')
tcalcdepths=np.full([len(df1),len(tdepths)],np.nan)
print('tcalc depths shape',tcalcdepths.shape)
# n=0
# assuming only P1(corr)
print('Pcolscorr',Pcolscorr)
for ii, row in df1.iterrows():
    if not df1['ridged'].iloc[ii]:
        # if np.all(df1[Pcolscorr].iloc[ii] >= pdepths):  # .ge means deeper
        if df1[Pcolscorr[-1]].iloc[ii] >= pdepths[-1]:  # .ge means deeper
            tcalcdepths[ii,:] = tdepths + ( df1['P1corr'].iloc[ii] - pdepths[1])
            # print('tdepths',tdepths)
            # print('P1corr measured',df1['P1corr'].iloc[ii])
            # print(tcalcdepths[ii,:])
            # exit(-1)
        else:
            pmeas = list(itertools.chain.from_iterable([[0],df1[Pcolscorr].iloc[ii]]))
            fi = interpolate.interp1d(pdepths,pmeas,fill_value = 'extrapolate')    
            tinvolved = tdepths
            tcalcdepths[ii,:] = fi(tinvolved)
            # print('tdepths',tdepths)
            # print('P1corr measured',df1['P1corr'].iloc[ii])
            # print(tcalcdepths[ii,:])
            # exit(-1)
    else:  # ridged
        # if -1*df1['P1corr'].iloc[ii] - (df1a['ridgedPressure'].iloc[ii]+0.2) <= 0:  # assuming string straight
        #     tcalcdepths[ii,:] = tdepths + ( df1['P1corr'].iloc[ii] - pdepths[1])
        #     # print('tdepths',tdepths)
        #     # print('P1corr measured',df1['P1corr'].iloc[ii])
        #     # print(tcalcdepths[ii,:])
        #     deepestZero = df1['FirstTpod'].iloc[ii]
        #     tcalcdepths[ii,:deepestZero] = 0
        #     # print(df1['FirstTpod'].iloc[ii])
        #     # print(tcalcdepths[ii,:])
        #     # exit(-1)
        # else:
            pmeas = list(itertools.chain.from_iterable([[0],df1[Pcolscorr].iloc[ii]]))
            deepestZero = df1['FirstTpod'].iloc[ii]
            pdepthsRidged = [-1*df1a['ridgedPressure'].iloc[ii]] #[x-tdepths[deepestZero-1] for x in pdepths[1:]]
            pdepthsRidged.insert(0,0)
            print('pmeas',pmeas)
            print('pdepthsRidged',pdepthsRidged)
            print('deepestZero',deepestZero)
            fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')  
            offset = pdepths[1] - pdepthsRidged[1]
            print('offset',offset)
            tdepthsRidged = [x- offset for x in tdepths]  #( df1['P1corr'].iloc[ii] - pdepths[1])
            print('tdepthsRidged',tdepthsRidged)
            tcalcdepths[ii,:] = fi(tdepthsRidged)
            print('tcalcdepths',tcalcdepths[ii,:])
            tcalcdepths[ii,:deepestZero] = 0
            # exit(-1)
tcalcdepths = np.array(tcalcdepths)
print(tcalcdepths.shape)
print(Dcols)

for ii,dcol in enumerate(Dcols):
    print(dcol)
    df1[dcol] = tcalcdepths[:,ii]

print('Done')
print(df1.columns)
print()
print(df2.columns)

fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
for ii,dcol in enumerate(Dcols):
    ax8.plot(df1['Dates'],-1*df1[dcol],'.',color=cList[ii],label=f'{tdepths[ii]}')
ax8.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax8.set_yticks(np.arange(-26,1))
ax8.set_title('Suzanne s calculated depths ')
ax8.grid()
ax8.legend(loc='lower center')
ax8.set_xlim(dt1,dt2)
fig8.savefig(f'{figspath}/CalcDepthsSuzanne_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()
   
fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
for ii,dcol in enumerate(Dcols):
    ax8.plot(df2['Dates'],-1*df2[dcol],'.',color=cList[ii],label=f'{tdepths[ii]}')
ax8.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax8.set_yticks(np.arange(-26,1))
ax8.set_title('Wendy s calculated depths ')
ax8.grid()
ax8.legend(loc='lower center')
ax8.set_xlim(dt1,dt2)
fig8.savefig(f'{figspath}/CalcDepthsWendy_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()
   

mergedf = pd.merge(df1,df2,how='inner', on=['Dates'])
print(mergedf.columns)

fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
for ii,dcol in enumerate(Dcols):
    ax8.plot(mergedf['Dates'],mergedf[dcol+'_x']-mergedf[dcol+'_y'],'.',color=cList[ii],label=f'{tdepths[ii]}')
ax8.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# ax8.set_yticks(np.arange(-26,1))
ax8.set_title('Suzannes (+depths) minus Wendys (+depths) calculated depths ')
ax8.grid()
ax8.legend(loc='lower center')
ax8.set_xlim(dt1,dt2)
fig8.savefig(f'{figspath}/CalcDepthsSuzanne-Wendy_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()
   
fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
ax8.plot(mergedf['Dates'],mergedf['WaterIce_y'],'b+')
ax8.plot(mergedf['Dates'],mergedf['WaterIce_x'],'rx')
ax8.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# ax8.set_yticks(np.arange(-26,1))
ax8.set_title('Water/Ice indicator Wendy(b+) Suzanne(rx)')
ax8.grid()
ax8.legend(loc='lower center')
ax8.set_xlim(dt1,dt2)
fig8.savefig(f'{figspath}/WaterIceWendySuzanne_zoom_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()

# print(newdf[['P1corr','P1_y']].diff(axis=1).head(30)) #.mean())
# print(newdf[['P1corr','P1_y']].head(30)) #.mean())
# print(df2['Dates'].isin(df1['Dates']).iloc(3))

    
exit(-1)








# fig0,ax0 = plt.subplots(5,1,figsize=(15,12))
# ax0[0].plot(df2['Dates'],df2['WaterIce'],'bo-')
# ax0[0].plot(df1['Dates'],df1['WaterIce'],'r.')
# ax0[0].set_title(f'WaterIce indicator: NRT(b), CDR(r), Ice(1), Ocean(2), for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)

# ax0[1].plot(df2['Dates'],df2['FirstTpod'],'bo')
# ax0[1].plot(df1['Dates'],df1['FirstTpod'],'r.')
# ax0[1].plot([df2['Dates'].iloc[0],df2['Dates'].iloc[-1]],[-1.2,-1.2],'k--')
# ax0[1].set_title('First temperature pod in water',wrap=True)

# ax0[4].plot(df1['Dates'],df1['mindist'],'r.')
# ax0[4].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[17.7,17.7],'k--')
# ax0[4].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[35.4,35.4],'k--')
# ax0[4].set_title('Minimum distance from buoy to nearest Ice, km',wrap=True)

# ax0[2].plot(df1['Dates'],df1['T0'],'b.')
# ax0[2].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.2,-1.2],'k--')
# ax0[2].set_title('Buoy T0: shallowest thermistor, C',wrap=True)

# # ax0[3].plot(df2['Dates'],-1*df2['P1'],'bx')
# ax0[3].plot(df1['Dates'],-1*df1['P1corr'],'r.')
# ax0[3].set_title('Ocean Pressure with bias applied',wrap=True)

# for ax in ax0:
#     ax.grid()
#     ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# plt.savefig(f'{figspath}/WaterIce_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')

# fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
# ax1.plot(df1['Dates'],-1*df1['P1corr'],'r.')
# ax1.grid()
# ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
# ax1.gca().fmt_xdata(mdates.DateFormatter())
# ax1.set_title('Ocean Pressure with bias applied',wrap=True)

# plt.show()
# exit(-1)
# fig1,ax1 = plt.subplots(len(Pcols)-1,1,figsize=(15,5*(len(Pcols)-1)))
# ax1.plot(df1['Dates'],-1*df1['P1corr'],'r.-')
# ax1.plot(df2['Dates'],-1*df2['P1'],'b.-')
# ax1.set_title(f'Ocean pressure corrected for bias, at nominal depth of {pdepths[1]}db: W(b) S(r) for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
# ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# mndiff = f'Mean diff: {df2["P1"].mean() - df1["P1corr"].mean():.2f}'
# ax1.text(df1['Dates'].iloc[10],-1*pdepths[1]+5,mndiff,fontdict={'fontsize':12})
# ax1.grid()
# if len(Pcols)>2:
#     for ii,ax in enumerate(ax1):
#         if ii != 0:
#             print('ii',ii)
#             ax.plot(df1['Dates'],-1*df1[f'P{ii+1}corr'],'r.-')
#             ax.plot(df2['Dates'],-1*df2[f'P{ii+1}'],'b.-')
#             ax.set_title(f'Ocean pressure corrected for bias, at nominal depth of {pdepths[ii+1]}db: W(b) S(r) for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
#             ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
#             mndiff = f'Mean diff: {df2[f"P{ii+1}"].mean() - df1[f"P{ii+1}corr"].mean()}'
#             ax.text(df1['Dates'].iloc[10],-1*pdepths[ii+1]+5,mndiff,fontdict={'fontsize':12})
#             ax.grid()
# fig1.savefig(f'{figspath}/OPbiasCorr_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
# plt.show()

# establish time period of ridging
df1['ridging'] = 0
ridge = input('Is there ridging evident in this dataset? : 0 for No, 1 for yes ')

# try same as with pressure bias, click times.
while ridge:
    # for ii,pcol in enumerate(Pcolscorr):
        df1 = getRidging(pcol,pdepths[ii+1],df1,bid,figspath)
        ridge = input('Is there another ridging evident in this dataset? : 0 for No, 1 for yes ')
    # OPlimit = input('What is the pressure level of the ridging? ')
    # df1.loc[(df1['P1corr']<np.float(OPlimit)),'ridging'] = 1
    # # global coords
    # for ii,pcol in enumerate(Pcols):
    #     if pcol != 'P0':
    #         print()
    #         print(ii,pcol,pdepths[ii])
    #         df1 = getRidging(pcol,pdepths[ii],df1,bid,figspath)
print(df1.head())
exit(-1)  

             
fig5,ax5 = plt.subplots(1,1,figsize=(15,5))
# ax7[0].plot(df1['Dates'],df1['ridging'],'.')
# ax7[0].set_title(f'Ridging for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}')
ax5.plot(df1['Dates'],-1*df1['P1corr'],'.')
ax5.plot(df1.loc[(df1['ridging']==1),'Dates'],-1*df1.loc[(df1['ridging']==1),'P1corr'],'ro')
ax5.grid()
ax5.set_title(f'Pressures showing ridging (r) for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}')
fig5.savefig(f'{figspath}/RidgingPressures_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')

# find thermisters at zero depth
df1[Dcols[0]] = 0
for ii,dcol in enumerate(Dcols):
    if ii>0:
        df1[dcol] = np.nan
print('df1 with Dcols as nans')
print(df1.head())
print()
n=0
df1['FirstTpod'] = 0
df1['sst'] = -999

# find FWT and associated SST
for index, row in df1.iterrows():
    numZeros = 0
    if df1.loc[index,'WaterIce'] == 1:  # in/near ice
        # df1['FirstTpod'].iloc[index]=1  no good
        # df1.iloc[index]['FirstTpod']=1  no good 
        # df1.iloc[index, df1.columns.get_loc('FirstTpod')]=1# ok, but stupid
        numZeros = 1
    if df1.loc[index,'ridging'] == 1:
        # how much ridging?
        metersofRidge = pdepths[1] - df1['P1corr'].iloc[index]
        numZeros = len([x for x in tdepths if x<metersofRidge])
        # df1.loc[index,'FirstTpod'] = numZeros
        for dcol in Dcols[:numZeros]:
            df1.loc[index,dcol] = 0
    df1.loc[index,'FirstTpod'] = numZeros
    df1.loc[index,'sst' ] =df1.loc[index,Tcols[numZeros]]
    
ax0[1].plot(df1['Dates'],df1['FirstTpod'],'r.')
fig0.savefig(f'{figspath}/WaterIce_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')

# for ax in ax7:
#     ax.set_xlim([dt.datetime(2017,7,17),dt.datetime(2017,7,21)])
# ax7[0].plot(df1['Dates'],df1['FirstTpod'],'r.')
# plt.savefig(f'{figspath}/WhatisHappeningZoom_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()
exit(-1)
# print(df1.head())
# exit(-1)

# # find SST (temperature of FWT)
# df1['sst']=-999.
# for ii, row in df1.iterrows():
#     df1['sst'].iloc[ii]=row[Tcols[row['FirstTpod']]]
# #     # df1['SST'].iloc[ii = df1.loc[df1[Tcols[df1['FirstTpod']]])
# #     # print(row['FirstTpod'])
# #     # print(df1['FirstTpod'].iloc[ii])
# #     df1['sst'].iloc[ii] = int(row[Tcols[row['FirstTpod']]])
# #     # print()
# #     # if ii > 10:
#     #     exit(-1)
# df1.head()
# exit(-1)
# df1['SST'] = df1.loc[d1['']]
fig6,ax6 = plt.subplots(2,1,figsize=(15,5))
ax6[0].plot(df1['Dates'],df1['sst'],'r.')
ax6[0].text(dt.date(2016,11,15),3,f'Min SST {df1["sst"].min():.2}C')
ax6[0].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax6[0].xaxis.set_ticklabels([])
ax6[0].grid()
ax6[0].set_title(f'SST: S(r) from buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
ax6[1].plot(df2['Dates'],df2['FirstTpod'],'bo')
ax6[1].plot(df1['Dates'],df1['FirstTpod'],'r.')
ax6[1].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax6[1].grid()
ax6[1].set_title(f'First Tpod in Water: W(b), S(r) from buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
fig6.savefig(f'{figspath}/SST_FirstTpodWater_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
plt.show()
exit(-1)
# calculate depths at all thermistors     
# compute calculated depths by linear interpolation
tcalcdepths = []

Pcolscorr = deque([col for col in df1.columns if col.startswith('P') and col.endswith('corr')])
Pcolscorr.appendleft('P0')
print(Pcolscorr)
print()
print()
print()

# fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
# h = ax1.imshow(df1[Dcols],vmin=0,vmax=26)
# ax1.set_aspect('auto')
# fig1.colorbar(h,ax=ax1,label='pressure, db',shrink=1/2)
# ax1.set_title(f'Calculated depths S',wrap=True)

# fig2,ax2 = plt.subplots(1,1,figsize=(15,5))
# h = ax2.imshow(df2[Dcols],vmin=0,vmax=26)
# ax2.set_aspect('auto')
# fig2.colorbar(h,ax=ax2,label='pressure, db',shrink=1/2)
# ax2.set_title(f'Calculated depths W',wrap=True)

### DO THIS AFTER MERGING (SO SAME NUMBER OF ROWS/DATES)
Dcols_y = [f'D{col[1:]}' for col in newdf.columns if col.startswith('T') and col.endswith('_y')]
Dcols_x = [f'D{col[1:]}' for col in newdf.columns if col.startswith('T') and col.endswith('_x')]
newdf.rename(columns={'Year_x':'Year','Month_x':'Month','Day_x':'Day','Hour_x':'Hour'},inplace=True)
newdf['Dates']=pd.to_datetime(newdf[['Year','Month','Day','Hour']])

fig3,ax3 = plt.subplots(1,1,figsize=(15,5))
for ii,dcol in enumerate(Dcols_y):
    ax3.plot(newdf['Dates'],newdf[dcol]-newdf[f'{dcol[:-1]}x'],label=f'{tdepths[ii]}')
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax3.grid()
ax3.legend()
ax3.set_title(f'Difference in calculated depths W minus S,for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
plt.savefig(f'{figspath}/CalcDepths_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')

# depth profiles
D_y = newdf[Dcols_y].to_numpy()
D_x = newdf[Dcols_x].to_numpy()

fig6,ax6 = plt.subplots(1,1,figsize=(5,10))
jj=np.arange(240,260,5)
print(tdepths)
print(len(tdepths))
tmp = np.tile(np.reshape(np.array(tdepths),(1,-1)),(len(jj),1))
# print(tmp)
# print(np.tile(tmp,(len(jj),1)).shape)
# print()
# print(D_y[jj,:].shape, np.reshape(np.array(tdepths),(1,-1)).shape)
# # tmp=np.array(tdepths)
# # tmp=[tmp,None]
# # # tmp=np.tile(np.array(tdepths),(len(jj)))
# # print(tmp.shape)
# exit(-1)
cc=['b','r','k','g']
for ii,j in enumerate(jj):
    ax6.plot(D_y[j,:],-1*np.array(tdepths),'.-',color=cc[ii],label=f'{j}')
    ax6.plot(D_x[j,:],-1*np.array(tdepths),'--',color=cc[ii])
    print(df1.iloc[j])
ax6.set_title('Depth profile W(b), S(r)')
ax6.legend()
ax6.grid()
# ax6[1].plot(D_y[jj,:]-D_x[jj,:],-1*np.array(tdepths),'b.-')
# ax6[1].set_title('W minus S')
# ax6[1].grid()
# # difference in P1
# fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
# ax1.plot(newdf['Dates'],newdf['P1_y'] - newdf['P1corr'],'r.-')
# ax1.set_title(f'Ocean pressure corrected for bias, at nominal depth of {pdepths[1]}db: W(b) S(r) for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}',wrap=True)
# ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
# mndiff = f'Mean diff: {df2["P1"].mean() - df1["P1corr"].mean():.2f}'
# ax1.text(df1['Dates'].iloc[10],-1*pdepths[1]+5,mndiff,fontdict={'fontsize':12})
# ax1.grid()


# D1y = newdf['D1_y'].to_numpy()
# D1x = newdf['D1_x'].to_numpy()
# D1diff=D1y - D1x
# print(D1diff[D1diff<0])
# fig14,ax14 = plt.subplots(1,1)
# ax14.plot(D1diff,'.-')
# plt.show()
# exit(-1)

# print(newdf.loc[ (newdf['D1_y']-newdf['D1_x']) < 0,['P1corr','P1_y']])

# fig4,ax4 = plt.subplots(1,1,figsize=(5,10))
# for ii in range(243,255):
#     ax4.plot(newdf[Dcols_y].iloc[ii]-newdf[Dcols_x].iloc[ii],'.-')
#     # ax4.plot(newdf[Dcols_x].iloc[ii],'r.-')
#     print('blue',newdf[Dcols_y].iloc[ii],ii)
#     print('red ',newdf[Dcols_x].iloc[ii],ii)
# ax3.plot(newdf[Dcols_y] - newdf[Dcols_x])
# h = ax3.imshow(newdf[Dcols_y]) #-newdf[Dcols_x]) #,extent=[0,7,df1['Dates'][0], df1['Dates'][-1]],vmin=-1,vmax=1,cmap='bwr')
# ax3.set_aspect('auto')
# fig3.colorbar(h,ax=ax3,label='pressure, db',shrink=1/2)

# plt.show()
# exit(-1)

# # The calculated depth at the top most thermistor was generally assumed to be equal to the nominal depth, ie 2.5m. (what?)
# df1['D0'] = tdepths[1] - df1['D1']
# print(df1.head(20))  
# # plotL1vL2(df1,df2,bid,'_afterDepthCalc')
# print(df1.loc[0,Dcols])

# fig6,ax6 = plt.subplots(1,1)
# ax6.plot(tdepths,tdepths,'b')
# ax6.plot(tdepths,df1.loc[:30,Dcols],'r.')
# ax6.set_xlabel('Nominal Depths')
# ax6.set_xlabel('Calculated Depths')
# plt.show()
# exit(-1)

# if log:
#     log_file = f'{L2path}/QualityControlMods_{bid}_{dt.datetime.now().date()}.log'
#     print('Log file',os.path.basename(log_file))
#     fhlog = open(log_file,'a')

today = dt.date.today()
todaystr = f'{today.year}-{today.month:02}-{today.day:02}:\n'

# # print(binf)
# # read in level1 header and write to level2 header
# f1 = open(f'{level1Path}/{level1File}','r')
# # f2 = open(f'{level2Path}/{level2File}','w')
# # lines = f1.readlines()
# # for line in lines:
# #     if line.startswith('%') and 'FILE UPDATE' not in line and 'END' not in line:
# #         f2.write(line)
# #         if 'WMO' in line:
# #             f2.write(f'%MANUFACTURER: {binf["brand"]}\n')
# #         if '=' in line:
# #             # get col number
# #             col_number = int(re.search(r'\% (.*?) =',line).group(1).strip(' '))
# # f2.write(f'% {col_number+1} = Open Water or Ice Indicator (1=ice, 2=water)')        
# # f2.close()
# f1.close()


# all -99s and -999s have been set to np.NaN, reset NaNs to -999s later, when writing Level-2 ascii


# df.set_index(['Dates'],inplace=True)


# look at puzzling details
if bid == 300234063993850:
    print(df1.loc[(df1['Year'] == 2016) & (df1['Month'] == 9) & (df1['WaterIce'] == 1),['WaterIce','T0','mindist','P1corr']])

plt.show(block=False)
plt.pause(0.001)
input('Press enter to close figures.')
plt.close('all')
exit(-1)


# df.insert(len(df.columns)-1,'WaterIce',np.array(indicator))
# print(df.head())
    
# # get columns used for data cleanup
# Tcols = [col for col in df.columns if col.startswith('T')]
# Pcols = [col for col in df.columns if col.startswith('P')]
# Scols = [col for col in df.columns if col.startswith('S') and not col.startswith('SUB')]
# # calculating depths by interpolation                
# Dcols = [f'D{col[1:]}' for col in df.columns if col.startswith('T')]

# for col in zip(Dcols,Tcols):
#     print(col[0])
# exit(-1)
# # temperatures
# fig0,ax0 = plt.subplots(1,1,figsize=(10,5))
# for ii,tcol in enumerate(Tcols):
#     if ii<=1:
#         print(tcol)
#         ax0.scatter(df['Dates'],df[tcol],10,cList[ii])  #,picker=True, pickradius=5)
#     # ax0.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
#     #             df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),tcol],10,cList[ii])  #,picker=True, pickradius=5)
# # ax0.set_ylim([-20,20])
# ax0.set_title(f'Temperatures for {bid}')
# ax0.grid()    
# plt.show()
# exit(-1)

# # salinities
# fig1,ax1 = plt.subplots(1,1,figsize=(10,5))
# for scol in Scols:
#     ax1.scatter(df['Dates'],df[scol],10,cList[ii])  #,picker=True, pickradius=5)
#     # ax0.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
#     #             df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),tcol],10,cList[ii])  #,picker=True, pickradius=5)
# ax1.set_ylim([32,37])
# ax1.set_title(f'Salinities for {bid}')
# ax1.grid()    
# # plt.show()
# # exit(-1)


# fig3,ax3 = plt.subplots(1,1,figsize=(10,5))
# for ii,pcol in enumerate(Pcols):
#     ax3.scatter(df['Dates'],-1*df[pcol],10,cList[ii]) #,picker=True, pickradius=5)
# ax3.set_title(' before 0s to nans')
# ax3.grid()

# This command locates when all Pcols in a row equal 0, and sets them all to nan
df.loc[df.loc[:,Pcols].eq(0).apply(lambda x: all(x), axis=1),Pcols] = np.nan
# actually remove all zeros (0.0) for P1, and deeper and pressures deeper than deepest+5m
for ii,pcol in enumerate(Pcols):
    if pcol != 'P0':
        df[pcol].replace(0,np.nan,inplace=True)
        df.loc[df[pcol]>np.max(pdepths[ii])+5,pcol]= np.nan
    
# print(df.isna().sum())
# exit(-1)
# fig3,ax3 = plt.subplots(1,1,figsize=(10,5))
# for ii,pcol in enumerate(Pcols):
#     ax3.scatter(df['Dates'],-1*df[pcol],10,cList[ii]) #,picker=True, pickradius=5)
# ax3.set_title(' after 0s to nans')
# ax3.grid()

# compute, log and remove OPbiases
global coords
for ii,pcol in enumerate(Pcols):
    if pcol != 'P0':
        df, OPbias = getOPbias(pcol,pdepths[ii],df)
        if log:
            fhlog.write(f'Ocean Pressure bias for nominal depth {pdepths[ii]}m is {OPbias}m.\n')
        df[pcol+'UN'] = df[pcol]-OPbias
if log:
      fhlog.close()



# compute calculated depths of the thermistors
tcalcdepths = []
# print(tdepths)
PcolsUN = deque([col for col in df.columns if col.startswith('P') and col.endswith('UN')])
PcolsUN.appendleft('P0')

print('Interpolating calculated depths...')
for ii in range(len(df)):
    fi = interpolate.interp1d(pdepths,df[PcolsUN].iloc[ii])            
    tcalcdepths.append(fi(tdepths))
print('Done')

tcalcdepths = np.asarray(tcalcdepths)
print(tcalcdepths.shape)
print()

for ii,dcol in enumerate(Dcols):
    df[dcol] = tcalcdepths[:,ii]  
print(df.head())  

df2 = getL2(bid)
print()
print(df2.head())
# plot calculated depths from WE and SD
# for ii,col in enumerate(zip(Dcols,Tcols)):
#     # if ii < 4:
#         fig,ax = plt.subplots(1,1,figsize=(12,8))
#         ax.plot(df2[col[0]].mul(-1),'bx')
#         ax.plot(df[col[0]].mul(-1),'r+')
#         ax.set_title(f'Nominal Depth {tdepths[ii]}m')
#         plt.show()

# remove temperature spikes
for ii,tcol in enumerate(Tcols):
    if ii==1:
        df = removeSpikes(df,tdepths)

# fig, ax = plt.subplots(1,2)
# ax[0].plot(-1*pdepths,-1*df[pressureCols].iloc[0],'ro',linewidth=2,label='P Depth Meas')
# ax[0].plot(-1*tdepths,-1*tdepths,'k--')
#     ax[0].plot(-1*tdepths,-1*temperatureDepths,'b*',label='T Depth Interp')      
#     ax[0].legend(loc='upper left')  
#     ax[0].set_ylabel('Depth, [m]')
#     ax[1].plot(tdepths,temperatureDepths-tdepths,'b*',label='differences')      
#     ax[1].legend()  
#     plt.show()
#     exit(-1)
# fig6,ax6 = plt.subplots(1,1,figsize=(15,5))
# for ii,pcol in enumerate(Pcols):
#     if pcol != 'P0':
#         ax6.plot(df['Dates'],-1*df[pcol],'r')
#         ax6.plot(df['Dates'],-1*df[pcol+'corr'],'b')
#         ax6.grid()
# plt.show()

# print('whatever')
print(df.head())
# print(df.loc[:,df['Dates'] < '2018-9-20'])
# exit(-1)

fileL2 = f'{level2Path}/{level2File}'
plot_L2vsL1(fileL2,df,bid)    
    
    
    
exit(-1)    
    





fig3,ax3 = plt.subplots(1,1,figsize=(10,5))
for ii,pcol in enumerate(Pcols):
    ax3.scatter(df['Dates'],-1*df[pcol],10,cList[ii]) #,picker=True, pickradius=5)
    # ax3.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
    #             -1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),pcol],10,cList[ii])  #,picker=True, pickradius=5)
    # ax3.plot(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
    #             -1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),pcol],cList[ii])  #,picker=True, pickradius=5)
ax3.set_title(' before 0s to nans')
ax3.grid()

print(df.columns.values.tolist())

# fig4,ax4 = plt.subplots(1,1,figsize=(10,5))
# ax4.plot(df['T6'],-1*df['P1'],'.-',cList[6])
# ax4.plot(df['T10'],-1*df['P2'],'.-',cList[10])
# ax4.plot(df['T12'],-1*df['P3'],'.-',cList[12])
# ax4.plot(df['Dates'],-1*df['P1'],'.-')
# ax4.plot(df['Dates'],-1*df['P2'],'ro')
# ax4.plot(df['Dates'],-1*df['P3'],'gx')


# plot pressures
fig3,ax3 = plt.subplots(1,1,figsize=(10,5))
for ii,pcol in enumerate(Pcols):
    ax3.scatter(df['Dates'],-1*df[pcol],10,cList[ii]) #,picker=True, pickradius=5)
    # ax3.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
    #             -1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),pcol],10,cList[ii])  #,picker=True, pickradius=5)
    # ax3.plot(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
    #             -1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),pcol],cList[ii])  #,picker=True, pickradius=5)
ax3.set_title(' donot get it')
ax3.grid()

plt.show()
exit(-1)
# fig2,ax2 = plt.subplots(3,1,figsize=(10,5))
# n,bins,patches = ax2[0].hist(-1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'P1'],np.arange(-21.055,-20.005,0.01))
# # print(n,bins)
# print(bins[np.nonzero(n)][0])
# print()
# print()
# n,bins,patches = ax2[1].hist(-1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'P2'],np.arange(-41.055,-40.005,0.01))
# # print(n,bins)
# print(bins[np.nonzero(n)][0])
# print()
# print()
# n,bins,patches = ax2[2].hist(-1*df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'P3'],np.arange(-61.055,-60.005,0.01))
# # print(n,bins)
# print(bins[np.nonzero(n)][0])
# print()
# print()
# # ax2.set_ylim([-65,-55])
# for ax in ax2.ravel():
#     ax.grid()    

plt.show()
exit(-1)



# def onpick(event):
#     thisline = event.artist
#     xdata = thisline.get_xdata()
#     ydata = thisline.get_ydata()
#     ind = event.ind
#     points = tuple(zip(xdata[ind], ydata[ind]))
#     print('onpick points:', points)
#     plt.plot(xdata[ind],ydata[ind],'ro')
#     event.canvas.draw()

# # temperatures
# fig0,ax0 = plt.subplots(1,1,figsize=(10,5))
# for ii,tcol in enumerate(Tcols):
#     ax0.scatter(df['Dates'],df[tcol],10,cList[ii])
# ax0.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-2,-2],color='gray')
# ax0.grid()

# pressures    
# fig1,ax1 = plt.subplots(1,1,figsize=(10,5))
# for ii,pcol in enumerate(Pcols):
#     ax1.scatter(df['Dates'],-1*df[pcol],10,cList[ii],picker=True, pickradius=5)
# ax1.set_ylim([-100,0])
# ax1.grid()    
# fig1.canvas.mpl_connect('pick_event', onpick)

# plt.show()
exit(-1)


                
                

# CD.CalculateDepths(bid)