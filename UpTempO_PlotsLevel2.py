#!/usr/bin/python
import BuoyTools_py3_toot as BT
import PlottingFuncs as PF
import numpy as np
import UpTempO_BuoyMaster as BM
import UpTempO_Python as upp
import UpTempO_HeaderCodes as HC
import IABPplots as iplots
import ArcticPlots as aplots
# import ArcticPlots as aplots
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import (MONTHLY,DateFormatter,rrulewrapper,RRuleLocator,drange)
import cartopy.crs as ccrs
import re
import pandas as pd
from scipy import stats
from haversine import haversine

def TimeSeriesPlots(bid,path,quan='Temp'):
    print(f'plotting {quan} Time Series for {bid}')
    #quan = 'Temp' or 'Pressure'

    # cols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    cols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')
    tdepths = df['tdepths'].dropna()
    print('temperature nominal depths',tdepths)
    try:
        pdepths = df['pdepths']
        print('pressure nominal depths',pdepths)
    except:
        pass
    try:
        sdepths = df['sdepths']
        print('salinity nominal depths',pdepths)
    except:
        pass


    print(df.head())
    print(deplat,deplon)
    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])

    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')

    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18

    fig,ax=plt.subplots()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=85,labelsize=14)

    if quan == 'Temp':
        tcols = [col for col in df.columns if col.startswith('T')]
        yaxlab='Temperature (C)'
        ax.set_ylim(-2.0,10.0)

        for ii,tcol in enumerate(tcols):
            ax.plot(df['Date'],df[tcol],'-o',color=cols[ii],ms=1)

    if quan == 'Salinity':
        scols = [col for col in df.columns if col.startswith('S') and 'SUB' not in col]
        yaxlab='Salinity'
        ax.set_ylim(20,40)

        for ii,scol in enumerate(scols):
            ax.plot(df['Date'],df[scol],'-o',color=cols[ii],ms=1)

    if quan == 'Pressure':
        pcols = [col for col in df.columns if col.startswith('P') or col.startswith('CTD-P')]
        yaxlab='Ocean Pressure (dB)'
        maxdep=max(pdepths)
        ax.set_ylim(maxdep+10.,0)

        if 'BP' in df.columns:
            secax=ax.twinx()
            secax.spines['right'].set_color('red')
            secax.set_ylim(940.0,1080)
            secax.set_ylabel('Sea Level Pressure',color='r')
            df.loc[df['BP']<940,'BP']=np.nan
            secax.xaxis.set_major_formatter(formatter)
            secax.xaxis.set_major_locator(loc)
            secax.plot(df['Date'],df['BP'],color='r',alpha=0.7)

        for ii,pcol in enumerate(pcols):
            ax.plot(df['Date'],df[pcol],'-o',color=cols[ii],ms=1)

    datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
    plt.title(buoylab+' ('+bid+') '+yaxlab+' Time Series: '+datelab,fontsize=20)
    ax.set_ylabel(yaxlab)
    plt.subplots_adjust(bottom=0.15)
    plt.grid(True)
    plt.savefig(f'{path}/{quan}Series{abbv}L2.png')
    plt.show()

    # opr=open('UPTEMPO/transferRecord.dat','r')
    # tr=opr.read()
    # opr.close()
    # tr=tr.split('\n')
    #
    # outwrite='UPTEMPO/WebPlots/'+quan+'Series'+abbv+'.png WebPlots/'+quan+'Series'+abbv+'.png'
    # if outwrite not in tr:
    #     tr.append(outwrite)
    #     opw=open('UPTEMPO/transferRecord.dat','w')
    #     for t in tr: opw.write(t+'\n')
    #     opw.close()

def VelocitySeries(bid,path):

    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')
    print(df.head())
    print()
    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])

    df['DateBTN'] = np.nan
    df['DateBTN'].iloc[1:] = [df['Date'].iloc[i-1]+(df['Date'].iloc[i] - df['Date'].iloc[i-1])/2 for i in range(1,len(df))]
    df['DateBTN'] = pd.to_datetime(df['DateBTN'])
    df['SecondsDiff'] = df.loc[:,'Date'].diff()/np.timedelta64(1,'s')
    df['distm'] = np.nan
    
    df.loc[(df['Lon'])>180,'Lon'] -= 360

    for ii in range(1,len(df)):
        loc1 = (df['Lat'].iloc[ii-1],df['Lon'].iloc[ii-1])
        loc2 = (df['Lat'].iloc[ii],  df['Lon'].iloc[ii])
        df['distm'].iloc[ii] = haversine(loc1,loc2,unit='m')
    df['velocity'] = df['distm'] / df['SecondsDiff']

    # we want distance from beginning of day to end of day as the Arctic tern flies
    #  interpolat lon/lat to zero hour of each day, where date is in seconds
    origdate = df['Date'].to_numpy().astype(np.int64) // 10 ** 9
    daydate = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1],freq='D').floor('D').to_numpy().astype(np.int64) // 10 ** 9
    origlat = df['Lat'].to_numpy().astype(float)
    origlon = df['Lon'].to_numpy().astype(float)

    dfday = pd.DataFrame()
    dfday['date'] = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1],freq='D').floor('D')
    dfday['lat'] = np.interp(daydate,origdate,origlat)
    dfday['lon'] = np.interp(daydate,origdate,origlon)
    dfday['dist'] = np.nan
    for ii in range(1,len(dfday)):
        loc1 = (dfday['lat'].iloc[ii-1],dfday['lon'].iloc[ii-1])
        loc2 = (dfday['lat'].iloc[ii],  dfday['lon'].iloc[ii])
        dfday['dist'].iloc[ii] = haversine(loc1,loc2,unit='km')        # dayDate[ii] = daydate[ii] *
    dfday.loc[(dfday['dist'].diff().abs()<0.001),'dist'] = np.nan

    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')

    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18

    fig,ax=plt.subplots()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=85,labelsize=14)
    ax.set_ylim(0,2)
    ax.plot(df['DateBTN'],df['velocity'],'-ok',ms=3)

    secax=ax.twinx()
    secax.spines['right'].set_color('red')
    secax.set_ylim(-20,40)
    secax.set_ylabel('Daily Distance (km)',color='r')
    secax.xaxis.set_major_formatter(formatter)
    secax.plot(dfday['date'],dfday['dist'],'-or',alpha=0.5,ms=3)

    datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
    plt.title(buoylab+' ('+bid+') Velocity and Daily Distance '+datelab,fontsize=20)
    ax.set_ylabel('Velocity (m/s)')
    plt.subplots_adjust(bottom=0.15)
    plt.grid(True)
    plt.savefig(f'{path}/VelocitySeries{abbv}L2.png')

    plt.show()


def Batt_Sub(bid,path):
    print(f'plotting Battery Voltage and Submergence for {bid}')
    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')
    print('max submergence',df['SUB'].max(axis=0))
    print()
    print()

    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])

    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')

    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18

    fig,ax1=plt.subplots()
    ax1.xaxis.set_major_locator(loc)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.xaxis.set_tick_params(rotation=85,labelsize=14)

    if (df['SUB']>1).any():
        ax1.plot(df['Date'],df['SUB'],'k.-',ms=3)
    else:
        ax1.plot(df['Date'],df['SUB']*100,'k.-',ms=3)
    ax1.set_ylabel('Submergence Percent', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_ylim(-5,105)

    datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
    plt.title(buoylab+' ('+bid+') '+'Submergence Percent and Battery Voltage:'+datelab,fontsize=20)

    ax2 = ax1.twinx()
    ax2.xaxis.set_major_locator(loc)
    ax2.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_tick_params(rotation=85,labelsize=14)
    ax2.plot(df['Date'],df['BATT'],'r.-',ms=3)
    ax2.set_ylabel('Battery Voltage (V)', color='red')
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.set_ylim(5,20)
    ax2.grid(axis='y')
    plt.subplots_adjust(bottom=0.15)
    # plt.grid(True)
    plt.savefig(f'{path}/Submergence{abbv}L2.png')

    plt.show()

def transferList(writ):

    opr=open('UPTEMPO/transferRecord.dat','r')
    tr=opr.read()
    opr.close()
    tr=tr.split('\n')

    if writ not in tr:
        tr.append(writ)
        opw=open('UPTEMPO/transferRecord.dat','w')
        for t in tr:
            if t: opw.write(t+'\n')
        opw.close()


