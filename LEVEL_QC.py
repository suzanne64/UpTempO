#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:48:43 2022

@author: suzanne
"""
import re, sys
import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt
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
from waterIce import getBuoyIce

# loca = np.array([[20, 3],
#                  [0,0],
#                  [0,25],
#                  [25,0],
#                  [25,25]])
# dm = pdist(loca)
# print(loca)
# print(dm[0:loca.shape[0]-1])
# exit(-1)

cList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

level1Path = '/Volumes/GoogleDrive/My Drive/UpTempO/UPTEMPO/WebData/LEVEL1'
level2Path = '/Volumes/GoogleDrive/My Drive/UpTempO/UPTEMPO/WebData/LEVEL2'

nopresbids=['300534062158460','300534062158480']
nosalibids=['300534060051570','300534060251600','300234068519450']
bid='300234064735100'   # pressure no sal
# bid='300534062158460'     # sal no pressure
binf = BM.BuoyMaster(bid)

level1File = f'UpTempO_{binf["name"][0]}_{int(binf["name"][1]):02d}_{binf["vessel"]}-FINAL.dat'
level2File = f'UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'

# log_file = f'{level2Path}/QualityControlMods_{bid}.log'
# fhlog = open(log_file,'a')
today = dt.date.today()
todaystr = f'{today.year}-{today.month:02}-{today.day:02}:\n'
# fhlog.write('{}: No beam pair {} data\n'.format(ATL11_file_str,pair))

# print(binf)
# read in level1 header and write to level2 header
f1 = open(f'{level1Path}/{level1File}','r')
f2 = open(f'{level2Path}/{level2File}','w')
lines = f1.readlines()
for line in lines:
    if line.startswith('%') and 'FILE UPDATE' not in line and 'END' not in line:
        f2.write(line)
        if 'WMO' in line:
            f2.write(f'%MANUFACTURER: {binf["brand"]}\n')
        if '=' in line:
            # get col number
            col_number = int(re.search(r'\% (.*?) =',line).group(1).strip(' '))
f2.write(f'% {col_number+1} = Open Water or Ice Indicator (1=ice, 2=water)')        
f2.close()
f1.close()

baseheader ={'year':'Year',         # key from Level 1, value from ProcessedRaw and used here
             'month':'Month',
             'day':'Day',
             'hour':'Hour',
             'Latitude':'Lat',
             'Longitude':'Lon'}
columns = ['Year','Month','Day','Hour','Lat','Lon']

if bid == '300534062158460' or bid == '300534062158480':    # these don't have pressures or depths
    pdepths = [0.28]
else:
    pdepths = [0.]

tdepths = []
sdepths = []
pcols = []
pnum = 1
tnum = 0 
snum = 0 

# convert Level 1 .dat to pandas dataFrame
with open(f'{level1Path}/{level1File}','r') as f:
    lines = f.readlines()
    for ii,line in enumerate(lines):
        # print(ii,line)
        if line.startswith('%'):
            if 'year' in line:
                pass
            if 'Ocean Pressure' in line:
                pcols.append( int(re.search(r'\% (.*?)= Ocean Pressure',line).group(1).strip(' ')) )
                columns.append(f'P{pnum}')                
                pnum += 1
                pdepths.append( float(re.search(r'Nominal Depth = (.*?) m\)',line).group(1).strip(' ')) )
            if 'Temperature at nominal depth' in line:
                tdepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                columns.append(f'T{tnum}')  
                tnum += 1
            if 'Salinity at nominal depth' in line:
                sdepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                columns.append(f'S{snum}')  
                snum += 1
            if 'Sea Level Pressure' in line:
                columns.append('BP')
            if 'Battery Voltage' in line:
                columns.append('BATT')
            if 'Submergence Percent' in line:
                columns.append('SUB')
            if '%END' in line:
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) #ii+1,len(lines)+1)]
                df = pd.DataFrame(data=data,columns=columns)
                # print((df == -999).sum())
                # print((df == -99).sum())
                df[df==-999] = np.NaN
                df[df==-99] = np.NaN
                if bid != '300534062158460' and bid != '300534062158480':    # these don't have pressures or depths
                    df.insert(6,'P0',0.00)
                else: 
                    df.insert(6,'P0',0.28)
                if pdepths:
                    pdepths = np.array(pdepths)
                if tdepths:
                    tdepths = np.array(tdepths)
                if sdepths:
                    sdepths = np.array(sdepths)

# add dates column for plotting
df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
# uniqueDates = df['Dates'].dt.date.unique()
# print(df.groupby(['Dates'].dt.date.unique()))
# print(uniqueDates)
# exit(-1)

# fig2,ax2 = plt.subplots(1,1,figsize=(10,5))
# ax2.scatter(df['Dates'],-1*df['P1'],10,cList[1]) #,picker=True, pickradius=5)
# # ax1.set_ylim([-100,0])
# ax2.set_title('P1, L1 no editing')
# ax2.grid()    

# # if not submerged, remove,  I guess not
# df = df[df.SUB != 0]
# df=df.reset_index(drop=True)  # pandas would keep the orig index if didn't drop=True

# implement data clean up (see weCode/LEVEL_2_IDL_CODE/READ_ME.txt)
# remove duplicate lines
df.drop_duplicates(inplace=True)
df=df.reset_index(drop=True) 

# all -99s and -999s have been set to np.NaN, reset NaNs to -999s later, when writing Level-2 ascii

# sort by increasing date, over four cols
df.sort_values(by=['Year','Month','Day','Hour'],inplace=True)
df=df.reset_index(drop=True)

###### 
# get water or Ice column
indicator = []
mindist = []
for index, row in df.iterrows():
        indi,mind = getBuoyIce(df['Lon'].iloc[index],df['Lat'].iloc[index],
                                df['Year'].iloc[index],df['Month'].iloc[index],df['Day'].iloc[index],
                                df['T0'].iloc[index])
        indicator.append(indi)
        mindist.append(mind)
fig0,ax0 = plt.subplots(1,1)
ax0.plot(mindist,indicator)
plt.show()


exit(-1)
df.insert(len(df.columns)-1,'WaterIce',np.array(indicator))
print(df.head())
    
# get columns used for data cleanup
Tcols = [col for col in df.columns if col.startswith('T')]
Pcols = [col for col in df.columns if col.startswith('P')]
Scols = [col for col in df.columns if col.startswith('S') and not col.startswith('SUB')]

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
        df.loc[df[pcol]>np.max(pdepths[ii])+5]= np.nan
    
# fig3,ax3 = plt.subplots(1,1,figsize=(10,5))
# for ii,pcol in enumerate(Pcols):
#     ax3.scatter(df['Dates'],-1*df[pcol],10,cList[ii]) #,picker=True, pickradius=5)
# ax3.set_title(' after 0s to nans')
# ax3.grid()

dt1=[]
y1=[]
def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    dt1.append(xdata[ind])
    y1.append(ydata[ind])
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)
    plt.plot(xdata[ind],ydata[ind],'ro')
    event.canvas.draw()
    props = dict(ind=ind, pickx = xdata[ind], picky=ydata[ind])
    return props

def wtf(line, event):
    if event.xdata is None:
        return False, dict()
    else: 
        print('x click',event.xdata)
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    maxd = 1
    d = np.sqrt( (xdata - event.xdata)**2 )
    ind, = np.nonzero(d<=maxd)
    if len(ind):
        pickx=xdata[ind]
        picky=xdata[ind]
        props = dict(ind=ind,pickx=pickx,picky=picky)
        return True, props
    else:
        return False, dict()
        

def press_return(event):
    print('you pressed', event.key, event.sdata, event.ydata)
    # thisline = event.artist
    # xdata = thisline.get_xdata()
    # ydata = thisline.get_ydata()
    # ind = event.ind
    # dt1.append(xdata[ind])
    # y1.append(ydata[ind])
    # points = tuple(zip(xdata[ind], ydata[ind]))
    # print('onpick points:', points)
    # plt.plot(xdata[ind],ydata[ind],'ro')
    # event.canvas.draw()

if 'P1' in df.columns:    
    dfday = df.groupby(pd.Grouper(key='Dates',freq='D'))['P1'].max()
    print(dfday.head())
    print(df.head(45))
# exit(-1)
# following Wendy's FineTuenOPbias subroutine in QC_FUNCTIONS_UPTEMPO.pro
for ii,pcol in enumerate(Pcols):
    # if pcol != 'P0':
    if pcol == 'P1':
        print(pcol,ii)
        print()
        # dfday = df.groupby(pd.Grouper(key='Dates',freq='D'))[pcol].max()
        fig5,ax5 = plt.subplots(1,1,figsize=(15,5))
        # ax5.plot(df['Dates'],-1*df[pcol],'ko-',linewidth=4)
        ax5.plot(-1*df.groupby(pd.Grouper(key='Dates',freq='D'))[pcol].max(),'gx-')
        medians = -1*df.groupby(pd.Grouper(key='Dates',freq='D'))[pcol].max().rolling(7,center=True).median()
        print('medians',medians)
        lline, = ax5.plot(medians,'b+-',picker=wtf,pickradius=1)
        
        print(lline)
        ax5.set_ylim([-1*pdepths[ii]-5,0])
        # ax5.set_xlim([dt.datetime(2018,9,18,0,0,0),dt.datetime(2018,9,19,0,0,0)])
        ax5.grid()
        fig5.canvas.mpl_connect('pick_event', onpick)
        cid = fig5.canvas.mpl_connect('key_press_event', press_return)

print('picked data',dt1,y1)
plt.show()
exit(-1)
# # OP bias datastrings
# if binf['name'][0] == '2018' and binf['name'][1] == '2':
#     datestr1 = '2018-09-20 06:00:00'
#     datestr2 = '2018-09-24'

# # fhlog.close()








# # temperatures
# fig0,ax0 = plt.subplots(1,1,figsize=(10,5))
# for ii,tcol in enumerate(Tcols):
#     ax0.scatter(df['Dates'],df[tcol],10,cList[ii])  #,picker=True, pickradius=5)
#     # ax0.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
#     #             df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),tcol],10,cList[ii])  #,picker=True, pickradius=5)
# ax0.set_ylim([-20,20])
# ax1.set_title(f'Temperatures for {bid}')
# ax0.grid()    

# # salinities
# fig1,ax1 = plt.subplots(1,1,figsize=(10,5))
# for scol in Scols:
#     ax1.scatter(df['Dates'],df[scol],10,cList[ii])  #,picker=True, pickradius=5)
#     # ax0.scatter(df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),'Dates'],
#     #             df.loc[(df.Dates >= datestr1) & (df.Dates < datestr2),tcol],10,cList[ii])  #,picker=True, pickradius=5)
# ax1.set_ylim([32,37])
# ax1.set_title(f'Salinities for {bid}')
# ax1.grid()    


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


# calculating depths by interpolation                
pressureCols = [col for col in df.columns if col.startswith('P')]
CalcDepthCols = [f'CalcDepth{col}' for col in df.columns if col.startswith('T')]
print(CalcDepthCols)

# make dataFrame for calculated depths of the thermistors
# dft = pd.DataFrame(columns=CalcDepthCols)
tcalcdepths = []
for ii in range(len(df)):
    fi = interpolate.interp1d(pdepths,df[pressureCols].iloc[ii])            
    # temperatureDepths.vstack(fi(tdepths))
    tcalcdepths.append(fi(tdepths))

tcalcdepths = np.asarray(tcalcdepths)
dftcalcdepths = pd.DataFrame(data=tcalcdepths,columns=CalcDepthCols)     
print(dftcalcdepths.head())      
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
                
                

# CD.CalculateDepths(bid)