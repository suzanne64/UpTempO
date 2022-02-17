#!/usr/bin/python
import numpy as np
import os
import datetime as dt
# from datetime import date
#import timedelta
import sys
import netCDF4 as nc
import BuoyTools_py3_toot as BT
import PlottingFuncs as pfuncs
from ftplib import FTP
import urllib
import requests
import matplotlib.pyplot as plt

#======= Get and Process NSIDC ==============
def getNSIDCice(strdate='default',nors='n'):
    #strdate= yyyymmdd

    if strdate == 'default':
        today=dt.datetime.now()
        strtod="%d%.2d%.2d" % (today.year,today.month,today.day)
        yest=today-dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)

    # path='/Volumes/GoogleDrive/My Drive/UpTempO/NSIDCiceDATA/'
    path=f'/Volumes/GoogleDrive/My Drive/UpTempO/NSIDC_ICE/'
    ftp=FTP('sidads.colorado.edu')
    ftp.login()

    if nors == 'n':
        reg='north/'
        servfile='nt_'+strdate+'_f18_nrt_n.bin'
        ftp.cwd('pub/DATASETS/nsidc0081_nrt_nasateam_seaice/north/')       
        # ftp.retrlines('LIST')
    else:
        reg='south/'
        servfile='nt_'+strdate+'_f18_nrt_s.bin'
        ftp.cwd('/DATASETS/nsidc0081_nrt_nasateam_seaice/south/')

    try:
        localfile=open(f'{path}{reg}{strdate[:4]}/{servfile}','wb')
        ftp.retrbinary('RETR '+servfile, localfile.write)
        localfile.close()
        ftp.quit()
        print(servfile+' was successfully downloaded.')
    except:
        ftp.quit()
        print(servfile+' was not found on the nsidc server.')
    
def processNSIDCice(strdate='default',nors='n'):
    #strdate=yyyymmdd

    if strdate == 'default':
        today=dt.datetime.now()
        strtod="%d%.2d%.2d" % (today.year,today.month,today.day)
        yest=today-dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)
    print('line 60, pfields',strdate)
    if nors == 'n': regpath='north'
    else: regpath='south'

    cadd='f18'
    path=f'/Volumes/GoogleDrive/My Drive/UpTempO/NSIDC_ICE/{regpath}/nt_{strdate}_{cadd}_nrt_{nors}.bin'

    data=np.fromfile(path,dtype='ubyte')
    data=data[300:]
    data=data/255.0
    if nors == 'n': data=np.reshape(data,(448,304))
    else: data=np.reshape(data,(332,316))
    #data=np.transpose(data)
    #data=np.rot90(data)

    sh=np.shape(data)
    
    pdata=np.zeros(sh)
    for i in range(sh[0]):
        pdata[i,:]=data[sh[0]-1-i,:]
        
    # establish x/y grid
    if not os.path.exists(f'/Volumes/GoogleDrive/My Drive/UpTempO/NSIDC_ICE/{regpath}/xx.dat'):
        # probably not the best way
        dx = dy = 25000
        x = np.arange(-3850000, +3750000, +dx)
        y = np.arange(+5850000, -5350000, -dy)
        xx, yy = np.meshgrid(x,y)
        np.savetxt('Satellite_Fields/NSIDC_ICE/'+regpath+'/xx.txt',xx,fmt="%.2f")
        np.savetxt('Satellite_Fields/NSIDC_ICE/'+regpath+'/yy.txt',yy,fmt="%.2f")
        extent = [x[0]-dx/2, x[-1]+dx/2, y[-1]-dy/2, y[0]+dy/2]
        fig,ax = plt.subplots(1,2)
        ax[0].imshow(xx);fig.colorbar()
        ax[1].imshow(yy);fig.colorbar()
        plt.show()

    np.savetxt('Satellite_Fields/NSIDC_ICE/'+regpath+'/'+strdate+'.txt',pdata,fmt="%.2f")
    
#============== Get and process SLP ================
def getNCEPslp(year):
    servfile=f'slp.{year}.nc'
    localput=f'/Volumes/GoogleDrive/My Drive/UpTempO/SeaLevelPressure/slp.{year}.nc'
    localfile=open(localput,'wb')

    #ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/surface/slp.2016.nc

    ftp = FTP('ftp.cdc.noaa.gov')
    ftp.login('anonymous','anonymous')
    #ftp.cwd('Datasets/ncep.reanalysis.dailyavgs/surface/')
    ftp.cwd('Datasets/ncep/')

    checkfile=[]
    try:
        ftp.retrlines('LIST '+servfile,checkfile.append)
        print(checkfile)

        ftp.retrbinary('RETR '+servfile,localfile.write)
        localfile.close()
        print(servfile+' was downloaded successfully.')
    except:
        print(servfile+' was not found')

    localfile.close()

    ftp.quit()
    
def processSLP(year,writexy=0):

    path=f'/Volumes/GoogleDrive/My Drive/UpTempO/SeaLevelPressure/slp.{year}.nc'
    ncdata=nc.Dataset(path)
    #for dim in ncdata.dimensions.values(): print(dim)
    #for var in ncdata.variables.values(): print(var)
    
    slp=ncdata['slp']
    lat=ncdata['lat']
    lon=ncdata['lon']
    lat=np.asarray(lat)
    lon=np.asarray(lon)

    wlat=lat > 30
    lat=lat[wlat]
    sqlat=np.zeros((len(lat),len(lon)))
    sqlon=np.zeros((len(lat),len(lon)))

    shapeout=(len(lat),len(lon))
    nvals=len(lon)*len(lat)

    if writexy:
        for i in range(len(lat)):
            sqlat[i,:]=lon
            
        for i in range(len(lon)):
            sqlon[:,i]=lat

        rlat=np.reshape(sqlat,(nvals))
        rlon=np.reshape(sqlon,(nvals))
        slpxx,slpyy=pfuncs.LLtoXY(rlat,rlon,0.0)
        slpxx=np.reshape(slpxx,shapeout)
        slpyy=np.reshape(slpyy,shapeout)
        print(np.shape(slpxx))
        np.savetxt('Satellite_Fields/SLP/SLP_XX.txt',slpxx,fmt="%.4f")
        np.savetxt('Satellite_Fields/SLP/SLP_YY.txt',slpyy,fmt="%.4f")
        

    ndays=np.shape(slp)[0]
    for r in range(ndays):
        cr=r+1
        date=BT.DOY2Date(year,cr)
        strdate="%.2d%.2d" % (date[0],date[1])
        strdate=year+strdate
        if not os.path.isfile('Satellite_Fields/SLP/slp_'+strdate+'.txt'):
            cslp=slp[r,:,:]
            cslp=cslp[wlat,:]
            print(np.shape(cslp))
            np.savetxt('Satellite_Fields/SLP/slp_'+strdate+'.txt',cslp,fmt="%.2f")
           
#========= Get and Process SST ==================
def processSST(strdate='default'):
    #strdate = 'yyyymmdd'
    
    if strdate == 'default':
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    year="%d" % (objdate.year)   # this infor for url sub directories
    month="%.2d" % (objdate.month)
    print(strdate)
        
    thefile='oisst-avhrr-v02r01.'+strdate+'_preliminary.nc'
    theurl=('https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/'+year+month+'/'+thefile)
    
    ncpath=f'/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/sstNOAA/{year}/{thefile}'
    print('line 180, ncapth',ncpath,year,month)
    print('theurl',theurl)
    
    #----download if required---
    # if not os.path.isfile(ncpath):
    noFile = True
    numDaysBack = 0
    while noFile: 
        print(theurl)
        if numDaysBack==7:
            return 
        request = urllib.request.Request(theurl)
        request.get_method = lambda: 'HEAD'
        try: 
            urllib.request.urlopen(request)
            print('the file is there')
            noFile = False
            urllib.request.urlretrieve(theurl,ncpath)
        except: # urllib.request.HTTPError:
            print('in the except')
            numDaysBack += 1
            objdate = objdate - dt.timedelta(days=1)
            strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
            print('line 215',strdate)
            thefile='oisst-avhrr-v02r01.'+strdate+'_preliminary.nc'
            theurl = f'https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{objdate.year}{objdate.month}/{thefile}'
            ncpath = f'/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/sstNOAA/{objdate.year}/{thefile}'
            
    print('pfields, line 218',strdate)
    # retrieve data to save as ascii     best way?
    ncdata=nc.Dataset(ncpath)   
    sst=np.squeeze(ncdata['sst'])
    lat=ncdata['lat'][:]
    lon=ncdata['lon'][:]
    
    # fig,ax = plt.subplots(1,1)
    # h = ax.imshow(sst,vmin=-10,vmax=10)
    # fig.colorbar(h)
    # plt.show()
    # exit(-1)
 
    # print('sst: ')        
    # print(np.shape(sst))  # (720,1440)
    # print('lat:')
    # print(np.shape(lat))  # (720,)
    # print('lon:')
    # print(np.shape(lon))  # (1440,)

    # apply scale factor 1/100.
    wgood=sst > -999.0
    sst[wgood]=sst[wgood]/100.
    # trim to 35.125:0.25:89.875
    sst=sst[500:,:]
    lat=lat[500:]

    sqlon, sqlat = np.meshgrid(lon,lat)
    # print(sqlat.shape,sqlon.shape)
    # exit(-1)
    # sqlats=np.zeros((220,1440))
    # sqlons=np.zeros((220,1440))
    # for r in range(1440):
    #     sqlats[:,r]=lat
    # for r in range(220):
    #     sqlons[r,:]=lon

    # flatlat=sqlats.flatten()
    # flatlon=sqlons.flatten()
    sstxx,sstyy=pfuncs.LLtoXY(sqlat.flatten(),sqlon.flatten(),0.0)
    sstxx=np.reshape(sstxx,(220,1440))
    sstyy=np.reshape(sstyy,(220,1440))
    print('line 222, ProcessFields',sst.shape, sstxx.shape, sstyy.shape)
    np.savetxt('/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/sstNOAA/SST-XX.dat',sstxx,fmt="%.4f")
    np.savetxt('/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/sstNOAA/SST-YY.dat',sstyy,fmt="%.4f")
    np.savetxt('/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/sstNOAA/'+year+'/SST-'+strdate+'.dat',sst,fmt="%.2f")
    # np.savetxt('Satellite_Fields/SST/SST-XX.dat',sqxx,fmt="%.4f")
    # np.savetxt('Satellite_Fields/SST/SST-YY.dat',sqyy,fmt="%.4f")
    # np.savetxt('Satellite_Fields/SST/'+year+'/SST-'+strdate+'.dat',sst,fmt="%.2f")        
    return strdate, sst, sstxx, sstyy
    
def processNCEPta(year):

    #path='/Users/wendye/Dropbox/RecentWarming/NCEP_Ta/air.'+year+'.nc'
    #procpath='/Users/wendye/Dropbox/ICE_SST_SLP_DATA/NCEP_Ta/'
    path='Satellite_Fields/air.sig995.'+year+'.nc'
    procpath='Satellite_Fields/NCEP_Ta/'
    theurl='https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/surface/air.sig995.'+year+'.nc'

    with requests.get(theurl) as resp:
        ncdata=nc.Dataset('in-mem-file',mode='r',memory=resp.content)


    #return ncdata
    #for dim in ncdata.dimensions.values(): print(dim)
    #for var in ncdata.variables.values(): print(var)
    
    ta=ncdata['air'][:].data  # new file shape(744,73,144)   #shape(161,12,73,144) --> (doy,level,lat,lon)
    lat=ncdata['lat'][:].data #shape(73)
    lon=ncdata['lon'][:].data #shape(144)
    thour=ncdata['time'][:].data
    start=date(1800,1,1)
    finish=date(int(year),1,1)
    tdelt=timedelta.Timedelta(finish-start)
    tdhours=tdelt.days*24.
    hourssinceJan=[t-tdhours for t in thour]
    doy=[(h/24.)+1 for h in hourssinceJan]
    #return doy
    
    
#    level=ncdata['level'].data #shape(12)
    lat=np.asarray(lat)
    lon=np.asarray(lon)

    print(lat[0],lon[0])

    
    

    sh=np.shape(ta)
    print(sh)
    lat=lat[0:21]
    
    for d in range(sh[0]):
        cdoy=doy[d]
        dec=(cdoy-int(cdoy))*100.
        cdate=BT.DOY2Date(year,cdoy)
        cdate="%d%.2d%.2d.%d" % (int(cdate[2]),int(cdate[0]),cdate[1],dec)
        
        
        
        if not os.path.isfile(procpath+'Ta_'+cdate+'.dat'):
            print(cdate)
            cair=ta[d,0:21,:]
            cair=cair-273.15
            #cair=0.01*cair+477.65-273.15
            np.savetxt(procpath+'Ta_'+cdate+'.dat',cair,fmt="%.2f")

        
    
