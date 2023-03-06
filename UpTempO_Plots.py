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

def TimeSeriesPlots(bid,quan='Temp'):
    print(f'plotting {quan} Time Series for {bid}')
    #quan = 'Temp' or 'Pressure'

    # cols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    cols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'UPTEMPO/Processed_Data/{bid}.csv')
    print(df.head())
    print(deplat,deplon)
    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])
    depdate = df.loc[(df['Lon']==deplon) & (df['Lat']==deplat),'Date'].iloc[0]

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
        tcols = [col for col in df.columns if col.startswith('T') or col.startswith('CTD-T')]
        tcolsD = {}
        if 'tdepths' in binf:
            tdepths = binf['tdepths']
        if 'CTDtdepths' in binf:
            CTDtdepths = binf['CTDtdepths']
        if 'HULLtdepths' in binf:
            HULLtdepths = binf['HULLtdepths']

        for tcol in tcols:
            if tcol.startswith('CTD-T'):
                tcolsD[tcol] = CTDtdepths.pop(0)
            if tcol.startswith('T') and not tcol.startswith('Thull'):
                tcolsD[tcol] = tdepths.pop(0)
            if tcol.startswith('Thull'):
                tcolsD[tcol] = HULLtdepths.pop(0)
        tcolsD = dict(sorted(tcolsD.items(), key=lambda item:item[1]))
        print(tcolsD)
        depths = tcolsD.values()

        if bid=='300534062158480' or bid=='300534062158460':
            depths=[0.28]  # all data at depth=0 are null.
        # ind1=[header.index(item) for item in header if item.startswith('T')]
        yaxlab='Temperature (C)'
        if bid == '300234061160500': ax.set_ylim(-2.0,2.0)
        else: ax.set_ylim(-2.0,10.0)

        plot = (df['Date']>=depdate)
        for t,tcol in enumerate(tcols):
            ax.plot(df['Date'][plot],df[tcol][plot],'-o',color=cols[t],ms=1)

    if quan == 'Salinity':
        scols = [col for col in df.columns if (col.startswith('S') or col.startswith('CTD-S')) and 'SUB' not in col]
        scolsD = {}
        if 'sdepths' in binf:
            sdepths = binf['sdepths']
        if 'CTDsdepths' in binf:
            CTDsdepths = binf['CTDsdepths']
        if 'HULLsdepths' in binf:
            HULLsdepths = binf['HULLsdepths']

        for scol in scols:
            if scol.startswith('CTD-S'):
                scolsD[scol] = CTDsdepths.pop(0)
            if scol.startswith('S') and not scol.startswith('Shull'):
                scolsD[scol] = sdepths.pop(0)
            if scol.startswith('Shull'):
                scolsD[scol] = HULLsdepths.pop(0)
        scolsD = dict(sorted(scolsD.items(), key=lambda item:item[1]))
        print('scolsD')
        depths = scolsD.values()
        yaxlab='Salinity'
        ax.set_ylim(20,40)

        plot = (df['Date']>=depdate)
        for t,scol in enumerate(scols):
            ax.plot(df['Date'][plot],df[scol][plot],'-o',color=cols[t],ms=1)


    # havepressures=1
    # havebp=1
    if quan == 'Pressure':
        pcols = [col for col in df.columns if col.startswith('P') or col.startswith('CTD-P')]
        pcolsD = {}
        if 'CTDpdepths' in binf:
            CTDpdepths = binf['CTDpdepths']
        if 'pdepths' in binf:
            pdepths = binf['pdepths']

        for pcol in pcols:
            if pcol.startswith('CTD-P'):
                pcolsD[pcol] = CTDpdepths.pop(0)
            if pcol.startswith('P'):
                pcolsD[pcol] = pdepths.pop(0)
        pcolsD = dict(sorted(pcolsD.items(), key=lambda item:item[1]))
        print(pcolsD)
        depths = pcolsD.values()
        yaxlab='Ocean Pressure (dB)'
        maxdep=max(depths)
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

        plot = (df['Date']>=depdate)
        for t,pcol in enumerate(pcols):
            ax.plot(df['Date'][plot],df[pcol][plot],'-o',color=cols[t],ms=1)
        # if 'pdepths' in binf:
        #     depths=binf['pdepths']
        #     ind1=header.index('P1')
        # else:
        #     if 'ddepths' in binf:
        #         depths=binf['ddepths']
        #         ind1=header.index('D2')
        #     else:
        #         havepressures=0

    #     if 'BP' in df.columns:
    #         islp=header.index('BP')
    #     else:
    #         havebp=0
    #
    #     # if havepressures:
    #     #     yaxlab='Ocean Pressure (dB)'
    #     #     maxdep=np.max(depths)
    #     #     ax.set_ylim(maxdep+10.,0)
    #
    # if havepressures:
    #     nt=len(depths)
    #     if quan=='Pressure':
    #         vals=data[:,ind1:ind1+nt]
    #     else:
    #         vals=data[:,ind1]
    #
    #     if quan == 'Pressure':
    #         # secax.set_ticks()
    #
    #     for t in range(nt):
    #         cvals=vals[:,t]
    #         ax.plot_date(dateobjs,cvals,'-o',color=cols[t],ms=1)
    #

    # datelab=" %.2d/%.2d/%d to %.2d/%.2d/%d" % (dateobjs[0].month,dateobjs[0].day,dateobjs[0].year,dateobjs[-1].month,dateobjs[-1].day,dateobjs[-1].year)
    datelab=f"{df['Month'].iloc[0]:02}/{df['Day'].iloc[0]:02}/{df['Year'].iloc[0]} to {df['Month'].iloc[-1]:02}/{df['Day'].iloc[-1]:02}/{df['Year'].iloc[-1]}"
    plt.title(buoylab+' ('+bid+') '+yaxlab+' Time Series: '+datelab,fontsize=20)
    ax.set_ylabel(yaxlab)
    plt.subplots_adjust(bottom=0.15)
    plt.grid(True)
    plt.savefig('UPTEMPO/WebPlots/'+quan+'Series'+abbv+'.png')
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

def VelocitySeries(bid):

    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'UPTEMPO/Processed_Data/{bid}.csv')
    print(df.head())
    print()
    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])
    depdate = df.loc[(df['Lon']==deplon) & (df['Lat']==deplat),'Date'].iloc[0]

    # # make daily means
    # dfdaily = df.groupby(pd.Grouper(key='Date',freq='1D')).mean()
    # dfdaily.reset_index(inplace=True)
    # dfdaily['DateBTN'] = dfdaily.loc[:,'Date']+dfdaily.loc[:,'Date'].diff()/2
    # dfdaily['DateDiff'] = dfdaily.loc[:,'Date'].diff()/np.timedelta64(1,'s')


    # NOT daily, instead for each data row: datetime vector for plotting velocity
    # df['DateBTN'] = df.loc[:,'Date']+df.loc[:,'Date'].diff()/2
    df['DateBTN'] = np.nan
    df['DateBTN'].iloc[1:] = [df['Date'].iloc[i-1]+(df['Date'].iloc[i] - df['Date'].iloc[i-1])/2 for i in range(1,len(df))]
    df['DateBTN'] = pd.to_datetime(df['DateBTN'])
    df['SecondsDiff'] = df.loc[:,'Date'].diff()/np.timedelta64(1,'s')
    df['distm'] = np.nan
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
    # fig,ax = plt.subplots(1,1)
    # # ax.plot(df['Date'],df['Lat'],'k.-')
    # print(dfday['dist'])
    # print()
    # ax.plot(dfday['date'],dfday['dist'],'r.-')
    # ax.grid()
    # plt.show()
    # exit(-1)
    # make daily sums
    # dfdailysum = df.groupby(pd.Grouper(key='Date',freq='1D')).sum()

    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')

    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18

    fig,ax=plt.subplots()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=85,labelsize=14)
    if bid == '300534062894700':
        print('what up')
        # plt.show()
    ax.set_ylim(0,2)
    ax.plot(df['DateBTN'],df['velocity'],'-ok',ms=3)
    # plt.show()
    # exit(-1)

    # #-- daily distance --
    # intdoys=[int(d) for d in doys]
    # udoys=[]
    # for i in intdoys:
    #     if i not in udoys: udoys.append(i)
    #
    # intdoys=np.asarray(intdoys)
    # lats=np.asarray(lats)
    # lons=np.asarray(lons)
    # sto=[]
    #
    # # if bid=='300534060051570':
    # #     exit(-1)
    # for ii,ud in enumerate(udoys):
    #     wud=intdoys == ud
    #     if np.sum(wud) > 15:
    #         cll=[ud,lats[wud][0],lats[wud][-1],lons[wud][0],lons[wud][1],s[ii]]
    #         sto.append(cll)
    #
    # nsto=np.asarray(sto)
    # startlats=nsto[:,1]
    # endlats=nsto[:,2]
    # startlons=nsto[:,3]
    # endlons=nsto[:,4]
    # dists=PF.dist_ll(startlats,startlons,endlats,endlons)
    # doys=nsto[:,0]

    secax=ax.twinx()
    secax.spines['right'].set_color('red')
    secax.set_ylim(-20,40)
    secax.set_ylabel('Daily Distance (km)',color='r')
    secax.xaxis.set_major_formatter(formatter)
    secax.plot(dfday['date'],dfday['dist'],'-or',alpha=0.5,ms=3)

    datelab=f"{df['Month'].iloc[0]:02}/{df['Day'].iloc[0]:02}/{df['Year'].iloc[0]} to {df['Month'].iloc[-1]:02}/{df['Day'].iloc[-1]:02}/{df['Year'].iloc[-1]}"
    plt.title(buoylab+' ('+bid+') Velocity and Daily Distance '+datelab,fontsize=20)
    ax.set_ylabel('Velocity (m/s)')
    plt.subplots_adjust(bottom=0.15)
    plt.grid(True)
    plt.savefig('UPTEMPO/WebPlots/VelocitySeries'+abbv+'.png')

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

def Batt_Sub(bid):
    print(f'plotting Battery Voltage and Submergence for {bid}')
    binf=BM.BuoyMaster(bid)
    deplat = binf['deploymentLat']
    deplon = binf['deploymentLon']

    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    df = pd.read_csv(f'UPTEMPO/Processed_Data/{bid}.csv')
    print('max submergence',df['SUB'].max(axis=0))
    print()
    print()

    df['Date'] = pd.to_datetime(df[['Year','Month','Day','Hour']])
    depdate = df.loc[(df['Lon']==deplon) & (df['Lat']==deplat),'Date'].iloc[0]
    print(depdate)

    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')


    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18

    fig,ax1=plt.subplots()
    ax1.xaxis.set_major_locator(loc)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.xaxis.set_tick_params(rotation=85,labelsize=14)

    # #convert date to doy
    # doys=[]
    # dyears=[]
    # batt=[]
    # subm=[]
    # uyears=[]
    # for d in range(len(data)):
    #     cdoy=BT.dateToDOY(year=data[d,0],month=data[d,1],day=data[d,2],hour=data[d,3])
    #     doys.append(float(cdoy))
    #     dyears.append(data[d,0])
    #     batt.append(data[d,-2])
    #     subm.append(data[d,-1])
    #     if data[d,0] not in uyears: uyears.append(data[d,0])
    #
    # if len(uyears) > 1:
    #     addinf={}
    #     for y in range(len(uyears)-1):
    #         if BT.isLeap(uyears[y]): addinf[uyears[y+1]]=366.
    #         else: addinf[uyears[y+1]]=365.
    #
    #     addinf[uyears[0]]=0
    #
    #     dyears=np.asarray(dyears)
    #     doys=np.asarray(doys)
    #     for uy in uyears:
    #         w=dyears == uy
    #         doys[w]=doys[w]+addinf[uy]
    #
    ax1.plot(df['Date'],df['SUB']*100,'k.-',ms=3)
    ax1.set_ylabel('Submergence Percent', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_ylim(-5,105)

    datelab=f"{df['Month'].iloc[0]:02}/{df['Day'].iloc[0]:02}/{df['Year'].iloc[0]} to {df['Month'].iloc[-1]:02}/{df['Day'].iloc[-1]:02}/{df['Year'].iloc[-1]}"
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
    plt.savefig('UPTEMPO/WebPlots/Submergence'+abbv+'.png')

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


def TrackMaps(bid):

    # ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    ucols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    plt=iplots.blankBathMap(cdomain='UpTempO')
    plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])

    df = pd.read_csv('UPTEMPO/Processed_Data/'+bid+'.csv')

    #
    # opf=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    # header=opf.readline()
    # opf.close()
    # header=header.split(' ')
    # ilat=header.index('Lat')
    # ilon=header.index('Lon')
    # imo=header.index('Month')
    #
    # data=np.loadtxt('UPTEMPO/Processed_Data/'+bid+'.dat',skiprows=1)
    for m in range(12):
        cm=m+1
        cdat=df['Month'] == cm  #data[data[:,imo] == cm,:]
        xar,yar=PF.LLtoXY(df['Lat'][cdat],df['Lon'][cdat],0.0)
        plt.plot(xar,yar,'o',ms=1.5,color='k')
        plt.plot(xar,yar,'o',ms=1,color=ucols[m])

    binf=BM.BuoyMaster(bid)
    startdate=f"{df['Month'].iloc[0]:02}/{df['Day'].iloc[0]:02}/{df['Year'].iloc[0]}"
    enddate  =f"{df['Month'].iloc[-1]:02}/{df['Day'].iloc[-1]:02}/{df['Year'].iloc[-1]}"
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
    plt.savefig('UPTEMPO/WebPlots/TrackByMonth'+abbv+'.png',bbox_inches='tight')
    plt.show()

    outwrite='UPTEMPO/WebPlots/TrackByMonth'+abbv+'.png WebPlots/TrackByMonth'+abbv+'.png'
    transferList(outwrite)

# def OverviewMap(regen='none'):

# #    ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
#     ucols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
#     scale=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]


#     if regen != 'none':
#         plt=iplots.blankSSTMap(cdomain='UpTempO',udomain=[-2000,2000,-2500,2500],rot=0,fsize=(8.3,10),strdate=regen)
#         tyr=regen[0:4]
#         tmo=regen[4:6]
#         tda=regen[6:]
#     else:
#         today=datetime.datetime.now()
#         tyr=today.year
#         tmo=today.month
#         tda=today.day

#         plt=iplots.blankSSTMap(cdomain='UpTempO',udomain=[-2000,2000,-2500,2500],rot=0,fsize=(8.3,10))

#     plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])


#     curbuoys,deadbuoys,orderbuoys,deadbuoys=BM.getBuoys()
#     for c in curbuoys:
#         opf=open('UPTEMPO/Processed_Data/'+c+'.dat','r')
#         data=opf.read()
#         opf.close()
#         data=data.split('\n')
#         data=[da for da in data if da]
#         head=data[0]

#         if regen != 'none':
#             foundlast=0
#             for d in data:
#                 sd=d.split(' ')
#                 if (sd[0] == tyr) and (sd[1] == tmo) and (sd[2] == tda):
#                     last=d
#                     foundlast=1
#                     break

#             if not foundlast: last=data[-1]
#         else:
#             last=data[-1]

#         shead=head.split(' ')
#         slast=last.split(' ')
#         ilat=shead.index('Lat')
#         ilon=shead.index('Lon')
#         iyr=shead.index('Year')
#         imo=shead.index('Month')
#         ida=shead.index('Day')
#         if 'Ts' in shead: its=shead.index('Ts')
#         else: its=shead.index('T1')

#         binf=BM.BuoyMaster(c)

#         # latest location and date
#         clat=float(slast[ilat])
#         clon=float(slast[ilon])
#         ts=float(slast[its])
#         cyr=slast[iyr]
#         cmo=slast[imo]
#         cda=slast[ida]

#         if ts < -2.0:
#             tcol=ucols[0]
#             if ts == -999.0: tcol='dimgrey'
#         for i,t in enumerate(scale):
#             if ts >= t: tcol=ucols[i+1]

#         blab=binf['name'][0]+'-'+binf['name'][1]+' ('+cmo+'/'+cda+'/'+cyr+')'
#         xx,yy=PF.LLtoXY([clat],[clon],0.0)
#         plt.plot(xx,yy,'ok',ms=10)
#         plt.plot(xx,yy,'o',color=tcol,ms=8)
#         plt.text(xx,yy,blab,fontsize=12,color='k',fontweight='bold')

#     outlabs=['Alaska','Russia','Greenland','85N','80N','75N','90E','135E','180E','135W','90W']
#     rot1=-20.0
#     suby=100.
#     llcol='dimgrey'
#     outpos=[[-1400,2250,0,'w'],[1300.,2250,0,'w'],[-1180,-900,0,'w'],
#             [110,550.-suby,rot1,llcol],[280,1070-suby,rot1,llcol],[560-suby,1590-suby,rot1,llcol],
#             [700,10,0,llcol],[480,550,45,llcol],[-80,700,90,llcol],[-650,450,-45,llcol],[-900,10,0,llcol]]
#     for i,o in enumerate(outlabs):
#         if i <= 2: fs=14
#         else: fs=11
#         plt.text(outpos[i][0],outpos[i][1],outlabs[i],rotation=outpos[i][2],color=outpos[i][3],fontsize=fs)

#     strcol="%.2d/%.2d/%d" % (int(tmo),int(tda),int(tyr))
#     strtit="%d%.2d%.2d" % (int(tyr),int(tmo),int(tda))
#     plt.title('UpTempO Buoy Positions '+strcol,fontsize=20)
#     if regen == 'none': plt.savefig('UPTEMPO/WebPlots/CurrentPositionsMap.png',bbox_inches='tight')
#     plt.savefig('UPTEMPO/WebPlots/PositionsMap.'+strtit+'.png',bbox_inches='tight')

#     outwrite='UPTEMPO/WebPlots/PositionsMap.'+strtit+'.png PositionMaps/PositionsMap.'+strtit+'.png'
#     transferList(outwrite)

def OverviewMap(strdate=None):

    if strdate == None:
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    buoysdate = objdate
    ax = aplots.UpTempOArcticMap()
    shapes = {2019:'o', 2020:'s',2021:'d',2022:'.'}
    # plot latest locations of each buoy we are currently following
    curbuoys,deadbuoys,orderbuoys,deadbuoys=BM.getBuoys()
    for ii,c in enumerate(curbuoys):
        binf=BM.BuoyMaster(c)
        df = pd.read_csv(f'UPTEMPO/Processed_Data/{c}.csv')
        if ((df['Year']==buoysdate.year) & (df['Month']==buoysdate.month) & (df['Day']==buoysdate.day)).any():
            clat = df['Lat'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month)].iloc[-1]  #  & (df['Day']==buoysdate.day)
            clon = df['Lon'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month)].iloc[-1]  #  & (df['Day']==buoysdate.day)
            blab=f"#{binf['name'][1]}" #{buoysdate.strftime(strformat)}"
        # else:
        #     clon = df['Lon'].iloc[-1]
        #     clat = df['Lat'].iloc[-1]
        #     # blab=f"{binf['name'][0]}-{binf['name'][1]}{newline}{df['Month'].iloc[-1]}/{df['Day'].iloc[-1]}/{df['Year'].iloc[-1]-2000}"
        #     blab=f"{binf['name'][0]}-{binf['name'][1]} {df['Month'].iloc[-1]}/{df['Day'].iloc[-1]}/{df['Year'].iloc[-1]-2000}"

            ax.plot(clon,clat,marker=shapes[df['Year'].iloc[0]],color='k',ms=10,
                    transform=ccrs.PlateCarree())
            ax.text(clon-(2*np.cos(clat)*np.pi/180),clat-0.5,blab,fontsize=12, color='k', fontweight='bold',transform=ccrs.PlateCarree())
        # print(clat)
        # print(c)
        # print(cyr,cmo,cda)
        # ax.plot(clon,clat,'ok',ms=10,transform=ccrs.PlateCarree())
        # blab=f"{binf['name'][0]}-{binf['name'][1]} {cmo}/{cda}/{cyr}"
        # ax.text(clon,clat,blab,fontsize=12, color='k', fontweight='bold',transform=ccrs.PlateCarree())
        #     ax.plot(clon,clat,marker=shapes[df['Year'].iloc[0]],color='k',ms=10,
        #             transform=ccrs.PlateCarree())
        #     ax.text(clon-(2*np.cos(clat)*np.pi/180),clat-0.5,blab,fontsize=12, color='k', fontweight='bold',transform=ccrs.PlateCarree())

    for key in shapes.keys():
        ax.scatter(0,0,10,marker=shapes[key],color='k',transform=ccrs.PlateCarree(),label=key)
    ax.legend(markerscale=2.5,fontsize=10) #,title='UpTempO')

    plt.savefig('UPTEMPO/WebPlots/CurrentPositionsMap.png',bbox_inches='tight')
    plt.savefig('UPTEMPO/WebPlots/PositionsMap.'+strdate+'.png',bbox_inches='tight')

    outwrite='UPTEMPO/WebPlots/PositionsMap.'+strdate+'.png PositionMaps/PositionsMap.'+strdate+'.png'
    transferList(outwrite)

def PrevOverviewMap(strdate=None):

    if strdate == None:
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    # objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    buoysdate = objdate # + dt.timedelta(days=1)
    print('buoys date',buoysdate)

    ax = aplots.UpTempOArcticMap(strdate)
    shapes = {2019:'o', 2020:'s',2021:'d',2022:'.'}
    print('line 649 in plots')
    # newline = '\n'
    # get last locations of each buoy we are currently following on buoysdate
    curbuoys,deadbuoys,orderbuoys,deadbuoys=BM.getBuoys()
    for ii,c in enumerate(curbuoys):
        binf=BM.BuoyMaster(c)
        df = pd.read_csv(f'UPTEMPO/Processed_Data/{c}.csv')
        if ((df['Year']==buoysdate.year) & (df['Month']==buoysdate.month) & (df['Day']==buoysdate.day)).any():
            clat = df['Lat'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month)].iloc[-1]  #  & (df['Day']==buoysdate.day)
            clon = df['Lon'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month)].iloc[-1]  #  & (df['Day']==buoysdate.day)
            # some longitudes are wacky. Don't consider them in the day's mean, actually taking last is better
            # dayLon = df['Lon'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month) & (df['Day']==buoysdate.day)]
            # goodLon = np.abs(stats.zscore(dayLon))< 3
            # clon = dayLon[goodLon].mean()
            # clon = df['Lon'][(df['Year']==buoysdate.year) & (df['Month']==buoysdate.month) & (df['Day']==buoysdate.day)].mean()
            # blab=f"{binf['name'][0]}-{binf['name'][1]}{newline}{buoysdate.strftime(strformat)}"
            blab=f"#{binf['name'][1]}" #{buoysdate.strftime(strformat)}"
        # else:
        #     clon = df['Lon'].iloc[-1]
        #     clat = df['Lat'].iloc[-1]
        #     # blab=f"{binf['name'][0]}-{binf['name'][1]}{newline}{df['Month'].iloc[-1]}/{df['Day'].iloc[-1]}/{df['Year'].iloc[-1]-2000}"
        #     blab=f"{binf['name'][0]}-{binf['name'][1]} {df['Month'].iloc[-1]}/{df['Day'].iloc[-1]}/{df['Year'].iloc[-1]-2000}"

            ax.plot(clon,clat,marker=shapes[df['Year'].iloc[0]],color='k',ms=10,
                    transform=ccrs.PlateCarree())
            ax.text(clon-(2*np.cos(clat)*np.pi/180),clat-0.5,blab,fontsize=12, color='k', fontweight='bold',transform=ccrs.PlateCarree())

    for key in shapes.keys():
        ax.scatter(0,0,10,marker=shapes[key],color='k',transform=ccrs.PlateCarree(),label=key)
    ax.legend(markerscale=2.5,fontsize=10) #,title='UpTempO')

    plt.savefig('UPTEMPO/WebPlots/CurrentPositionsMap.png',bbox_inches='tight')
    plt.savefig('UPTEMPO/WebPlots/PositionsMap.'+strdate+'.png',bbox_inches='tight')

    outwrite='UPTEMPO/WebPlots/PositionsMap.'+strdate+'.png PositionMaps/PositionsMap.'+strdate+'.png'
    print(outwrite)
    transferList(outwrite)

    plt.show()

def PrevOverviewMapSouth(strdate=None,defaultPlot=False):
    if strdate == None:
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    print('in overview',defaultPlot)

    ax = aplots.UpTempOAntarcticMap(strdate,defaultPlot=defaultPlot)

    shapes = {2019:'o', 2020:'s',2021:'d'}
    ###### add latest buoy locs here, when we have buoys deployed there.

    if defaultPlot is False:
        plt.savefig('UPTEMPO/WebPlots/CurrentSouthPositionsMap.png',bbox_inches='tight')
        plt.savefig('UPTEMPO/WebPlots/SouthPositionsMap'+strdate+'.png',bbox_inches='tight')

        outwrite='UPTEMPO/WebPlots/SouthPositionsMap'+strdate+'.png PositionMapsS/SouthPositionsMap'+strdate+'.png'
        print(outwrite)
        transferList(outwrite)
    else:
        plt.savefig('UPTEMPO/WebPlots/CurrentSouthPositionsMap_default.png',bbox_inches='tight')
        outwrite='UPTEMPO/WebPlots/CurrentSouthPositionsMap_default.png PositionMapsS/CurrentSouthPositionsMap_default.png'
        print(outwrite)
        transferList(outwrite)

    plt.show()

    return ax

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


def Plot_UpTempO():

    curbuoys,deadbuoys,orderbuoys=BM.getBuoys()
    for c in curbuoys:
        TimeSeriesPlots(c)
        TimeSeriesPlots(c,quan='Pressure')
        VelocitySeries(c)
        # exit(-1)
