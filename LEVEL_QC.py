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
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime as dt
# from waterIce import getL1, getL2, plotL1vL2, getOPbias, getBuoyIce, getRidging, getRidgeDates
from waterIce import *

cList=['k','purple','blue','deepskyblue','cyan','limegreen','darkorange','red'] #'lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

# assign paths. L2 data brought in for comparison
L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'
figspath = '/Users/suzanne/Google Drive/UpTempO/level2/'

bid = '300234064737080'   # 2017 04
# bid = '300234062491420'   # 2016 04
# bid = '300234063991680'   # 2016 07
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
    level2File = f'{L2path}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'
except:
    level2File = f'{L2path}/UTO_{binf["name"][0]}-{binf["name"][1]}_{bid}_L2.dat'
try:
    level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'
except:
    level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{binf["name"][1]}_{bid}_L2.dat'

# write header for L2. Start with header from L1.
f1 = open(level1File,'r')
if '300234064737080' in bid:
    WrapCorr = 'YES'
else:
    WrapCorr = 'NO'

f2 = open(level2Draft,'w')
df1,pdepths,tdepths,sdepths = getL1(level1File,bid,figspath)
print(df1.columns)
print(len(df1))

outputCols = {}
lines = f1.readlines()
for ii,line in enumerate(lines):
    if line.startswith('%') and '%END' not in line:
        f2.write(line)
        ColNum = re.findall(r'(\d+) =',line)
        if len(ColNum)>0:
            outputCols[int(ColNum[0])] = df1.columns[int(ColNum[0])]
    if '%END' in line:
        break
nextColNum = int(ColNum[0]) + 1
print(outputCols)

compareL2 = input('Do you want to compare L1 to Wendys L2? : y for Yes, n for No ')
if compareL2.startswith('y'):
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

# inventory columns, make calculated depth columns
Pcols = [col for col in df1.columns if col.startswith('P')]
# Pcolscorr = [col+'corr' for col in df1.columns if col.startswith('P') and not col.endswith('0')]
Tcols = [col for col in df1.columns if col.startswith('T')]
Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
Dcols = [f'D{col[1:]}' for col in df1.columns if col.startswith('T')]
print(Dcols)
print(Tcols)
print(Scols)
print(Pcols)
print('pdepths',pdepths)
print('tdepths',tdepths)
# get indices in tdepths where pdepths in intersects
indT = dict((k,i) for i,k in enumerate(tdepths))
inter = set(indT).intersection(pdepths)  # intersection of the keys
indP = sorted([indT[x] for x in inter])  # intersection of the values (indices)
print(df1.columns)

# This command locates when all Pcols in a row equal NaN, and set all temperatures to NaN, except SST
# print(df1.loc[:,Pcols[1]].isna())  # logical output  using .eq(np.nan) DOES NOT WORK
# invalidate all temps and all calc depths if all pdepths[1:] = NaN
# df1.loc[df1.loc[:,Pcols[1:]].isna().apply(lambda x: all(x), axis=1),Tcols[1:]] = np.nan  # ASSUMES Tcols[0] = 'T0'
# print(df1.head(20))

# keep all temperature less than -1.8, set correcsponding calc dpths = 0
# for ii,tcol in enumerate(Tcols):
#     df1[tcol].where(df1[tcol]>=-1.8, np.nan, inplace=True) # args are cond, other (so acts like 'or')

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
            # df1 pressure columns are 'corrected for bias' and returned NO LONGER CALLED Pxcorr
            df1, bias = getOPbias(pcol,pdepths[ii],df1,bid,figspath)
            OPbias.append(bias)  # this is for writing to L2 file ???
        print(f'ocean pressure biases:{[bias for bias in OPbias]}')
        dfbias['pdepths'] = pdepths
        dfbias['OPbias'] = OPbias
        dfbias['Pcols'] = Pcols
        dfbias.to_csv(biasname)
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

# make depth columns, set all to zero.
for col in Dcols:
    df1[col] = 0.

# offset D0 (deeper) when the deepest measurement is deeper than pdepths[-1] (nominal), when offset is positive.
for ii,row in df1.iterrows():
    offset = df1[Pcols[-1]].iloc[ii]-pdepths[-1]
    if offset>0:
        df1['D0'].iloc[ii] += offset

fig,ax = plt.subplots(2,1,figsize=(15,5),sharex=True)
ax[0].plot(df1['Dates'],-1*df1['D0'],'.-')
ax[0].set_title('-1*D0 offset/yanked down when deepest pressure measurement is deeper than deepest nominal pressure.')
ax[1].plot(df1['Dates'],-1*df1[Pcols[-1]],'.-')
ax[1].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1*pdepths[-1],-1*pdepths[-1]],'r')
ax[1].set_title(f'Deepest pressure measurement {Pcols[-1]} and deepest nominal depth(r).')
if '300234063991680' in bid:
    dt1 = dt.datetime(2016,9,4)
    dt2 =  dt.datetime(2016,10,24)
elif '300234062491420' in bid:
    dt1 = dt.datetime(2016,8,22)
    dt2 = dt.datetime(2016,11,3)
elif '300234064737080' in bid:
    dt1 = dt.datetime(2017,9,10)
    dt2 = dt.datetime(2017,10,25)
ax[0].set_xlim([dt1,dt2])
ax[1].set_ylim([-1*pdepths[-1]-3,-1*pdepths[-1]+1])

fig.savefig(f'{figspath}/D0_tug.png')
plt.show()
print(df1.columns)

# plot OP bias corrected pressures
fig2,ax2 = plt.subplots(len(Pcols)+1,1,figsize=(15,12),sharex=True)
ax2[0].plot(df1['Dates'],df1['BP'],'.-')
ax2[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[1013,1013],'r-')
ax2[0].set_title('Measured Barometric Pressure')
ax2[0].set_xlim([dt1,dt2])
ax2[0].grid()
for ii,pcol in enumerate(Pcols):
    ax2[ii+1].plot(df1['Dates'],-1*df1[pcol],'b.')
    ax2[ii+1].set_title(f'{pcol} before (b) and after (g) SLP correction')
    ax2[ii+1].grid()

# correct pressure measurements for SLP
if 'BP' in df1.columns:  ## this is for AFTER 2014 ?  Wendy used 1015mb. Suzanne started using 1013 Nov 2022
    for pcol in Pcols:
        df1.loc[~np.isnan(df1['BP']),pcol] -= (df1.loc[~np.isnan(df1['BP']),'BP'] - 1013)*0.01
    OPcorr4SLP = 'YES'
else:
    OPcorr4SLP = 'NO'

# plot OP SLP corrected pressures
for ii,pcol in enumerate(Pcols):
    ax2[ii+1].plot(df1['Dates'],-1*df1[pcol],'g.')

fig2.savefig(f'{figspath}/SLPcorrection_Pcols.png')
plt.show()

### determine water/ice
print('Determining Water/Ice values')
IceInd = 'YES'
indicator = []
mindist = []
for index, row in df1.iterrows():
    # if df2['WaterIce'].iloc[index]==2:
        indi,mind = getBuoyIce(df1['Lon'].iloc[index],df1['Lat'].iloc[index],
                                df1['Year'].iloc[index],df1['Month'].iloc[index],df1['Day'].iloc[index],
                                df1['T0'].iloc[index],plott=0)
        indicator.append(indi)
        mindist.append(mind/1000) # in km
df1.insert(nextColNum,'WaterIce',indicator)

fig3,ax3 = plt.subplots(4,1,figsize=(15,15),sharex=True)
ax3[0].plot(df1['Dates'],df1['WaterIce'])
ax3[0].set_title('Water Ice indicator (1=ice, 2=water)')
ax3[1].plot(df1['Dates'],df1['T0'])
ax3[1].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1.8,-1.8],'r')
ax3[1].set_title('T0')

print(df1.columns)
# df1['mindist'] = mindist
f2.write(f'% {nextColNum} = Open Water or Ice Indicator (1=ice, 2=water)\n')
nextColNum += 1
print(nextColNum)

# find FWT only based on W/I indicator, to start
FirstTpodInd = 'YES'
SSTInd = 'YES'
df1['FirstTpod'] = 0
df1.loc[df1['WaterIce']==1,'FirstTpod'] = 1

# assume no ridging, unless we answer yes to questions below
df1['ridged'] = 0

fig0,ax0 = plt.subplots(1,1,figsize=(15,5))
ax0.plot(df1['Dates'],-1*df1['P1'],'b.-')
ax0.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
if '300234063991680' in bid:
    dt1=dt.datetime(2016,10,10)
    dt2=dt.datetime(2016,10,25)
elif '300234062491420' in bid:
    dt1=dt.datetime(2016,8,22)
    dt2=dt.datetime(2016,11,3)

secax=ax0.twinx()
secax.spines['right'].set_color('red')
# secax.set_ylim(940.0,1080)
secax.set_ylabel('Water(2), Ice(1)',color='r')
secax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
secax.plot(df1['Dates'],df1['WaterIce'],color='r',alpha=0.7)
ax0.set_xlim([dt1,dt2])
ax0.set_title(f'Ocean Pressure nominal depth {pdepths[0]} (b), Water(2)/Ice(1) indicator (r)')
ax0.grid()
fig0.savefig(f'{figspath}/P1_WaterIce.png')
plt.show()

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
    ax1.set_title(f'IceConc and track(b) on {dt.datetime(int(icedate[:4]),int(icedate[4:6]),int(icedate[6:]))}. Red shows entire track.')
    fig1.savefig(f'{figspath}/IceConc_Buoytrack_{icedate}.png')
    plt.show()

# find riding times (besides indicated by Water/Ice indicator), put in .csv file
rTimes = input('Do you want to make ridging time periods file? : y for Yes, n for No ')
if rTimes.startswith('y'):
    fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
    ax1.plot(df1['Dates'],-1*df1['P1'],'b.-')
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
rFile = input('Do you want to make ridging time periods file? : y for Yes, n for No ')
if rFile.startswith('y'):
    ridgeFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridging{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'
    dfr = pd.read_csv(ridgeFile)
    dfr['dt1'] = pd.to_datetime(dfr['dt1'],format='%Y-%m-%d %H:%M:%S')
    dfr['dt2'] = pd.to_datetime(dfr['dt2'],format='%Y-%m-%d %H:%M:%S')
    dfr.dropna(axis=0,how='all',inplace=True)

    # plot to ensure the ridged areas
    rcols = ['m','c','r','g','orange','m']
    fig3,ax3 = plt.subplots(4,1,figsize=(15,12),sharex=True)
    ax3[0].plot(df1['Dates'],-1*df1['P1'],'b.')

    df1['ridged'] = 0  # binary whether riding or no
    for ii,row in dfr.iterrows():
        # if ii==1:
        #     print(df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'Dates'])
            print(ii,row)
            ax3[0].plot(df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'Dates'],
                    -1*df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'P1'],
                    '.',color=rcols[ii])
            ax3[0].plot([dfr['dt1'].iloc[ii],dfr['dt2'].iloc[ii]],[dfr['OPlimit'].iloc[ii],dfr['OPlimit'].iloc[ii]],'k')
            df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridged'] = 1
    ax3[0].set_yticks(np.arange(np.floor(-1*df1['P1'].max()),np.ceil(-1*df1['P1'].min()),1))
    ax3[0].set_title('OP corrected for bias, colors for ridge levels')
    ax3[1].plot(df1['Dates'],df1['ridged'],'b.')
    ax3[1].set_title('Ridged: 0 = no, 1 = yes')
    ax3[2].plot(df1['Dates'],df1['WaterIce'],'b.')
    ax3[2].set_title('Water (2), Ice (1)')
    # looking at ridged areas and set FirstTpod (FWT)  NEEDS TO BE MODIFIED IF RIDGING INCLUDES SHALLOWEST PRESSURE SENSOR
    for ii,row in dfr.iterrows():
        for index,ridgerow in df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii])].iterrows():
            # how much ridging?
            # metersofRidge = pdepths[0] - df1['P1'].iloc[index]
            # numZeros = len([x for x in tdepths if x<metersofRidge])
            metersofRidge = pdepths[0] - df1.loc[index,'P1']
            numZeros = len([x for x in tdepths if x<metersofRidge])
            # set calculated depths 'shallower' than FWT as 0
            for dcol in Dcols[:numZeros]:
                df1.loc[index,dcol] = 0
            df1.loc[index,'FirstTpod'] = numZeros
# else:
#     pass
#     df1.loc[]
ax3[2].plot(df1['Dates'],df1['FirstTpod'],'r.')
ax3[2].set_title('First Wet Thermistor (zero based)')

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
    # temperature of FWT
    df1.loc[ii,'sst' ] = df1.loc[ii,Tcols[fwt]]
ax3[3].plot(df1['Dates'],df1['sst'],'r.')
ax3[3].set_title('SST')
for ax in ax3:
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.grid()
fig3.savefig(f'{figspath}/WaterIce_T0_FWT_SST.png')
plt.show()

# fig4,ax4 = plt.subplots(3,1,figsize=(15,12),sharex=True)
# ax4[0].plot(df1['Dates'],-1*df1['P1'],'b.')
# ax4[0].set_yticks(np.arange(np.floor(-1*df1['P1'].max()),np.ceil(-1*df1['P1'].min()),1))
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
#     # ax.set_xlim([dt1,dt2])
# plt.show()

ridgedPresFile = f'/Users/suzanne/Google Drive/UpTempO/level2/ridgedPressure{binf["name"][0]}-{int(binf["name"][1]):02d}.csv'

writeCSV = input('Do you want to make a new ridgePressure .csv now? : y for yes, n for no ')
if writeCSV.startswith('y'):
    df1['ridgedPressure'] = -1*pdepths[-1]

    for ii in range(len(dfr)):
        df1.loc[(df1['Dates']>=dfr['dt1'][ii]) & (df1['Dates']<=dfr['dt2'][ii]),'ridgedPressure'] = dfr['OPlimit'][ii]

    # col2move = df1.pop('Dates')
    # df1.insert(0,'Dates',col2move)
    # col2move = df1.pop('P1')
    # df1.insert(1,'P1',col2move)
    # col2move = df1.pop('ridgedPressure')
    # df1.insert(2,'ridgedPressure',col2move)
    # print(df1.head())

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

# dt1 = dt.datetime(2016,11,1)
# dt2 = dt.datetime(2016,11,5)
readCSV = input('Do you want to read in ridgePressure .csv now? : y for yes, n for no ')
if readCSV.startswith('y'):
    print(ridgedPresFile)
    df1a = pd.read_csv(ridgedPresFile)
    print(df1a.columns)
    # fig4,ax4 = plt.subplots(1,1,figsize=(15,6))
    # ax4.plot(df1['Dates'],-1*df1['P1corr'],'b.')
    # ax4.plot(df1['Dates'],df1a['ridgedPressure'],'r.-')
    # # ax4.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    # ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #%Y-%m-%dT%H:%M
    # ax4.set_yticks(np.arange(np.floor(-1*df1['P1corr'].max()),np.ceil(-1*df1['P1corr'].min()),1))
    # ax4.set_xlim(dt1,dt2)
    # ax4.set_title('manually edited Ridged Pressures (r), bias corrected OP (b)')
    # fig4.savefig(f'{figspath}/ManuallyRigedPressures_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    # plt.show()

# to determine if buoy is dragging on ocean bottom
bathyCalc = input('Do you want to find bathymetry? : y for Yes, n for No ')
if bathyCalc.startswith('y'):
    # fig4,ax4 = plt.subplots(1,1,figsize=(15,6))
    # ax4.plot(df1['Dates'],-1*df1['P1'],'b.')
    # ax4.plot(df1['Dates'],df1a['ridgedPressure'],'r.-')
    # ax4.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    # ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #%Y-%m-%dT%H:%M
    # ax4.set_yticks(np.arange(np.floor(-1*df1['P1'].max()),np.ceil(-1*df1['P1'].min()),1))
    # ax4.set_title('manually edited Ridged Pressures (r), bias corrected OP (b)')
    # plt.show()
    bathydate = input('Enter strdate (yyyymmdd) to find lon/lat for bathymetry calc: ')
    objbathy = dt.datetime.strptime(bathydate,'%Y%m%d')
    blon = df1.loc[(df1['Dates']>=objbathy) & (df1['Dates']<=objbathy+dt.timedelta(days=1)),'Lon'].mean()
    blat = df1.loc[(df1['Dates']>=objbathy) & (df1['Dates']<=objbathy+dt.timedelta(days=1)),'Lat'].mean()
    print(f'buoy location during dragging, {blon:.2f}E, {blat:.2f}N ')
    bathy = getBuoyBathy(blon,blat,lonlim=5,latlim=3)
    fig1, ax1 = plt.subplots(1,figsize=(8.3,10))
    ax1 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
    ax1.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
    ax1.add_feature(cfeature.LAND,facecolor='gray')
    # ax1.add_feature(cfeature.OCEAN,facecolor='lightblue')
    ax1.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
    kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
    ch = ax1.contourf(bathy.lon,bathy.lat,bathy.elevation,transform=ccrs.PlateCarree(),
                      levels=np.arange(-75,5,5),cmap='turbo')
    ax1.contour(bathy.lon,bathy.lat,bathy.elevation,transform=ccrs.PlateCarree(),
                      levels=pdepths,color='k')
    ax1.plot(blon,blat,'k*',markersize=12,
             transform=ccrs.PlateCarree(),label=f'Buoy location on {bathydate}')
    ax1.legend()
    fig1.colorbar(ch)
    fig1.savefig(f'{figspath}/Bathymetry_{bathydate}.png')
    plt.show()

if len(pdepths)>0:
    print('Interpolating calculated depths...')
    Pcols.insert(0,'D0')
    pdepths.insert(0,0.0)
    tcalcdepths=np.full([len(df1),len(tdepths)],np.nan)
    print('tcalc depths shape',tcalcdepths.shape)
    # n=0
    print('Pcols',Pcols)
    # for ii in range(30):
    #     print(ii,[df1[col].iloc[ii] for col in Pcols])
    # print()
    print(pdepths)
    numPs = len(Pcols)
    height = numPs*3
    fig,ax = plt.subplots(numPs,1,figsize=(15,height),sharex=True)
    for ii,pcol in enumerate(Pcols):
        ax[ii].plot(df1['Dates'].iloc[:50],-1*df1[pcol].iloc[:50],'.-')
        ax[ii].set_title(f'{pcol}')
        ax[ii].grid()

    for ii, row in df1.iterrows():
        if not df1['ridged'].iloc[ii]:
            pmeas = [df1[col].iloc[ii] for col in Pcols]
            pnoms = [df1[Pcols[0]].iloc[ii]]
            pnoms.extend(pdepths[1:])
            # print(ii)
            # print('pmeas',pmeas)
            # print('pnoms',pnoms)
            fi = interpolate.interp1d(pdepths,pmeas,fill_value = 'extrapolate')
            # fi = interpolate.interp1d(pdepths,pmeas,fill_value = 'extrapolate')
            tinvolved = tdepths
            tcalcdepths[ii,:] = fi(tinvolved)
            # print(fi(tinvolved))
            # if ii==50:
            #     exit(-1)
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
            # pmeas = list(itertools.chain.from_iterable([[0],df1[Pcolscorr[1:]].iloc[ii]]))
            pmeas = [df1[col].iloc[ii] for col in Pcols]
            deepestZero = df1['FirstTpod'].iloc[ii]
            pdepthsRidged = [-1*df1a['ridgedPressure'].iloc[ii]] #[x-tdepths[deepestZero-1] for x in pdepths[1:]]
            pdepthsRidged.insert(0,0)
            # print('pmeas',pmeas)
            # print('pdepthsRidged',pdepthsRidged)
            # print('deepestZero',deepestZero)
            fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')
            offset = pdepths[1] - pdepthsRidged[1]
            # print('offset',offset)
            tdepthsRidged = [x- offset for x in tdepths]  #( df1['P1corr'].iloc[ii] - pdepths[1])
            # print('tdepthsRidged',tdepthsRidged)
            tcalcdepths[ii,:] = fi(tdepthsRidged)
            # print('tcalcdepths',tcalcdepths[ii,:])
            tcalcdepths[ii,:deepestZero] = 0
                # exit(-1)
    tcalcdepths = np.array(tcalcdepths)
    print(tcalcdepths.shape)
    print(Dcols)
    print(tdepths)
    CalcDepths = 'YES'
else:
    CalcDepths = 'NO'


# dt1 = dt.datetime(2016,9,1)
# dt2 = dt.datetime(2017,11,1)

# fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
# for ii,dcol in enumerate(Dcols):
#     ax8.plot(df1['Dates'],df1[dcol],'.',color=cList[ii],label=f'{tdepths[ii]}')
# ax8.xaxis.set_major_locator(mdates.DayLocator(interval=2))
# ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# # ax8.set_yticks(np.arange(-26,1))
# ax8.set_title('Depths before interp; bias and yank only  ')
# ax8.grid()
# ax8.legend(loc='lower center')
# ax8.set_xlim(dt1,dt2)

for ii,dcol in enumerate(Dcols):
    df1[dcol] = tcalcdepths[:,ii]
    f2.write(f'% {nextColNum} = Calculated Depth at nominal depth {tdepths[ii]} (m)\n')
    nextColNum += 1
ax[0].plot(df1['Dates'].iloc[:50],-1*df1['D0'].iloc[:50],'rx')
fig.savefig(f'{figspath}/First50_Pcols_pdepth0_D0.jpg')
plt.show()


print(Tcols)
print(Dcols)
fig9,ax9 = plt.subplots(1,1,figsize=(15,10))
for ii in range(50):
    tees = [df1[tcol].iloc[ii] for tcol in Tcols]
    dees = [df1[dcol].iloc[ii] for dcol in Dcols]
    ax9.plot([tee+ii for tee in tees],[-1*dee for dee in dees],'.-')
    if not np.isnan([tees[indp] for indp in indP]).any():
        ax9.plot([tees[indp]+ii for indp in indP],[-1*df1[col].iloc[ii] for col in Pcols[1:]],'rx')
ax9.grid()
ax9.set_title('first 50 temperature profiles at calculated depths. Red xs show measured T/P.')
ax9.set_xlabel('Temperatures + index, to offset profiles for better viewing')
ax9.set_ylabel('Calculated Depths, (m)')
fig9.savefig(f'{figspath}/First50Tprofiles.png')
plt.show()

# # correct depths for sea level pressure variations
# slp = input('Do you want to compare Dcols before and after SLP correction?  Yes (y), No (n) ')
# if slp.startswith('y'):
#     DcolsSLP = [f'{col}SLP' for col in Dcols]
#     for dcol in DcolsSLP:
#         df1[dcol] = np.NaN
#     if 'BP' in df1.columns:  ## this is for AFTER 2014 ?  Wendy used 1015mb. Suzanne started using 1013 Nov 2022
#         for dcol in Dcols:
#             df1.loc[~np.isnan(df1['BP']),f'{dcol}SLP'] = df1.loc[~np.isnan(df1['BP']),dcol] - (df1.loc[~np.isnan(df1['BP']),'BP'] - 1013)*0.01
#
#     if '300234063991680' in bid:
#         dt1 = dt.datetime(2016,9,5)
#         dt2 = dt.datetime(2016,10,21)
#     elif '300234062491420' in bid:
#         dt1=dt.datetime(2016,8,22)
#         dt2=dt.datetime(2016,11,3)
#     fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
#     for ii,dcol in enumerate(Dcols):
#         ax8.plot(df1['Dates'],df1[dcol]-df1[f'{dcol}SLP'],'.-',color=colorList[ii],label=f'{tdepths[ii]}')
#     ax8.xaxis.set_major_locator(mdates.DayLocator(interval=10))
#     ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     # ax8.set_yticks(np.arange(-26,1))
#     ax8.set_title(f'Calculated Depths BEFORE SLP correction minus AFTER SLP correction{binf["name"][0]}-{int(binf["name"][1]):02d}')
#     ax8.grid()
#     ax8.legend(loc='lower center')
#     ax8.set_xlim(dt1,dt2)
#     fig8.savefig(f'{figspath}/CalcDepths_before-afterSLP_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
#     plt.show()
#     # remove the DxSLP cols
#     df1.drop(columns=[dcol for dcol in DcolsSLP],inplace=True)
#     print('columns after removing SLP correction columns')
#     print(df1.columns)
#
# print('line 650, Pcols',Pcols)
# print(pdepths)
#
# fig,ax = plt.subplots(1,1,figsize=(15,6),sharex=True)
# ax.plot(df1['Dates'],-1*df1['D0'],'r.-')
# ax.set_title('D0 before(r) and after(b) SLP correction, m')
#

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

fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
for ii,dcol in enumerate(Dcols):
    ax8.plot(df1['Dates'],-1*df1[dcol],'.-',color=colorList[ii],label=f'{tdepths[ii]}')
ax8.xaxis.set_major_locator(mdates.DayLocator(interval=10))
ax8.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# ax8.set_yticks(np.arange(-26,1))
ax8.set_title(f'Calculated Depths after SLP correction {binf["name"][0]}-{int(binf["name"][1]):02d}')
ax8.grid()
ax8.legend(loc='best')
ax8.set_xlim(dt1,dt2)
fig8.savefig(f'{figspath}/CalcDepths_afterSLP_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')

plt.show()


OPcorr4drift = 'NO'
Capped999 = 'YES'
DataFilt = 'YES'
f2.write(f'% {nextColNum} = First tpod in water\n')
f2.write(f'% {nextColNum+1} = Sea Surface Temperature\n')
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
f2.write(f'END\n')

df1.drop(columns=['ridged'],inplace=True)
print('line 773')
print(df1.columns)
print(Dcols)
for ii,dcol in enumerate(Dcols):
    print(ii,dcol)
print()
print()
print()
# plot L2 similar to L1 in waterIce.py, getL1
remcols = []
for col in df1.columns:
    fig,ax = plt.subplots(1,1,figsize=(15,5))
    if col.startswith('P'):
        ax.plot(df1['Dates'],-1*df1[col],'.')
    elif 'Lat' in col:
        if '300234064737080' in bid:
            df.loc[(df['Lon'])<0,'Lon'] += 360
        ax.plot(df1['Lon'],df1[col],'.')
        ax.plot(df1['Lon'].iloc[0],df1[col].iloc[0],'go')
        ax.plot(df1['Lon'].iloc[-1],df1[col].iloc[-1],'ro')
    elif 'Lon' in col:
        remcols.append(col)
    elif 'T0' in col:
        for ii,tcol in enumerate(Tcols):
            ax.plot(df1['Dates'],df1[tcol],'o',color=colorList[ii],ms=1)
            # ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    elif col.startswith('T') and 'T0' not in col:
        remcols.append(col)
    elif 'D0' in col:
        for ii,dcol in enumerate(Dcols):
            ax.plot(df1['Dates'],-1*df1[dcol],'o',color=colorList[ii],ms=1)
            # ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    elif col.startswith('D') and 'D0' not in col and 'Day' not in col:
        remcols.append(col)
    else:
        ax.plot(df1['Dates'],df1[col],'.')
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
    df1.drop(columns=[dcol for dcol in DcolsSLP])
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
uplotsL2.Batt_Sub(bid,figspath)
uplotsL2.VelocitySeries(bid,figspath)

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
