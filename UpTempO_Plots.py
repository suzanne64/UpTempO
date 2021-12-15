#!/usr/bin/python
import os
import sys
import time
import datetime
import BuoyTools_py3_toot as BT
import PlottingFuncs as PF
import numpy as np
import UpTempO_BuoyMaster as BM
import UpTempO_Python as upp
import IABPplots as iplots
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY,DateFormatter,rrulewrapper,RRuleLocator,drange)



def TimeSeriesPlots(bid,quan='Temp'):
    print('plotting Time Series for '+bid)
    #quan = 'Temp' or 'Pressure'
    
    # cols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    cols=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    
    binf=BM.BuoyMaster(bid)
    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    opf=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    header=opf.readline()
    opf.close()
    header=header.split(' ')
    
    data=np.loadtxt('UPTEMPO/Processed_Data/'+bid+'.dat',skiprows=1)

    #Time Series Plots for:
    #Ocean Pressure and SLP
    #Temperature

    years=[int(y) for y in data[:,0]]
    months=[int(m) for m in data[:,1]]
    days=[int(d) for d in data[:,2]]
    hours=[int(h) for h in data[:,3]]
    n=len(days)

    dateobjs=[datetime.datetime(years[i],months[i],days[i],hours[i]) for i in range(n)]

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
        depths=binf['tdepths']
        ind1=header.index('T1')
        yaxlab='Temperature (C)'
        if bid == '300234061160500': ax.set_ylim(-2.0,2.0)
        else: ax.set_ylim(-2.0,10.0)

    if quan == 'Salinity':
        depths=binf['sdepths']
        ind1=header.index('S1')
        yaxlab='Salinity'
        # if bid == '300234061160500': ax.set_ylim(-2.0,2.0)
        # else: ax.set_ylim(-2.0,10.0)

    havepressures=1
    havebp=1
    if quan == 'Pressure':
        if 'pdepths' in binf:
            depths=binf['pdepths']
            ind1=header.index('P1')
        else:
            if 'ddepths' in binf:
                depths=binf['ddepths']
                ind1=header.index('D2')
            else:
                havepressures=0
                
        if 'BP' in header:    
            islp=header.index('BP')
        else:
            havebp=0

        if havepressures:
            yaxlab='Ocean Pressure (dB)'
            maxdep=np.max(depths)
            ax.set_ylim(maxdep+10.,0)

    if havepressures:  
        nt=len(depths)
        vals=data[:,ind1:ind1+nt]
        
        if quan == 'Pressure':
            secax=ax.twinx()
            secax.spines['right'].set_color('red')
            secax.set_ylim(940.0,1080)
            secax.set_ylabel('Sea Level Pressure',color='r')
            slp=data[:,islp]
            slp[slp <= 940] =np.nan
            secax.xaxis.set_major_formatter(formatter)
            secax.plot_date(dateobjs,data[:,islp],color='r',alpha=0.5)

        for t in range(nt):
            cvals=vals[:,t]
            ax.plot_date(dateobjs,cvals,'-o',color=cols[t],ms=1)


    datelab=" %.2d/%.2d/%d to %.2d/%.2d/%d" % (dateobjs[0].month,dateobjs[0].day,dateobjs[0].year,dateobjs[-1].month,dateobjs[-1].day,dateobjs[-1].year)
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
    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    opf=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    header=opf.readline()
    opf.close()
    header=header.split(' ')
    
    data=np.loadtxt('UPTEMPO/Processed_Data/'+bid+'.dat',skiprows=1)

 
    years=[int(y) for y in data[:,0]]
    months=[int(m) for m in data[:,1]]
    days=[int(d) for d in data[:,2]]
    hours=[int(h) for h in data[:,3]]
    n=len(days)
    dateobjs=[datetime.datetime(years[i],months[i],days[i],hours[i]) for i in range(n)]
    # daily dates for distance plot
    s = np.unique([d.date() for d in dateobjs])

    # datetime vector for plotting velocity and distance
    dateobjsBTN = [dateobjs[i]+(dateobjs[i+1]-dateobjs[i])/2 for i in range(n-1)]

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

    #convert date to doy
    doys=[]
    dyears=[]
    lats=[]
    lons=[]
    uyears=[]
    for d in range(len(data)):
        cdoy=BT.dateToDOY(year=data[d,0],month=data[d,1],day=data[d,2],hour=data[d,3])
        doys.append(float(cdoy))
        dyears.append(data[d,0])
        lats.append(data[d,4])
        lons.append(data[d,5])
        if data[d,0] not in uyears: uyears.append(data[d,0])


    if len(uyears) > 1:
        addinf={}
        for y in range(len(uyears)-1):
            if BT.isLeap(uyears[y]): addinf[uyears[y+1]]=366.
            else: addinf[uyears[y+1]]=365.

        addinf[uyears[0]]=0

        dyears=np.asarray(dyears)
        doys=np.asarray(doys)
        for uy in uyears:
            w=dyears == uy
            doys[w]=doys[w]+addinf[uy]

    velocity=[]
    dkmt=[]
    dobj=[];
    for i in range(len(doys)-1):
        startdoy=doys[i]
        enddoy=doys[i+1]
        startlat=lats[i]
        endlat=lats[i+1]
        startlon=lons[i]
        endlon=lons[i+1]

        deltat=(enddoy-startdoy)*24.*60.*60.  #seconds

        distkm=PF.dist_ll([startlat],[startlon],[endlat],[endlon])
        distm=distkm*1000.
        dkmt.append([distm,deltat])

        if deltat != 0:
            vel=distm/deltat
        else: vel=0
        if vel != 0:
            # velocity.append([startdoy,vel])
            velocity.append([dateobjsBTN[i],vel])
    nvel=np.asarray(velocity)
    plt.plot_date(nvel[:,0],nvel[:,1],'-ok',ms=3)

    #-- daily distance --
    intdoys=[int(d) for d in doys]
    udoys=[]
    for i in intdoys:
        if i not in udoys: udoys.append(i)        

    intdoys=np.asarray(intdoys)
    lats=np.asarray(lats)
    lons=np.asarray(lons)
    sto=[]

    # if bid=='300534060051570':
    #     exit(-1)
    for ii,ud in enumerate(udoys):
        wud=intdoys == ud
        if np.sum(wud) > 15:
            cll=[ud,lats[wud][0],lats[wud][-1],lons[wud][0],lons[wud][1],s[ii]]
            sto.append(cll)

    nsto=np.asarray(sto)
    startlats=nsto[:,1]
    endlats=nsto[:,2]
    startlons=nsto[:,3]
    endlons=nsto[:,4]
    dists=PF.dist_ll(startlats,startlons,endlats,endlons)
    doys=nsto[:,0]

    secax=ax.twinx()
    secax.spines['right'].set_color('red')
    secax.set_ylim(-20,40)
    secax.set_ylabel('Daily Distance (km)',color='r')
    secax.xaxis.set_major_formatter(formatter)
    secax.plot_date(nsto[:,-1],dists,'-or',alpha=0.5,ms=3)
    # 
    datelab=" %.2d/%.2d/%d to %.2d/%.2d/%d" % (dateobjs[0].month,dateobjs[0].day,dateobjs[0].year,dateobjs[-1].month,dateobjs[-1].day,dateobjs[-1].year)

    plt.title(buoylab+' ('+bid+') Velocity and Daily Distance'+datelab,fontsize=20)
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
    buoylab='UpTempO '+binf['name'][0]+' #'+binf['name'][1]
    abbv=binf['imeiabbv']

    opf=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    header=opf.readline()
    opf.close()
    header=header.split(' ')
    
    data=np.loadtxt('UPTEMPO/Processed_Data/'+bid+'.dat',skiprows=1)

 
    years=[int(y) for y in data[:,0]]
    months=[int(m) for m in data[:,1]]
    days=[int(d) for d in data[:,2]]
    hours=[int(h) for h in data[:,3]]
    n=len(days)
    dateobjs=[datetime.datetime(years[i],months[i],days[i],hours[i]) for i in range(n)]


    rule=rrulewrapper(MONTHLY,interval=1)
    loc=RRuleLocator(rule)
    formatter=DateFormatter('%m/%d/%y')
    

    plt.rcParams['figure.figsize']=(20,8)
    plt.rcParams['font.size']=18
    
    fig,ax1=plt.subplots()
    ax1.xaxis.set_major_locator(loc)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.xaxis.set_tick_params(rotation=85,labelsize=14)
    
    #convert date to doy
    doys=[]
    dyears=[]
    batt=[]
    subm=[]
    uyears=[]
    for d in range(len(data)):
        cdoy=BT.dateToDOY(year=data[d,0],month=data[d,1],day=data[d,2],hour=data[d,3])
        doys.append(float(cdoy))
        dyears.append(data[d,0])
        batt.append(data[d,-2])
        subm.append(data[d,-1])
        if data[d,0] not in uyears: uyears.append(data[d,0])

    if len(uyears) > 1:
        addinf={}
        for y in range(len(uyears)-1):
            if BT.isLeap(uyears[y]): addinf[uyears[y+1]]=366.
            else: addinf[uyears[y+1]]=365.

        addinf[uyears[0]]=0

        dyears=np.asarray(dyears)
        doys=np.asarray(doys)
        for uy in uyears:
            w=dyears == uy
            doys[w]=doys[w]+addinf[uy]

    ax1.plot_date(dateobjs,np.asarray(subm)*100,'k.-',ms=3)
    ax1.set_ylabel('Submergence Percent', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_ylim(-5,105)
    
    datelab=" %.2d/%.2d/%d to %.2d/%.2d/%d" % (dateobjs[0].month,dateobjs[0].day,dateobjs[0].year,dateobjs[-1].month,dateobjs[-1].day,dateobjs[-1].year)
    plt.title(buoylab+' ('+bid+') '+'Submergence Percent and Battery Voltage:'+datelab,fontsize=20)
    
    ax2 = ax1.twinx()
    ax2.xaxis.set_major_locator(loc)
    ax2.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_tick_params(rotation=85,labelsize=14)
    ax2.plot_date(dateobjs,np.asarray(batt),'r.-',ms=3)
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
    
    ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    plt=iplots.blankBathMap(cdomain='UpTempO')
    plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])

    
    opf=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    header=opf.readline()
    opf.close()
    header=header.split(' ')
    ilat=header.index('Lat')
    ilon=header.index('Lon')
    imo=header.index('Month')
    
    data=np.loadtxt('UPTEMPO/Processed_Data/'+bid+'.dat',skiprows=1)
    for m in range(12):
        cm=m+1
        cdat=data[data[:,imo] == cm,:]
        xar,yar=PF.LLtoXY(cdat[:,ilat],cdat[:,ilon],0.0)
        plt.plot(xar,yar,'o',ms=1.5,color='k')
        plt.plot(xar,yar,'o',ms=1,color=ucols[m])

    binf=BM.BuoyMaster(bid)
    startdate="%.2d/%.2d/%d" % (data[0,1],data[0,2],data[0,0])
    enddate="%.2d/%.2d/%d" % (data[-1,1],data[-1,2],data[-1,0])
    titout='UpTempO '+binf['name'][0]+' #'+binf['name'][1]+'('+bid+')  '+startdate+' to '+enddate

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
    outwrite='UPTEMPO/WebPlots/TrackByMonth'+abbv+'.png WebPlots/TrackByMonth'+abbv+'.png'
    transferList(outwrite)        

def OverviewMap(regen='none'):
    
    ucols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
    scale=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]


    if regen != 'none':
        plt=iplots.blankSSTMap(cdomain='UpTempO',udomain=[-2000,2000,-2500,2500],rot=0,fsize=(8.3,10),strdate=regen)
        tyr=regen[0:4]
        tmo=regen[4:6]
        tda=regen[6:]
    else:
        today=datetime.datetime.now()
        tyr=today.year
        tmo=today.month
        tda=today.day

        plt=iplots.blankSSTMap(cdomain='UpTempO',udomain=[-2000,2000,-2500,2500],rot=0,fsize=(8.3,10))

    plt=PF.laloLines(plt,0,lats=[50.,60.,70.,75.,80.,85.])
    
    
    curbuoys,deadbuoys,orderbuoys,deadbuoys=BM.getBuoys()
    for c in curbuoys:
        opf=open('UPTEMPO/Processed_Data/'+c+'.dat','r')
        data=opf.read()
        opf.close()
        data=data.split('\n')
        data=[da for da in data if da]
        head=data[0]

        if regen != 'none':
            foundlast=0
            for d in data:
                sd=d.split(' ')
                if (sd[0] == tyr) and (sd[1] == tmo) and (sd[2] == tda):
                    last=d
                    foundlast=1
                    break

            if not foundlast: last=data[-1]
        else:
            last=data[-1]

        shead=head.split(' ')
        slast=last.split(' ')
        ilat=shead.index('Lat')
        ilon=shead.index('Lon')
        iyr=shead.index('Year')
        imo=shead.index('Month')
        ida=shead.index('Day')
        if 'Ts' in shead: its=shead.index('Ts')
        else: its=shead.index('T1')
        
        binf=BM.BuoyMaster(c)

        clat=float(slast[ilat])
        clon=float(slast[ilon])
        ts=float(slast[its])
        cyr=slast[iyr]
        cmo=slast[imo]
        cda=slast[ida]

        if ts < -2.0:
            tcol=ucols[0]
            if ts == -999.0: tcol='dimgrey'
        for i,t in enumerate(scale):
            if ts >= t: tcol=ucols[i+1]

        blab=binf['name'][0]+'-'+binf['name'][1]+' ('+cmo+'/'+cda+'/'+cyr+')'
        xx,yy=PF.LLtoXY([clat],[clon],0.0)
        plt.plot(xx,yy,'ok',ms=10)
        plt.plot(xx,yy,'o',color=tcol,ms=8)
        plt.text(xx,yy,blab,fontsize=12,color='k',fontweight='bold')

    outlabs=['Alaska','Russia','Greenland','85N','80N','75N','90E','135E','180E','135W','90W']
    rot1=-20.0
    suby=100.
    llcol='dimgrey'
    outpos=[[-1400,2250,0,'w'],[1300.,2250,0,'w'],[-1180,-900,0,'w'],
            [110,550.-suby,rot1,llcol],[280,1070-suby,rot1,llcol],[560-suby,1590-suby,rot1,llcol],
            [700,10,0,llcol],[480,550,45,llcol],[-80,700,90,llcol],[-650,450,-45,llcol],[-900,10,0,llcol]]
    for i,o in enumerate(outlabs):
        if i <= 2: fs=14
        else: fs=11
        plt.text(outpos[i][0],outpos[i][1],outlabs[i],rotation=outpos[i][2],color=outpos[i][3],fontsize=fs)

    strcol="%.2d/%.2d/%d" % (int(tmo),int(tda),int(tyr))
    strtit="%d%.2d%.2d" % (int(tyr),int(tmo),int(tda))
    plt.title('UpTempO Buoy Positions '+strcol,fontsize=20)
    if regen == 'none': plt.savefig('UPTEMPO/WebPlots/CurrentPositionsMap.png',bbox_inches='tight')
    plt.savefig('UPTEMPO/WebPlots/PositionsMap.'+strtit+'.png',bbox_inches='tight')
    
               
    
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
        # VelocitySeries(c)
        exit(-1)
