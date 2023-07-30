#!/usr/bin/python
import BuoyTools_py3_toot as BT
import PlottingFuncs as PF
import numpy as np
import UpTempO_BuoyMaster as BM
import UpTempO_Python as upp
import UpTempO_HeaderCodes as HC
import IABPplots as iplots
import ArcticPlots as aplots
import PlottingFuncs as PF
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import (MONTHLY,DateFormatter,rrulewrapper,RRuleLocator,drange)
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import re
import pandas as pd
from scipy import stats
from haversine import haversine

def TimeSeriesPlots(bid,path,quan='Temp',df=None,tdepths=None,pdepths=None,sdepths=None,dt1=None,dt2=None):
    print(f'plotting {quan} Time Series for {bid}')

    #quan = 'Temp' or 'Pressure'

    # cols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    cols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    binf=BM.BuoyMaster(bid)

    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    if df is None:
        df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')

    if 'Temperature' in quan:
        if tdepths is None:
            tdepths = df['tdepths'].dropna()
            print('temperature nominal depths',tdepths)

    if 'Pressure' in quan:
        if pdepths is None:
            pdepths = df['pdepths']
            print('pressure nominal depths',pdepths)

    if 'Salinity' in quan:
        if sdepths is None:
            sdepths = df['sdepths']
            print('salinity nominal depths',pdepths)


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
    if dt1:
        ax.set_xlim([dt1,dt2])

    if quan == 'Temp':
        tcols = [col for col in df.columns if col.startswith('T') and not col.startswith('Tilt')]
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

    if quan == 'Tilt':
        tiltcols = [col for col in df.columns if col.startswith('Tilt')]
        yaxlab='Tilt (degrees from vertical)'
        # ax.set_ylim(20,40)

        for ii,tiltcol in enumerate(tiltcols):
            ax.plot(df['Date'],df[tiltcol],'-o',color=cols[ii],ms=1)

    datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
    plt.title(buoylab+' ('+bid+') '+yaxlab+' Time Series: '+datelab,fontsize=20)
    ax.set_ylabel(yaxlab)
    plt.subplots_adjust(bottom=0.15)
    plt.grid(True)
    plt.savefig(f'{path}/{quan}Series{abbv}.png')
    plt.show()

    opr=open('UPTEMPO/transferRecord.dat','r')
    tr=opr.read()
    opr.close()
    tr=tr.split('\n')
    
    outwrite='UPTEMPO/WebPlots/'+quan+'Series'+abbv+'.png WebPlots/'+quan+'Series'+abbv+'.png'
    if outwrite not in tr:
        tr.append(outwrite)
        opw=open('UPTEMPO/transferRecord.dat','w')
        for t in tr: opw.write(t+'\n')
        opw.close()

def VelocitySeries(bid,path,df=None,dt1=None,dt2=None):

    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    if df is None:
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
    if dt1:
        ax.set_xlim([dt1,dt2])
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

    plt.savefig(f'{path}/VelocitySeries{abbv}.png')

    plt.show()

    opr=open('UPTEMPO/transferRecord.dat','r')
    tr=opr.read()
    opr.close()
    tr=tr.split('\n')

    outwrite='UPTEMPO/WebPlots/VelocitySeries'+abbv+'.png WebPlots/VelocitySeries'+abbv+'.png'
    if outwrite not in tr:
        tr.append(outwrite)
        opw=open('UPTEMPO/transferRecord.dat','w')
        for t in tr: opw.write(t+'\n')
        opw.close()


def Batt_Sub(bid,path,df=None,dt1=None,dt2=None):
    print(f'plotting Battery Voltage and Submergence for {bid}')
    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    if df is None:
        df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')

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
    if dt1:
        ax1.set_xlim([dt1,dt2])

    if 'SUB' in df.columns:
        if (df['SUB']>1).any():
            ax1.plot(df['Date'],df['SUB'],'k.-',ms=3)
        else:
            ax1.plot(df['Date'],df['SUB']*100,'k.-',ms=3)
        ax1.set_ylabel('Submergence Percent', color='black')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.set_ylim(-5,105)

        if 'BATT' not in df.columns:
            datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
            plt.title(buoylab+' ('+bid+') '+'Submergence Percent:'+datelab,fontsize=20)

    if 'BATT' in df.columns:
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
        
        if 'SUB' not in df.columns:
            datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
            plt.title(buoylab+' ('+bid+') '+'Battery Voltage:'+datelab,fontsize=20)

    if 'SUB' in df.columns and 'BATT' in df.columns:
        datelab=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])} to {int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
        plt.title(buoylab+' ('+bid+') '+'Submergence Percent and Battery Voltage:'+datelab,fontsize=20)
    plt.savefig(f'{path}/Submergence{abbv}.png')

    plt.show()

    opr=open('UPTEMPO/transferRecord.dat','r')
    tr=opr.read()
    opr.close()
    tr=tr.split('\n')

    outwrite='UPTEMPO/WebPlots/Submergence'+abbv+'.png WebPlots/Submergence'+abbv+'.png'
    if outwrite not in tr:
        tr.append(outwrite)
        opw=open('UPTEMPO/transferRecord.dat','w')
        for t in tr: opw.write(t+'\n')
        opw.close()

def TrackMaps(bid,path,df=None):

    # ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    ucols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    plt=iplots.blankBathMap(cdomain='UpTempO')
    plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])

    if df is None:
        df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')

    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])


    for m in range(12):
        cm=m+1
        cdat=df['Month'] == cm  #data[data[:,imo] == cm,:]
        xar,yar=PF.LLtoXY(df['Lat'][cdat],df['Lon'][cdat],0.0)
        plt.plot(xar,yar,'o',ms=1.5,color='k',zorder=1)
        plt.plot(xar,yar,'o',ms=1,color=ucols[m],zorder=1)

    # plot the flag at end of track
    print(df['Lat'].iloc[-1],df['Lon'].iloc[-1])
    xf,yf=PF.LLtoXY([df['Lat'].iloc[-1]],[df['Lon'].iloc[-1]],0.0)
    plt.plot([xf,xf],[yf,yf+80],'k',linewidth=0.6,zorder=2)
    plt.scatter(xf+18,yf+80,s=40,c='r',marker='>',edgecolors='k',zorder=2)
    
    binf=BM.BuoyMaster(bid)
    startdate=f"{int(df['Month'].iloc[0]):02d}/{int(df['Day'].iloc[0]):02d}/{int(df['Year'].iloc[0])}"
    enddate  =f"{int(df['Month'].iloc[-1]):02d}/{int(df['Day'].iloc[-1]):02d}/{int(df['Year'].iloc[-1])}"
    titout='UpTempO '+binf['name'][0]+' #'+binf['name'][1]+' ('+bid+')  '+startdate+' to '+enddate

    outlabs=['Alaska','Russia','85N','80N','75N','90E','135E','180E','135W','90W']
    rot1=-20.0
    suby=100.
    outpos=[[-1400,2250,0,'w'],[1300.,2250,0,'w'],
            [110,550.-suby,rot1,'k'],[280,1070-suby,rot1,'k'],[560-suby,1590-suby,rot1,'k'],
            [700,10,0,'k'],[480,550,45,'k'],[-80,700,90,'k'],[-650,450,-45,'k'],[-900,10,0,'k']]
    for i,o in enumerate(outlabs):
        if i <= 1: fs=14
        else: fs=11
        plt.text(outpos[i][0],outpos[i][1],outlabs[i],rotation=outpos[i][2],color=outpos[i][3],fontsize=fs)


    plt.title(titout,fontsize=12)

    abbv=binf['imeiabbv']
    print(abbv)
    plt.savefig(f'{path}/TrackByMonth'+abbv+'.png',bbox_inches='tight')
    plt.show()

    opr=open('UPTEMPO/transferRecord.dat','r')
    tr=opr.read()
    opr.close()
    tr=tr.split('\n')

    outwrite='UPTEMPO/WebPlots/TrackByMonth'+abbv+'.png WebPlots/TrackByMonth'+abbv+'.png'
    if outwrite not in tr:
        tr.append(outwrite)
        opw=open('UPTEMPO/transferRecord.dat','w')
        for t in tr: opw.write(t+'\n')
        opw.close()

def TrackMaps2Atlantic(bid,path):

    # ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    ucols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    bscalegray=[50.,100.,500.,1000.,2000.,3000.]
    bscaleblack=[28.,60.]
    deepfillcol='beige' 

    # fig1, ax1 = plt.subplots(1,figsize=(6,6))
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

    bath=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATH-1041x1094.dat')
    bxx=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATHXX-1041x1094.dat')
    byy=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATHYY-1041x1094.dat')

    # rot=55.   # this has Greenland pointing down.
    # if rot:
    #     sqbxx=np.zeros((1094,1041))
    #     sqbyy=np.zeros((1094,1041))
    #     for r in range(1094): sqbxx[r,:]=bxx
    #     for r in range(1041): sqbyy[:,r]=byy
    #     fbxx=sqbxx.flatten()
    #     fbyy=sqbyy.flatten()
    #     lat,lon=PF.XYtoLL(fbxx,fbyy,0.0)
    #     bxx,byy=PF.LLtoXY(lat,lon,rot)
    #     bxx=np.reshape(bxx,(1094,1041))
    #     byy=np.reshape(byy,(1094,1041))
        
    ax1.contour(bxx*1000,byy*1000,-bath,bscalegray,colors='gray',linewidths=.5)
    # bathc=ax1.contour(bxx,byy,-bath,bscalegray,colors='gray',linewidths=.5)
    # if cdomain == 'UpTempO': pltt.contour(bxx,byy,-bath,bscaleblack,colors='black',linewidths=1)
    ax1.contourf(bxx*1000,byy*1000,-bath,[3000.,9000.],colors=deepfillcol)
    # ax1.axis('off')
    df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')

    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])

    for m in range(12):
        cm=m+1
        cdat=df['Month'] == cm  #data[data[:,imo] == cm,:]
        plt.plot(df['Lon'][cdat],df['Lat'][cdat],'o',ms=3,color='k',transform=ccrs.PlateCarree())
        plt.plot(df['Lon'][cdat],df['Lat'][cdat],'o',ms=2,color=ucols[m],transform=ccrs.PlateCarree())


    binf=BM.BuoyMaster(bid)
    startdate=f"{int(df['Month'].iloc[0]):02}/{int(df['Day'].iloc[0]):02}/{int(df['Year'].iloc[0])}"
    enddate  =f"{int(df['Month'].iloc[-1]):02}/{int(df['Day'].iloc[-1]):02}/{int(df['Year'].iloc[-1])}"
    # ax1.set_title(f"UpTempO {binf['name'][0]} #{binf['name'][1]} ({bid})\n{startdate} to {enddate}",fontsize=12)
    ax1.set_title(f"UpTempO {binf['name'][0]} #{binf['name'][1]} ({bid}) {startdate} to {enddate}",fontsize=12)

    outlabs=['Alaska','Russia','Greenland','85N','80N','75N','90E','135E','180E','135W','90W','45E','45W']
    rot1=-20.0
    suby=100.
    outpos=[[-1400,2250,0,'w'],[1300,2250,0,'w'],[-1400,-1300,0,'w'],
            [110,550.-suby,rot1,'k'],[280,1070-suby,rot1,'k'],[560-suby,1590-suby,rot1,'k'],
            [700,10,0,'k'],[460,550,45,'k'],[-80,700,90,'k'],[-650,450,-45,'k'],[-900,10,0,'k'],
            [480,-600,-45,'k'],[-590,-500,45,'k']]
    for i,o in enumerate(outlabs):
        if i <= 2: fs=14
        else: fs=11
        plt.text(outpos[i][0]*1000,outpos[i][1]*1000,outlabs[i],rotation=outpos[i][2],color=outpos[i][3],fontsize=fs)

    abbv=binf['imeiabbv']
    print(abbv,path)
    plt.savefig(f'{path}/TrackByMonth{abbv}.png',bbox_inches='tight')
    plt.show()

    outwrite='UPTEMPO/WebPlots/TrackByMonth'+abbv+'.png WebPlots/TrackByMonth'+abbv+'.png'
    transferList(outwrite)


# fig2, ax2 = plt.subplots(1,figsize=(8.3,10))
# ax2 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
# ax2.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
# ax2.add_feature(cfeature.LAND,facecolor='gray')
# # ax1.add_feature(cfeature.OCEAN,facecolor='lightblue')
# ax2.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
# ax2.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
# kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
# # ch = ax2.scatter(df1.loc[(df1['bathymetry']>=-75),'Lon'],
# #                  df1.loc[(df1['bathymetry']>=-75),'Lat'],s=5,
# #                c=df1.loc[(df1['bathymetry']>=-75),'bathymetry'],cmap='turbo',
# #                transform=ccrs.PlateCarree(),vmin=-75,vmax=0) #norm=mpl.colors.LogNorm(vmin=0,vmax=20))
# ch = ax2.scatter(df1['Lon'],df1['Lat'],s=5,c=df1['bathymetry'],cmap='turbo',
#     plt=iplots.blankBathMap(cdomain='UpTempO')
#     plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])

#     df = pd.read_csv(f'{path}/QualityControlled_{bid}.csv')

#     df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])

#     for m in range(12):
#         cm=m+1
#         cdat=df['Month'] == cm  #data[data[:,imo] == cm,:]
#         xar,yar=PF.LLtoXY(df['Lat'][cdat],df['Lon'][cdat],0.0)
#         plt.plot(xar,yar,'o',ms=1.5,color='k')
#         plt.plot(xar,yar,'o',ms=1,color=ucols[m])

#     binf=BM.BuoyMaster(bid)
#     startdate=f"{df['Month'].iloc[0]:02}/{df['Day'].iloc[0]:02}/{df['Year'].iloc[0]}"
#     enddate  =f"{df['Month'].iloc[-1]:02}/{df['Day'].iloc[-1]:02}/{df['Year'].iloc[-1]}"
#     titout='UpTempO '+binf['name'][0]+' #'+binf['name'][1]+' ('+bid+')  '+startdate+' to '+enddate

#     outlabs=['Alaska','Russia','85N','80N','75N','90E','135E','180E','135W','90W']
#     rot1=-20.0
#     suby=100.
#     outpos=[[-1400,2250,0,'w'],[1300.,2250,0,'w'],
#             [110,550.-suby,rot1,'k'],[280,1070-suby,rot1,'k'],[560-suby,1590-suby,rot1,'k'],
#             [700,10,0,'k'],[480,550,45,'k'],[-80,700,90,'k'],[-650,450,-45,'k'],[-900,10,0,'k']]
#     for i,o in enumerate(outlabs):
#         if i <= 1: fs=14
#         else: fs=11
#         plt.text(outpos[i][0],outpos[i][1],outlabs[i],rotation=outpos[i][2],color=outpos[i][3],fontsize=fs)


#     plt.title(titout,fontsize=12)

#     abbv=binf['imeiabbv']
#     print(abbv)
#     plt.savefig(f'{path}/TrackByMonth'+abbv+'.png',bbox_inches='tight')
#     plt.show()


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


