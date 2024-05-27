#!/usr/bin/python
import datetime as dt
import sys, os
import BuoyTools_py3_toot as BT
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import GFunctions as gf
import PlottingFuncs as PF
import cmocean
#import Special_Projects_py3 as SP
#import Utilities_py3 as ut
import ProcessFields as pfields
#import timedelta
# from matplotlib.dates import (YEARLY,MONTHLY,WEEKLY,DAILY,DateFormatter,rrulewrapper,RRuleLocator,drange)
import cartopy.crs as ccrs
import cartopy.feature

##subdomains=[[domain],[-3585.,0.,0.,4200],[0.,3100.,0.,4200.],[-3585.,0.,-3500.,0.],[0.,3100.,-3500.,0.0],[-1792.,1792.,-2100.,2100]]
##domlab=['','UL','UR','LL','LR','C']

def fieldCoords(field='ice',reg='north'):

    fieldpath='Satellite_Fields/'
    if field == 'ice':
        if not os.path.exists(fieldpath+'NSIDC_ICE/'+reg+'/xx.txt'):
            pfields.getNSIDCice()
        xx=np.loadtxt(fieldpath+'NSIDC_ICE/'+reg+'/xx.txt')
        yy=np.loadtxt(fieldpath+'NSIDC_ICE/'+reg+'/yy.txt')

    if field == 'slp':
        if not os.path.exists(fieldpath+'SLP/SLP_XX.dat'):
            pfields.getNCEPslp()
        xx=np.loadtxt(fieldpath+'SLP/SLP_XX.dat')
        yy=np.loadtxt(fieldpath+'SLP/SLP_YY.dat')

    if field == 'ta':
        opll=open('Satellite_Fields/TA_latlon.txt','r')
        ll=opll.read()
        opll.close()
        lat,lon=ll.split('\n')[0:-1]
        lat=lat.split(';')
        lon=lon.split(';')
        lat=[float(l) for l in lat]
        lon=[float(l) for l in lon]
        nlat=np.asarray(lat)
        nlon=np.asarray(lon)

        xx=np.zeros((21,144))
        yy=np.zeros((21,144))
        for i,la in enumerate(lat):
            lla=[la for r in range(144)]
            xar,yar=PF.LLtoXY(lla,lon,0.0)
            xx[i,:]=xar
        for i,lo in enumerate(lon):
            llo=[lo for r in range(21)]
            xar,yar=PF.LLtoXY(lat,llo,0.0)
            yy[:,i]=yar
         
    return xx,yy

def rotField(xx,yy,rot):
    sh=np.shape(xx)
    nrows=sh[0]
    ncols=sh[1]
    xx=np.reshape(xx,nrows*ncols)
    yy=np.reshape(yy,nrows*ncols)
    la,lo=PF.XYtoLL(xx,yy,0.0)
    xx,yy=PF.LLtoXY(la,lo,rot)
    xx=np.reshape(xx,sh)
    yy=np.reshape(yy,sh)
    return xx,yy

def getDomain(d):
    doms={'Overview':[-3800,2880,-3900,3800],
        #'Overview':[-4180,2500,-3900,3800],
        #'Overview':[-3585,3100,-3500,4200],
          'UL':[-3585.,0.,0.,4200],
          'UR':[0.,3100.,0.,4200.],
          'LL':[-3585.,0.,-3500.,0.],
          'LR':[0.,3100.,-3500.,0.0],
          'C':[-1792.,1792.,-2100.,2100],
          'Beaufort Gyre':[-2495.,-92,-1730.,1060.],
          'GIN Sea':[0.0,3100.,-3500.,0.0],
          'Central Arctic':[-2500.,1200.,-1700.,2250.],
          'SIDFEx':[-2600,2000,-3500,2000],
          'AXIBS_2021':[-3585,3100,-3500,4200],
          'ARCX_2021':[-3585,3100,-3500,4200],
          'Sea_Cadets_2021':[-3585,3100,-3500,4200],
          'ICEPPR_2021':[-3585,3100,-3500,4200],
          'ADA_2021':[-3585,3100,-3500,4200],
          'Utqiagvik_2021':[-2200,-1800,200,680],
          'Bering Sea':[-4200.,-1000,-1000,3500],
          'FYB_2020':[-2250,2500,-4200,1000],
          'Utqiagvik_2021':[-2100.,-1500,170,800.],
          #'ICE-PPR_DiskoBay_2021':[-300,300,-2600,-2000],
          'ICE-PPR_DiskoBay_2021':[-100,210,-2400,-2100],
          #'ICE-PPR_DiskoBay_2021z':[40,140,-2220,-2160],
          'ICE-PPR_DiskoBay_2021z':[20,100,-2220,-2130],
          #'ICE-PPR_DiskoBay_2021z':[-60,120,-2200,-2160],
          #'ICE-PPR_DiskoBay_2021z':[130,180,-2280,-2230],
          'UpTempO':[-2500.,2500.,0,2500.]}

    zdoms=zoomDoms()
    for z in zdoms:
        for i,cdom in enumerate(zdoms[z]):
            si="%d" % (i+1)
            doms[z+'z'+si]=cdom

    return doms[d]

def zoomDoms():

    zdoms={'FYB_2020':[[-1700,-800,-400,200],[-300,300,380,850],[-200,1000,-4200,-3000]]}

    return zdoms

def serverCode(domain,quan):

    domcode={'Beaufort_Gyre':'BG',
             'Beaufort Gyre':'BG',
             'Central_Arctic':'C',
             'Central Arctic':'C',
             'Overview':'O',
             'GIN_Sea':'GS',
             'GIN Sea':'GS',
             'Bering_Sea':'BS',
             'Bering Sea':'BS'}

    quancode={'slp':'BP',
              'ts':'SST',
              'ta':'TA',
              'vel':'VEL',
              'tracks':'TRACK'}

    out=domcode[domain]+quancode[quan]
    return out


# def blankIceMap(cdomain='Overview',udomain=[],strdate='current',fsize=(8.85,10),rot=55.0,icelevels=[0.0,0.15,0.30,0.45,0.60,0.75,0.90,1.0]):
#     #strdate='yyyymmdd'
    
#     if cdomain == 'UpTempO':
#         ucolors=['0.4','0.5','0.7','0.75','0.8','1.0']
#         icelevels=[0.15,0.2,0.3,0.4,0.5,0.75,1.0]
#         fsize=(10,5)
#         rot=0

#     if not udomain:
#         udomain=getDomain(cdomain)
#     if strdate=='current':
#         dates=BT.getDates()
#         stryest=dates[0].replace('-','')
#     else: stryest=strdate

#     plt=PF.ArcticMap(domain=udomain,fsize=fsize,rot=rot)

#     #----plot ice----
#     ucmap=cmocean.cm.ice
#     if cdomain == 'UpTempO': ucmap.set_over('white')
#     else: ucmap.set_over('azure')

#     icexx,iceyy=fieldCoords(field='ice')
#     icexx,iceyy=rotField(icexx,iceyy,rot)
#     icedata=np.loadtxt('Satellite_Fields/NSIDC_ICE/north/'+stryest+'.txt')
#     if cdomain == 'UpTempO':
#         icec=plt.contourf(icexx,iceyy,icedata,icelevels,colors=ucolors,vmax=.9)
#     else:
#         icec=plt.contourf(icexx,iceyy,icedata,icelevels,vmin=0.15,cmap=ucmap)

#     return plt

def ICEMap(cdomain='Overview',udomain=[],strdate='current',fsize=(8.85,10),rot=55.0,icelevels=[0.0,0.15,0.30,0.45,0.60,0.75,0.90,1.0]):
    #strdate='yyyymmdd'
    
    if cdomain == 'UpTempO':
        ucolors=['0.4','0.5','0.7','0.75','0.8','1.0']
        icelevels=[0.15,0.2,0.3,0.4,0.5,0.75,1.0]
        fsize=(10,5)
        rot=0

    if not udomain:
        udomain=getDomain(cdomain)
    if strdate=='current':
        dates=BT.getDates()
        stryest=dates[0].replace('-','')
    else: stryest=strdate

    # plt=PF.ArcticMap(domain=udomain,fsize=fsize,rot=rot)

    # #----plot ice----
    # ucmap=cmocean.cm.ice
    # if cdomain == 'UpTempO': ucmap.set_over('white')
    # else: ucmap.set_over('azure')

    # icexx,iceyy=fieldCoords(field='ice')
    # icexx,iceyy=rotField(icexx,iceyy,rot)
    # icedata=np.loadtxt('Satellite_Fields/NSIDC_ICE/north/'+stryest+'.txt')
    # if cdomain == 'UpTempO':
    #     icec=plt.contourf(icexx,iceyy,icedata,icelevels,colors=ucolors,vmax=.9)
    # else:
    #     icec=plt.contourf(icexx,iceyy,icedata,icelevels,vmin=0.15,cmap=ucmap)

    # return plt

def blankBathMap(cdomain='Overview',udomain=[],fsize=(8.85,10),rot=55.0):

    if cdomain == 'UpTempO':
        fsize=(10,5)
        rot=0
        
    if not udomain:
        udomain=getDomain(cdomain)

    pltt=PF.ArcticMap(domain=udomain,fsize=fsize,rot=rot)

    bscalegray=[50.,100.,500.,1000.,2000.,3000.]
    bscaleblack=[28.,60.]
    deepfillcol='beige' 
    # bath=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATH-1041x1094.dat')
    # bxx=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATHXX-1041x1094.dat')
    # byy=np.loadtxt('/Users/suzanne/Google Drive/UpTempO/Bathymetry_Files/6.BATHYY-1041x1094.dat')
    # Using GEBCO 2023 to extend domaing southward, May 2024
    ds = xr.open_dataset('/Users/suzanne/Google Drive/UpTempO/bathymetry/GEBCO_2023_arctic.nc')
    elat = ds['elat'].values
    elon = ds['elon'].values
    elev = ds['elev'].values
    print(elat.shape,elon.shape,elev.shape)
    pltt.show()
    pltt.contour(elon,elat,-elev,bscalegray,colors='gray',linewidths=.5,transform=ccrs.PlateCarree())

    if rot:
        print('line 230 of IABPlots, needs work!!!')
        # sqbxx=np.zeros((1094,1041))
        # sqbyy=np.zeros((1094,1041))
        # for r in range(1094): sqbxx[r,:]=bxx
        # for r in range(1041): sqbyy[:,r]=byy
        # fbxx=sqbxx.flatten()
        # fbyy=sqbyy.flatten()
        # lat,lon=PF.XYtoLL(fbxx,fbyy,0.0)
        # bxx,byy=PF.LLtoXY(lat,lon,rot)
        # bxx=np.reshape(bxx,(1094,1041))
        # byy=np.reshape(byy,(1094,1041))
        
    # bathc=pltt.contour(bxx,byy,-bath,bscalegray,colors='gray',linewidths=.5)
    # if cdomain == 'UpTempO': pltt.contour(bxx,byy,-bath,bscaleblack,colors='black',linewidths=1)
    # pltt.contourf(bxx,byy,-bath,[3000.,9000.],colors=deepfillcol)
    bathc=pltt.contour(elon,elat,-elev,bscalegray,colors='gray',linewidths=.5,transform=ccrs.PlateCarree())
    if cdomain == 'UpTempO': 
        pltt.contour(elon,elat,-elev,bscaleblack,colors='black',linewidths=1,transform=ccrs.PlateCarree())
    pltt.contourf(elon,elat,-elev,[3000.,9000.],colors=deepfillcol,transform=ccrs.PlateCarree())
    pltt.axis('off')
    
    return pltt

# def blankSSTMap(cdomain='Overview',strdate='current',udomain=[],fsize=(8.85,10),rot=55.0,pice=1):
    
#     # if cdomain == 'UpTempO':
#     #     fsize=(10,5)
#     #     rot=0

#     if not udomain:
#         udomain=getDomain(cdomain)

#     if strdate=='current':
#         dates=BT.getDates()
#         stryest=dates[0].replace('-','')
#     else: stryest=strdate
#     year=stryest[0:4]


#     featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
#     #featbar=[-30.0,-20.,-10.,-5.,-1.,0,1,5.,10.,20.,30.]
#     if cdomain=='UpTempO': featbar=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]
#     else: featbar=[-30.,-20.,-10.,-5.,-1.,0.0,1.0,5.0,10.,20.,30.]

#     if not os.path.isfile('/Volumes/GoogleDrive/My Drive/UpTempO/NOAA-Daily-SST/'+year+'/SST-'+stryest+'.dat'):
#         try:
#             if strdate=='current': pfields.processSST()
#             else: pfields.processSST(strdate=stryest)
#         except:            
#             stryest=BT.findYest(stryest)
#             print('Trying to find SST data for '+stryest)
#             if not os.path.isfile('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/MyData/SST-'+stryest+'.dat'):
#                 stryest=BT.findYest(stryest)
#                 print('Trying to find SST data for '+stryest)
#                 if not os.path.isfile('/Users/wendye/Drobox/RecentWarming/NOAA-Daily-SST/'+year+'/MyData/SST-'+stryest+'.dat'):
                    
#                     print('SST IS NOT UPDATING')
#                     print('NOT PLOTTING SST')

#                     plt=blankIceMap(cdomain=cdomain)
#                     return plt
                    
#     sst=np.loadtxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/MyData/SST-'+stryest+'.dat')
#     sstxx=np.loadtxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/SST-XX.dat')
#     sstyy=np.loadtxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/SST-YY.dat')
#     sstxx,sstyy=rotField(sstxx,sstyy,rot)

#     plt=PF.ArcticMap(domain=udomain,fsize=fsize,rot=rot)
#     plt.contourf(sstxx,sstyy,sst*100.,featbar,colors=featcolors,extend='both')
#     if pice:
#         icexx,iceyy = fieldCoords(field='ice')
#         icexx,iceyy = rotField(icexx,iceyy,rot)
#         icedata = np.loadtxt('Satellite_Fields/NSIDC_ICE/north'+stryest+'.txt')
#         icelevels = [0.15,0.30,0.45,0.60,0.75,0.90,1.0]
#         if cdomain == 'UpTempO':
#             ucolors=['0.4','0.5','0.7','0.75','0.8','1.0']
#             icelevels=[0.15,0.2,0.3,0.4,0.5,0.75,1.0]
#             icec=plt.contourf(icexx,iceyy,icedata,icelevels,colors=ucolors,vmax=.9)
#         else:
#             ucmap=cmocean.cm.ice
#             ucmap.set_over('azure')
#             icec=plt.contourf(icexx,iceyy,icedata,icelevels,vmax=.9,cmap=ucmap)
               
        
#     plt.axis('off')

#     return plt

def SSTMap(strdate='default',cdomain='Overview',udomain=[],pice=1,figsize=(8.85,10)):
    
##    if cdomain == 'UpTempO':
##        fsize=(10,5)
##        rot=0

    if not udomain:
        udomain=getDomain(cdomain)

    if strdate=='default':
        objdate = dt.datetime.now()
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    print(strdate)
    
    sstdate, sst, sstlon, sstlat = pfields.getSST(strdate)
    if pice:
        icedate, ice, icexx, iceyy = pfields.getICE(strdate,nors='n')
        
        
    featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    #featbar=[-30.0,-20.,-10.,-5.,-1.,0,1,5.,10.,20.,30.]
    if cdomain=='UpTempO':
        featbar=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]
        ucolors=['0.4','0.5','0.7','0.75','0.8','1.0']
        icelevels=[0.15,0.2,0.3,0.4,0.5,0.75,1.0]
        outlabs=['Alaska','Russia','Greenland','85N','80N','75N','90E','135E','180E','135W','90W']
    else:
        featbar=[-30.,-20.,-10.,-5.,-1.,0.0,1.0,5.0,10.,20.,30.]

                    
    print('line 243 IAP',sstdate, sst.shape, sstlon.shape, sstlat.shape)
    fig1, ax1 = plt.subplots(1,figsize=figsize)
    ax1 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
    gl = ax1.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45))
    kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
   
    if pice:
        # if not os.path.exists(f'/Volumes/GoogleDrive/My Drive/UpTempO/NSIDC_ICE/{year}/SST-{stryest}.dat'):
        try:
            icedate,ice,icexx,iceyy = pfields.getICE(strdate=strdate,nors='n')
            print(icedate,ice.shape)
        except:
            print('ICE IS NOT UPDATING')
            print('NOT PLOTTING ICE, want to plot older ice?')
                
        # icexx,iceyy=fieldCoords(field='ice')
        # icexx,iceyy=rotField(icexx,iceyy,rot)
        # icedata=np.loadtxt('Satellite_Fields/NSIDC_ICE/north/'+stryest+'.txt')
        icelevels=[0.15,0.30,0.45,0.60,0.75,0.90,1.0]
        if cdomain == 'UpTempO':
            ax1.add_feature(cartopy.feature.LAND)
            ax1.coastlines(resolution='110m',linewidth=0.5)
            ax1.set_extent([-180,180,70,90],crs=ccrs.PlateCarree())
            
            
            ax1.text(-45,79.5,'80N',transform=ccrs.PlateCarree(),fontsize=8)
            ax1.text(-45,69.5,'70N',transform=ccrs.PlateCarree(),fontsize=8)
            ch = ax1.imshow(ice, vmin=0, vmax=100, cmap=plt.cm.Blues,  #extent=extent, 
                       transform=ccrs.Stereographic(**kw))
            
            #ucmap.set_over('white')
        else:
            ucmap=cmocean.cm.ice
            ucmap.set_over('azure')
            icec=plt.contourf(icexx,iceyy,ice,icelevels,vmax=.9,cmap=ucmap)
        
    plt.axis('off')

    return plt
    
   
def blankTaMap(cdomain='Overview',strdate='current',udomain=[],fsize=(8.85,10),rot=55.0,pice=1):

    if pice:
        if '.' in strdate: ustrdate=strdate.split('.')[0]
        else: ustrdate=strdate
        plt=blankIceMap(cdomain=cdomain,strdate=ustrdate,udomain=udomain,fsize=fsize,rot=rot)
    else:
        if not udomain: udomain=getDomain(cdomain)
        plt=PF.ArcticMap(domain=udomain,fsize=fsize,rot=rot)


    if strdate == 'current':
        dateobj=BT.xDaysAgo(2)
        ustrdate="%d%.2d%.2d" % (dateobj[0].year,dateobj[0].month,dateobj[0].day)
        ustrdate+='.75'
    else:
        if '.' not in strdate: ustrdate+='.75'
        else: ustrdate=strdate

    featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    featbar=[-30.0,-20.,-10.,-5.,-1.,0,1,5.,10.,20.,30.]
    data=np.loadtxt('Satellite_Fields/NCEP_Ta/Ta_'+ustrdate+'.dat')
    xx,yy=fieldCoords(field='ta')
    xx,yy=rotField(xx,yy,rot)
    plt.contour(xx,yy,data,featbar,colors=featcolors)

    return plt
    
        

    
    
def projectMap(project='SIDFEx',tracks=0,rot=55.,strdate='current',showmap=0,showname=0,xterlab=0,latslons=[]):
    #This function creates a map from scratch with the appropriate domain defined in projectDomainID(project) and getDomain(d)
    #If strdate = 'current', ice from yesterday is plotted with the latest positions of the project buoys
    #If strdate = 'yyyymmdd', ice from yyyymmdd is plotted with the last project buoy positions on yyyymmdd
    #tracks = 0 means no track data will be plotted
    #tracks = x where x=days ago will plot tracks from x days ago to strdate
    mocols=['k','mediumpurple','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown',
            'darkorchid','plum','m','mediumvioletred','palevioletred','darkseagreen','goldenrod','chocolate','khaki']
    cdates=BT.getDates()

    dom=getDomain(project)
    addlab=''
    if project[-1] == 'z':
        project=project[0:-1]
        addlab='ZOOM'

    
    #plt=blankIceMap(cdomain=domid,strdate=strdate,rot=rot)

    ongoingps=SP.OngoingProjectNames()
    if project in ongoingps:
        uproj=project
        bids=SP.getOngoingProjectBids(project)
        if project == 'SIDFEx':
            cbids=bids[0]
            bids=[]
            for c in cbids: bids.append(cbids[c][0])
    else:
        
        if '2021' in project: projinf=SP.Projects_2021()
        if '2020' in project: projinf=SP.Projects_2020()

        cprojs=projinf['projects']
        if 'z' in project: uproj=project[0:-2]
        else: uproj=project
        bidinf=cprojs[uproj]
        bids=[]
        binf={}
        for bi in bidinf:
            bids.append(bidinf[bi][0])
            if xterlab: binf[bidinf[bi][0]]=[bidinf[bi][2],bidinf[bi][1]]

    opf=open('/Users/wendye/IABP_DATA_BU/Project_Tables/'+uproj+'.txt','r')
    tabdat=opf.read()
    opf.close()
    tabdat=tabdat.split('\n')[0:-1]
    if 'lat' in tabdat[0]:
        tabhead=tabdat[0]
        tabdat=tabdat[1:]
        shead=tabhead.split(',')
        ilat=shead.index('lat')
        ilon=shead.index('lon')
        idate=shead.index('LastDate')
        ibid=1
    else:
        if project == 'SIDFEx':
            ilat=6
            ilon=7
            idate=4
            ibid=2
        if project == 'McMurdo':
            ilat=3
            ilon=4
            idate=1
            ibid=0

    
    plt=blankIceMap(udomain=dom)
    if latslons:
        ulats=latslons[0]
        ulons=latslons[1]
        plt=PF.laloLines(plt,rot,lats=ulats,lons=ulons)

    xterlabs=[]
    ico=0
    usym='o'
    for td in tabdat:
        std=td.split(',')
        bid=std[ibid]
        name=std[0]
        cdate=std[idate]
        if cdate:
            clat=float(std[ilat])
            clon=float(std[ilon])
            cmo,cda,cyr=cdate.split('/')
            cdoy=BT.Date2Doy(cyr+'/'+cmo+'/'+cda+' 00:00:00',spliton='/')
            isup=BT.isUpdating(cdoy,cyr)

            cxx,cyy=PF.LLtoXY([clat],[clon],rot)

            if tracks:
                if os.path.isfile('GeneralFormat/'+bid+'.dat'):
                    yrdoyslist=BT.LastnDays(tracks)
                    dates=BT.dateList(yrdoyslist)
                    mos=[da[4:6] for da in dates]

                    sto=np.zeros((1,4))
                    data=np.loadtxt('GeneralFormat/'+bid+'.dat',skiprows=1,delimiter=';')
                    datyrs=data[:,1]
                    intdoys=[int(d) for d in data[:,4]]
                    intdoys=np.asarray(intdoys)
                    for i,yrdoy in enumerate(yrdoyslist):
                        
                        w=(datyrs == yrdoy[0]) & (intdoys == yrdoy[1])
                        sub=data[w,:]
                        if i == 0:
                            sto=np.zeros((len(sub),3))
                            sto[:,0]=mos[i]
                            sto[:,1]=sub[:,6]
                            sto[:,2]=sub[:,7]
                        else:
                            out=np.zeros((len(sub),3))
                            out[:,0]=mos[i]
                            out[:,1]=sub[:,6]
                            out[:,2]=sub[:,7]
                            sto=np.concatenate((sto,out))

                    txx,tyy=PF.LLtoXY(sto[:,1],sto[:,2],rot)
                    
                    for m in range(12):
                        wm=sto[:,0] == m+1
                        wmn=np.sum(wm)
                        if wmn > 0:
                            plt.plot(txx[wm],tyy[wm],'ko',ms=3)
                            plt.plot(txx[wm],tyy[wm],'o',color=mocols[m],ms=2)

            if xterlab:
                ulab={'4434517':'JD','4402491':'Ship'}
                if bid[-7:] in ulab:
                    labout=ulab[bid[-7:]]
                    specsym='^'
                else:
                    if binf[bid][0] == '1':
                        specsym='^'
                        labout=binf[bid][1].replace('<br>??','')
                        
                    else:
                        specsym='-'
                        labout=bid[-7:]
                if (cxx >= dom[0]) & (cxx <= dom[1]) & (cyy >= dom[2]) & (cyy <= dom[3]):
                    if bid == '4402491':
                        pid, = plt.plot(cxx,cyy,'s',color='maroon',ms=8,markeredgecolor='w',label='Ship '+cdate)
                    else:
                        if specsym != '-':
                            pid, = plt.plot(cxx,cyy,specsym,color=mocols[ico],ms=8,markeredgecolor='w',label=labout+' '+cdate[0:5])
                        else:
                            pid, = plt.plot(cxx,cyy,usym,color=mocols[ico],ms=8,markeredgecolor='w',label=labout+' '+cdate[0:5])

                    xterlabs.append(pid)
                    ico+=1
                    if ico == len(mocols):
                        ico=0
                        usym='P'
            else:
                plt.plot(cxx,cyy,'ro',ms=8)
            
            if project == 'SIDFEx': utext=std[0]+') '+cdate
            else: utext=cdate
            if showname: utext+=name+' '+bid
            if not xterlab:
                if not showname: plt.text(cxx,cyy,utext,fontweight='bold',color='white')
                else: plt.text(cxx,cyy,utext,color='white')
            if not isup: plt.plot(cxx,cyy,'o',color='gray',ms=6)

    if project == 'FYB_2020': uproject='Float Your Boat 2020'
    else: uproject=project
    plt.title(uproject)
    if xterlab: plt.legend(handles=[xt for xt in xterlabs],loc='upper left')
    if showmap: plt.show()
    else:
        if addlab != 'ZOOM':
            if 'z' in project: addlab=project[-2:]
            else: addlab=''
        plt.savefig('MAPS/Project_Maps/'+uproj+'/'+cdates[1]+'_Map'+addlab+'.png')
        ut.uploadToIABPserver('MAPS/Project_Maps/'+uproj+'/'+cdates[1]+'_Map'+addlab+'.png','Project_Tables/Project_Maps_2021/'+project+addlab+'.png')

        #plt.show()
        plt.close()
        if project == 'SIDFEx':
            ut.uploadToIABPserver('MAPS/Project_Maps/'+uproj+'/'+cdates[1]+'_Map.png','Project_Tables/SIDFEXimages/'+cdates[1].replace('-','')+'.png')
            ut.uploadToIABPserver('MAPS/Project_Maps/'+uproj+'/'+cdates[1]+'_Map.png','Project_Tables/SIDFEXimages/current.png')

def VelocityMap(cdomain='Overview',strdate='current',udomain=[],fsize=(8.85,10),rot=55.0,showplots=0):
    factor=500.

    if strdate == 'current':
        dates=BT.getDates()
        strdate=dates[0].replace('-','')
        
    plt=blankIceMap(cdomain=cdomain,udomain=[],strdate=strdate,fsize=(8.85,10),rot=55.0)
    plt=PF.laloLines(plt,rot)

    opf=open('Data_Products/Daily_Full_Res_Data/Arctic/FR_'+strdate+'.dat','r')
    frdata=opf.read()
    opf.close()

    frdata=frdata.split('\n')[1:-1]
    frdata=[fr for fr in frdata if fr]
    frdata=[fr for fr in frdata if float(fr.split(';')[6]) > 0.0]
    bids=[f.split(';')[0] for f in frdata]

    frinf={}
    for b in bids: frinf[b]=[]
    for f in frdata:
        sf=f.split(';')
        frinf[sf[0]].append(f)

    
    out=np.zeros((len(frinf),5)) #x,y,dx,dy,seconds
    for i,b in enumerate(frinf):

        start=frinf[b][0].split(';')[5:8]
        end=frinf[b][-1].split(';')[5:8]
        print(b)
##        print(start)
##        print(end)
##        print('-------')
        fstart=[float(s) for s in start]
        fend=[float(e) for e in end]

        doydiff=(fend[0]-fstart[0])*(24.0*60.*60.)  #seconds
        xar,yar=PF.LLtoXY([fstart[1],fend[1]],[fstart[2],fend[2]],rot)

        dx=(xar[1]-xar[0])*1000.  #meters
        dy=(yar[1]-yar[0])*1000.  #meters

        out[i,:]=(xar[0],yar[0],dx,dy,doydiff)

    #return out
    dx=out[:,2]
    dy=out[:,3]
    dt=out[:,4]
    wno0=dx != 0
    dxdt=(dx[wno0]*factor)/dt[wno0]
    dydt=(dy[wno0]*factor)/dt[wno0]
    x=out[wno0,0]
    y=out[wno0,1]

    out[wno0,2]=dxdt
    out[wno0,3]=dydt

    for i in range(len(x)):
        plt.arrow(x[i],y[i],dxdt[i],dydt[i],color='white',head_width=25,linewidth=2)
        plt.arrow(x[i],y[i],dxdt[i],dydt[i],color='k',head_width=25)

    #---key----
    pout=[100.,-1200.]
    if cdomain == 'Beaufort Gyre': pout=[-2300.,-1500.]
    if cdomain == 'Bering Sea': pout=[-2000.,1800.]
    plt.arrow(pout[0],pout[1],factor/2.,0,head_width=25,color='white',linewidth=2)
    plt.arrow(pout[0],pout[1],factor/2.,0,head_width=25,color='k',linewidth=1)

    plt.text(pout[0]+10,pout[1]+20,'0.5 m/s',color='k')
    plt.plot(out[:,0],out[:,1],'or',ms=2)
    
    outdate1=strdate[4:6]+'/'+strdate[6:]+'/'+strdate[0:4]
    outdate2=strdate[0:4]+'-'+strdate[4:6]+'-'+strdate[6:]
    subfolder=strdate[0:6]
    plt.title(outdate1+' '+cdomain+': Daily Mean Velocity')
    cdomain=cdomain.replace(' ','_')
    mapcode=serverCode(cdomain,'vel')

    plt.savefig('MAPS/'+subfolder+'/'+outdate2+'_'+cdomain+'-vel_Map.png',bbox_inches='tight')
    ut.uploadToIABPserver('MAPS/'+subfolder+'/'+outdate2+'_'+cdomain+'-vel_Map.png','Maps/'+mapcode+'map_current.png')    
    
    if showplots:
        plt.show()
    
    
def OceanMap(rot=55):
    today=datetime.datetime.now()
    strdate="%.2d/%.2d/%d" % (today.month,today.day,today.year)
    mocols=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']

    opf=open('MasterLists/ArcticTable_Current.txt','r')
    tab=opf.read()
    opf.close()
    tab=tab.split('\n')
    tab=[ta for ta in tab if ta]

    btypes=['UpTempO','UPTEMPO','ITP','SIMB3','IMB','SIMB','WIMBO']

    binf={}
    binf['ITP']=[]
    binf['UpTempO']=[]
    binf['IMB']=[]
    for t in tab:
        st=t.split(';')
        typ=st[3]
        if 'ITP' in typ: binf['ITP'].append(st[0])
        if 'UPTEMPO' in typ: binf['UpTempO'].append(st[0])
        if 'UpTempO' in typ: binf['UpTempO'].append(st[0])
        if 'IMB' in typ: binf['IMB'].append(st[0])

    plt=blankBathMap(cdomain='Central Arctic')
    plt=PF.laloLines(plt,rot=rot)
    yrdoyslist=BT.LastnDays(90)
    dates=BT.dateList(yrdoyslist)
    mos=[da[4:6] for da in dates]

    for bt in binf:
        
        for bid in binf[bt]:

            sto=np.zeros((1,4))
            data=np.loadtxt('GeneralFormat/'+bid+'.dat',skiprows=1,delimiter=';')
            datyrs=data[:,1]
            intdoys=[int(d) for d in data[:,4]]
            intdoys=np.asarray(intdoys)
            for i,yrdoy in enumerate(yrdoyslist):
                
                w=(datyrs == yrdoy[0]) & (intdoys == yrdoy[1])
                sub=data[w,:]
                if i == 0:
                    sto=np.zeros((len(sub),3))
                    sto[:,0]=mos[i]
                    sto[:,1]=sub[:,6]
                    sto[:,2]=sub[:,7]
                else:
                    out=np.zeros((len(sub),3))
                    out[:,0]=mos[i]
                    out[:,1]=sub[:,6]
                    out[:,2]=sub[:,7]
                    sto=np.concatenate((sto,out))

            txx,tyy=PF.LLtoXY(sto[:,1],sto[:,2],rot)
            
            for m in range(12):
                wm=sto[:,0] == m+1
                wmn=np.sum(wm)
                if wmn > 0:
                    plt.plot(txx[wm],tyy[wm],'ko',ms=3)
                    plt.plot(txx[wm],tyy[wm],'o',color=mocols[m],ms=2)

            if bt == 'ITP':
                itp, = plt.plot(txx[-1],tyy[-1],'ms',ms=10,markeredgecolor='k',label='ITP')
                outbid=bid[-3:]
                plt.text(txx[-1]+50,tyy[-1],outbid)
            if bt == 'IMB': imb, = plt.plot(txx[-1],tyy[-1],'cP',ms=10,markeredgecolor='k',label='IMB')
            if bt == 'UpTempO': upt, = plt.plot(txx[-1],tyy[-1],'yo',ms=10,markeredgecolor='k',label='UpTempO')

    plt.title('Ocean Buoys (ITP, IMB, UpTempO) '+strdate)
    
    plt.legend(handles=[itp,imb,upt])
    outdate=strdate.split('/')
    subfolder=outdate[2]+outdate[0]
    outdate2='-'.join([outdate[2],outdate[0],outdate[1]])
    plt.savefig('MAPS/'+subfolder+'/'+outdate2+'_OCEANmap.png',bbox_inches='tight')
    ut.uploadToIABPserver('MAPS/'+subfolder+'/'+outdate2+'_OCEANmap.png','Maps/OCEANmap_current.png') 
    

            
        

    
        
   
def mapit(region='Arctic',period='Current',cdomain='Overview',features='slp',rot=55,addproj='none',pbids=0,showmap=0,tracks=0):
    #features: slp,ta,ts, tracks

    cdates=BT.getDates()
    stryest=cdates[0].replace('-','')

    
    featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    mocols=featcolors

    featind={'slp':9,'ts':10,'ta':11}
    if features=='slp':
        featbar=[960,970,980,990,1000,1010,1020,1030,1040,1050,1060]
    else:
        featbar=[-30.0,-20.,-10.,-5.,-1.,0,1,5.,10.,20.,30.]
    

    opf=open('MasterLists/'+region+'Table_'+period+'.txt','r')
    table=opf.read()
    opf.close()
    table=table.split('\n')[0:-1]

    lats=[]
    lons=[]
    feat=[]
    bids=[]
    
    for t in table:
        st=t.split(';')
        lats.append(float(st[7]))
        lons.append(float(st[8]))
        if features != 'tracks': feat.append(float(st[featind[features]]))
        bids.append(st[0])

    if tracks:
        plt=blankBathMap(cdomain=cdomain,rot=rot)
        for b in bids:
            if os.path.isfile('GeneralFormat/'+b+'.dat'):
                yrdoyslist=BT.LastnDays(tracks)
                dates=BT.dateList(yrdoyslist)
                mos=[da[4:6] for da in dates]

                sto=np.zeros((1,4))
                data=np.loadtxt('GeneralFormat/'+b+'.dat',skiprows=1,delimiter=';')
                datyrs=data[:,1]
                intdoys=[int(d) for d in data[:,4]]
                intdoys=np.asarray(intdoys)
                for i,yrdoy in enumerate(yrdoyslist):
                    
                    w=(datyrs == yrdoy[0]) & (intdoys == yrdoy[1])
                    sub=data[w,:]
                    if i == 0:
                        sto=np.zeros((len(sub),3))
                        sto[:,0]=mos[i]
                        sto[:,1]=sub[:,6]
                        sto[:,2]=sub[:,7]
                    else:
                        out=np.zeros((len(sub),3))
                        out[:,0]=mos[i]
                        out[:,1]=sub[:,6]
                        out[:,2]=sub[:,7]
                        sto=np.concatenate((sto,out))

                txx,tyy=PF.LLtoXY(sto[:,1],sto[:,2],rot)
                
                for m in range(12):
                    wm=sto[:,0] == m+1
                    wmn=np.sum(wm)
                    if wmn > 0:
                        plt.plot(txx[wm],tyy[wm],'ko',ms=1.3)
                        plt.plot(txx[wm],tyy[wm],'o',color=mocols[m],ms=.6)                

    else:
        if features == 'ts': plt=blankSSTMap(cdomain=cdomain,rot=rot)
        elif features == 'ta': plt=blankTaMap(cdomain=cdomain,rot=rot)
        else: plt=blankIceMap(cdomain=cdomain,rot=rot)
    
    xar,yar=PF.LLtoXY(lats,lons,rot)

    if features=='slp':
        #-----plot slp----
        slpdata=np.loadtxt('Satellite_Fields/SLP/slp_'+stryest+'.txt')
        slpxx,slpyy=fieldCoords(field='slp')
        slpxx,slpyy=rotField(slpxx,slpyy,rot)
        slpxx=slpxx[1:,:]
        slpyy=slpyy[1:,:]
        slpdata=np.transpose(slpdata)
        ufeatbar=[0.0]
        for hf in featbar: ufeatbar.append(hf)
        ufeatbar.append(2000.)
        plt.contour(slpxx,slpyy,slpdata,ufeatbar,colors=featcolors)
        #-----------------


    plt.axis('off')
    plt.plot(xar,yar,'ko',ms=5)
    if pbids:
        for i in range(len(xar)):
            cx=xar[i]
            cy=yar[i]
            if bids[i] not in sidbids:
                sb="%d" % (i+100)
                if (cx > dom[0]) & (cx < dom[1]) & (cy > dom[2]) & (cy < dom[3]):
                    plt.text(xar[i],yar[i],sb)

    if features == 'tracks':
        plt.plot(xar,yar,'o',color='k',ms=3.8)
        plt.plot(xar,yar,'o',color='white',ms=3)
    else:
        feat=np.asarray(feat)
        if features == 'slp':
            wbad=feat <= 850.0
            wgood=feat > 850.0
        else:
            wbad=feat <= -99.0
            wgood=feat > -99.0

        xarbad=xar[wbad]
        yarbad=yar[wbad]
        xarg=xar[wgood]
        yarg=yar[wgood]
        featbad=feat[wbad]
        featgood=feat[wgood]

        plt.plot(xarbad,yarbad,'o',color='gray',ms=3)

        wlt=featgood < featbar[0]
        wgt=featgood >= featbar[-1]
        nfeat=len(featbar)-1
        for i in range(nfeat):
            wi=(featgood >= featbar[i]) & (featgood < featbar[i+1])
            plt.plot(xarg[wi],yarg[wi],'o',color=featcolors[i],ms=3)
            
        plt.plot(xarg[wlt],yarg[wlt],'o',color='k',ms=3)
        plt.plot(xarg[wgt],yarg[wgt],'o',color='saddlebrown',ms=3)

            
            

    cyr,cmo,cda=cdates[1].split('-')
    outdate=cmo+'/'+cda+'/'+cyr

    plt=PF.laloLines(plt,rot)
    featlab={'slp':'SLP','ta':'Air Temperature (C)','ts':'Surface Temperature (C)','tracks':'60 Day Tracks colored by Month'}
    plt.title(outdate+' '+cdomain+': '+featlab[features])

    
    cdomain=cdomain.replace(' ','_')
    if showmap: plt.show()
    else:
        subfolder=cdates[1].replace('-','')[0:6]
        if not os.path.isdir('MAPS/'+subfolder): os.system('mkdir MAPS/'+subfolder)
        plt.savefig('MAPS/'+subfolder+'/'+cdates[1]+'_'+cdomain+'-'+features+'_Map.png',bbox_inches='tight')   
        mapcode=serverCode(cdomain,features)
        ut.uploadToIABPserver('MAPS/'+subfolder+'/'+cdates[1]+'_'+cdomain+'-'+features+'_Map.png','Maps/'+mapcode+'map_current.png')
        plt.close()

def SouthMaps():

    today=datetime.datetime.now()
    strdate="%.2d/%.2d/%.d" % (today.month,today.day,today.year)
    
    ucolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    labs=['Sea Level Pressure','Surface Temperature','Atmospheric Temperature']
    filelab=['BP','Ts','Ta']
    opf=open('MasterLists/AntarcticTable_Current.txt','r')
    tab=opf.read()
    tab=tab.split('\n')
    tab=[ta for ta in tab if ta]

    lats=[]
    lons=[]
    bp=[]
    ts=[]
    ta=[]

    for t in tab:
        sd=t.split(';')
        if float(sd[7]) > -90.0:
            lats.append(float(sd[7]))
            lons.append(float(sd[8]))
            bp.append(float(sd[9]))
            ts.append(float(sd[10]))
            ta.append(float(sd[11]))

    lats=np.asarray(lats)
    lons=np.asarray(lons)
    #return lats,lons
    xar,yar=PF.LLtoXY(-lats,-lons,rot=180)
    for r in range(2):
        plt=PF.AntMap()
        plt=PF.laloLines(plt,rot=0)

        if r == 0: var=np.asarray(bp)
        if r == 1: var=np.asarray(ts)
        if r == 2: var=np.asarray(ta)

        if r ==0:
            bar=[960,970,980,990,1000,1010,1020,1030,1040,1050,1060]
            minval=940
            maxval=1080
        else:
            bar=[-30.0,-20.,-10.,-5.,-1.,0,1,5.,10.,20.,30.]
            minval=-60.
            maxval=60.

        plt.plot(xar,yar,'ko',ms=5)
        w0=var < bar[0]
        plt.plot(xar[w0],yar[w0],'o',color=ucolors[0],ms=4)
        for b in range(len(bar)-1):
            w=(var >= bar[b]) & (var < bar[b+1])
            plt.plot(xar[w],yar[w],'o',color=ucolors[b],ms=4)
        wt=var > bar[-1]
        plt.plot(xar[wt],yar[wt],'o',color=ucolors[-1],ms=4)

        wbad=var < minval
        plt.plot(xar[wbad],yar[wbad],'o',color='gray',ms=4)
        wbad=var > maxval
        plt.plot(xar[wbad],yar[wbad],'o',color='gray',ms=4)

        plt.title(labs[r]+' '+strdate)

        datar=strdate.split('/')
        subfolder=datar[2]+datar[0]
        strdate2=subfolder+datar[1]

        if not os.path.isdir('AntMaps/'+subfolder): os.system('mkdir AntMaps/'+subfolder)

        plt.savefig('AntMaps/'+subfolder+'/'+filelab[r]+'-'+strdate2+'.png',bbox_inches='tight')
        ut.uploadToIABPserver('AntMaps/'+subfolder+'/'+filelab[r]+'-'+strdate2+'.png','AntMaps/'+filelab[r]+'_Current.png')        
    

    
def BuoyTracks(showplot=0,runtable='Current'):
    #runtable= year to run 'yyyy'
    mocolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    
    opf=open('MasterLists/ArcticTable_'+runtable+'.txt','r')
    tab=opf.read()
    opf.close()
    tab=tab.split('\n')[0:-1]
    tab=[t for t in tab if t]

           

    count=0
    for t in tab:
        print(t)
        bid=t.split(';')[0]
        #if not os.path.isfile('/Users/wendye/IABP_DATA_BU/BuoyPlots/Tracks/Track_'+bid+'.png'):
        count+=1
        if showplot:
            if count == 10:
                break
        opf=open('WebFormat/'+bid+'.dat','r')
        head=opf.readline()
        opf.close()
        head=head.replace('\n','')
        head=head.split(' ')
        head=[h for h in head if h]

        data=np.loadtxt('WebFormat/'+bid+'.dat',skiprows=1)

        try:
            startdate=BT.DOY2Date(data[0,1],data[0,4])
            strstart="%.2d/%.2d/%d" % (startdate[0],startdate[1],startdate[2])
        except:
            strstart='bad date'

        try:
            enddate=BT.DOY2Date(data[-1,1],data[-1,4])
            strend="%.2d/%.2d/%d" % (enddate[0],enddate[1],enddate[2])
        except:
            strend='bad date'

        minf=BT.MonthFromDoy()
        doys=[int(d) for d in data[:,4]]
        
        molist=[]
        for doy in doys:
            if doy in minf: molist.append(minf[doy])
            else: molist.append(-1)
            
        molist=np.asarray(molist)
        
        ilat=head.index('Lat')
        ilon=head.index('Lon')
        lat=data[:,ilat]
        lon=data[:,ilon]
        clat=lat[lat > 0]
        clon=lon[lat > 0]
        cmolist=molist[lat > 0]
        xar,yar=PF.LLtoXY(clat,clon,55.)
        stdxar=np.std(xar)
        stdyar=np.std(yar)
        wgoodx=(xar > np.mean(xar)-3.*stdxar) & (xar < np.mean(xar)+3.*stdxar)
        wgoody=(yar > np.mean(yar)-3.*stdyar) & (yar < np.mean(yar)+3.*stdyar)
        meanx=np.mean(xar[wgoodx])
        meany=np.mean(yar[wgoody])
        cdomain=[(meanx-3.*stdxar)-1000.,(meanx+3.*stdxar)+1000.,(meany-3.*stdyar)-1000.,(meany+3.*stdyar)+1000.]
        xdiff=cdomain[1]-cdomain[0]
        ydiff=cdomain[3]-cdomain[2]
        if xdiff < ydiff:
            ddiff=(ydiff-xdiff)/2.0
            cdomain[0]+=ddiff
            cdomain[1]+=ddiff
        else:
            ddiff=(xdiff-ydiff)/2.0
            cdomain[2]+=ddiff
            cdomain[3]+=ddiff
           
        try:
            plt=blankBathMap(udomain=cdomain,fsize=(10,10))
        except:
            cdomain=[-2500,2500,-2500,2500]
            plt=blankBathMap(udomain=cdomain)
            
        plt=PF.laloLines(plt,55.)

        plt.plot(xar,yar,'ok',ms=3)
        for m in range(12):
            wm = cmolist == m+1
            if np.sum(wm) > 0: plt.plot(xar[wm],yar[wm],'o',color=mocolors[m],ms=2)

        plt.title(bid+'  '+strstart+' to '+strend)
        if showplot:
            plt.show()
        else:
            plt.savefig('BuoyPlots/Tracks/Track_'+bid+'.png',bbox_inches='tight')
            ut.uploadToIABPserver('BuoyPlots/Tracks/Track_'+bid+'.png','BuoyPlots/Tracks/Track_'+bid+'.png')
            
       
def TimeSeriesPlots(showplots=0,runtable='Current',pbid=['']):
    mocolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']

    if pbid[0] != '': tab=pbid
    else:
        opf=open('MasterLists/ArcticTable_'+runtable+'.txt','r')
        tab=opf.read()
        opf.close()
        tab=tab.split('\n')[0:-1]
        tab=[t for t in tab if t]

        if showplots: tab=tab[0:10]
    for t in tab:
        if pbid[0] != '': bid=t
        else: bid=t.split(';')[0]
        print(bid)
        opf=open('WebFormat/'+bid+'.dat','r')
        head=opf.readline()
        opf.close()
        head=head.replace('\n','')
        head=head.split(' ')
        head=[h for h in head if h]

        data=np.loadtxt('WebFormat/'+bid+'.dat',skiprows=1)
        data=data[data[:,4] >= 0,:]

        startdate=BT.DOY2Date(data[0,1],data[0,4])
        enddate=BT.DOY2Date(data[-1,1],data[-1,4])
        strstart="%.2d/%.2d/%d" % (startdate[0],startdate[1],startdate[2])
        strend="%.2d/%.2d/%d" % (enddate[0],enddate[1],enddate[2])

        doys=data[:,4]
        years=data[:,1]
        mos=[]
        dateobj=[]
        for i in range(len(doys)):
            try:
                cdate=BT.DOY2Date(years[i],doys[i])
                newobj=datetime.datetime(int(years[i]),int(cdate[0]),int(cdate[1]),int(cdate[3]),int(cdate[4]))
                dateobj.append(newobj)
                mos.append(cdate[0])
            except:
                print(data[i,:])
                return data[i,:]
        #return dateobj
    
        mos=np.asarray(mos)

        datelab=" %.2d/%.2d/%d to %.2d/%.2d/%d" % (dateobj[0].month,dateobj[0].day,dateobj[0].year,dateobj[-1].month,dateobj[-1].day,dateobj[-1].year)

        dt=timedelta.Timedelta(dateobj[-1]-dateobj[0])
        if dt.days <= 31: rule=rrulewrapper(DAILY,interval=1)
        if (dt.days > 31) and (dt.days <= 90): rule=rrulewrapper(WEEKLY)
        if (dt.days > 90) and (dt.days <= 1095): rule=rrulewrapper(MONTHLY)
        if dt.days > 1095: rule=rrulewrapper(YEARLY)

        #rule=rrulewrapper(MONTHLY,interval=1)
        loc=RRuleLocator(rule)
        formatter=DateFormatter('%m/%d/%y')


        uplots=[]
        if 'BP' in head: uplots.append('BP')
        if 'Ts' in head: uplots.append('Ts')
        if 'Ta' in head: uplots.append('Ta')

        axlabs={'BP':'Sea Level Pressure','Ts':'Surface Temperature','Ta':'Atmospheric Temperature'}
        yaxlims={'BP':[940,1080],'Ts':[-40,20],'Ta':[-40,30]}

        if uplots:
            vals={}
            if 'BP' in uplots:
                ibp=head.index('BP')
                bp=data[:,ibp]
                vals['BP']=bp

            if 'Ts' in uplots:
                its=head.index('Ts')
                ts=data[:,its]
                vals['Ts']=ts

            if 'Ta' in uplots:
                ita=head.index('Ta')
                ta=data[:,ita]
                vals['Ta']=ta

            nplots=len(uplots)
            plt.rcParams['figure.figsize']=(10,4*nplots)
            plt.rcParams['font.size']=12

            if nplots == 3:
                fig, (ax1,ax2,ax3)=plt.subplots(3,1)
                axar=[ax1,ax2,ax3]
            if nplots == 2:
                fig, (ax1,ax2)=plt.subplots(2,1)
                axar=[ax1,ax2]
            if nplots == 1:
                fig, ax1=plt.subplots()
                axar=[ax1]
                
    

            for i,ax in enumerate(axar):
                ax.xaxis.set_major_locator(loc)
                ax.xaxis.set_major_formatter(formatter)
                ax.xaxis.set_tick_params(rotation=85,labelsize=10)

                ax.set_ylim(yaxlims[uplots[i]][0],yaxlims[uplots[i]][1])
                ax.set_title(axlabs[uplots[i]]+' '+bid+' '+datelab)
                ax.set_ylabel(axlabs[uplots[i]])

                cvals=vals[uplots[i]]
                ax.plot_date(dateobj,cvals,'ko',ms=2)
                for m in range(12):
                    wm=mos == m+1
                    if np.sum(wm) > 0:
                        wmi=[r for r in range(len(wm)) if wm[r]]
                        subobj=[dateobj[j] for j in wmi]
                        ax.plot_date(subobj,cvals[wm],'o',ms=1,color=mocolors[m])
                        
                ax.grid('True')

            plt.subplots_adjust(bottom=0.15,hspace=0.5)
            



            if showplots:
                plt.show()
            else:
                plt.subplots_adjust(bottom=0.15)
                plt.savefig('BuoyPlots/TimeSeries/TS_'+bid+'.png',bbox_inches='tight')
                ut.uploadToIABPserver('BuoyPlots/TimeSeries/TS_'+bid+'.png','BuoyPlots/TimeSeries/TS_'+bid+'.png')


def dailyMaps():

    dates=BT.getDates()
    yest=dates[0].replace('-','')
    
    pfields.getNSIDCice()
    pfields.getNSIDCice(nors='s')
    pfields.processNSIDCice()
    pfields.processNSIDCice(nors='s')
    pfields.getNCEPslp('2021')
    pfields.processSLP('2021')
    pfields.processNCEPta('2021')

    
    cdomains=['Overview','Central Arctic','Beaufort Gyre','GIN Sea','Bering Sea']
    quans=['slp','ts','ta','tracks']
    for cd in cdomains:
        for q in quans:
            if q == 'tracks': mapit(cdomain=cd,features=q,tracks=60)
            else: mapit(cdomain=cd,features=q)

        VelocityMap(cdomain=cd)

    projectMap(tracks=60)
    projectMap(project='FYB_2020',tracks=170)
    projectMap(project='FYB_2020z1',tracks=170)
    projectMap(project='FYB_2020z2',tracks=170)
    projectMap(project='FYB_2020z3',tracks=170)
    projectMap(project='ICE-PPR_DiskoBay_2021',xterlab=1)
    projectMap(project='ICE-PPR_DiskoBay_2021z',xterlab=1)
    
    latslons=[[70.,71.,72.,73.,74.,75.],[196.,198.,200.,202.,204.,206.,208.,210.,212.,214.,216.]]
    projectMap(project='Utqiagvik_2021',showname=1,latslons=latslons,tracks=7)
    OceanMap()
    SouthMaps()

    
    today=datetime.datetime.now()
    dofw=today.isoweekday()
    if dofw == 1:
        MondayMaps()


def MondayMaps():

    BuoyTracks()
    TimeSeriesPlots()
    



