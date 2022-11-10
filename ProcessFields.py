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
from nsidc_download_0081_v02 import nsidc_download_0081_v02

#======= Get and Process NSIDC ==============
def getICE(strdate='default',nors='n',src='nsidc-0081'):
    #strdate= yyyymmdd
    regdict={'n':'north', 's':'south'}

    if strdate == 'default':
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    noFile = True
    numDaysBack = 0

    if src=='g02202':
        icepath = f'/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/NSIDC_ICE/{regdict[nors]}/{strdate[:4]}'
        icefile = f'seaice_conc_daily_nh_{objdate.year}{objdate.month:02}{objdate.day:02}_f17_v04r00.nc'
        print(f'{icepath}/{icefile}')
        if os.path.exists(f'{icepath}/{icefile}'):
            ncdata=nc.Dataset(f'{icepath}/{icefile}')
            ice=np.squeeze(ncdata['cdr_seaice_conc'])  # np.squeeze converts nc dataset to np array
            ice[ice==251] = 1.  # fill pole_hole_mask, flags are not scaled
            ice[ice==254] = np.nan  # land
            ice[ice==253] = np.nan  # coast
            ice[ice==0] = np.nan  # no ice
            y=ncdata['ygrid'][:]
            x=ncdata['xgrid'][:]
            icexx, iceyy = np.meshgrid(x,y)

    elif src=='nsidc-0081':
        while noFile:
            print('ICE',strdate)
            if numDaysBack == 7:
                ice, icexx, iceyy = None, None, None
                break

            nsidc_download_0081_v02(strdate,nors)
            # icepath = f'/Volumes/GoogleDrive/My Drive/UpTempO/Satellite_Fields/NSIDC_ICE/{regdict[nors]}/{strdate[:4]}'
            icepath = f'/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/NSIDC_ICE/{regdict[nors]}/{strdate[:4]}'
            icefile = f'NSIDC0081_SEAICE_PS_{nors.capitalize()}25km_{strdate}_v2.0.nc'
            print('line 41 in pfields',f'{icepath}/{icefile}')
            if os.path.exists(f'{icepath}/{icefile}'):
                ncdata=nc.Dataset(f'{icepath}/{icefile}')
                # print('flag meanings',ncdata.variables['F18_ICECON'].getncattr('flag_meanings'))
                # print('flag values',ncdata.variables['F18_ICECON'].getncattr('flag_values'))
                # print(ncdata['F18_ICECON'].shape)
                ice=np.squeeze(ncdata['F18_ICECON'])  # np.squeeze converts nc dataset to np array
                ice[ice==251] = 1.  # fill pole_hole_mask, flags are not scaled
                ice[ice==254] = np.nan  # land
                ice[ice==253] = np.nan  # coast
                ice[ice==0] = np.nan  # no ice
                y=ncdata['y'][:]
                x=ncdata['x'][:]
                icexx, iceyy = np.meshgrid(x,y)
                noFile = False
            else:
                objdate = objdate - dt.timedelta(days=1)
                strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
                numDaysBack += 1

    return strdate,ice,icexx,iceyy

#======= Get and Process NSIDC ==============
# WErmold code downloading .bin files from sidads.colorado.edu
def getNSIDCice(strdate='default',nors='n'):
    #strdate= yyyymmdd

    if strdate == 'default':
        today=dt.datetime.now()
        strtod="%d%.2d%.2d" % (today.year,today.month,today.day)
        yest=today-dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)

    path='/Users/WendyE/Dropbox/RecentWarming/NSIDCiceDATA/'

    ftp=FTP('sidads.colorado.edu')
    ftp.login()
    if nors == 'n':
        reg='north/'
        servfile='nt_'+strdate+'_f18_nrt_n.bin'
        ftp.cwd('pub/DATASETS/nsidc0081_nrt_nasateam_seaice/north/')
    else:
        reg='south/'
        servfile='nt_'+strdate+'_f18_nrt_s.bin'
        ftp.cwd('/DATASETS/nsidc0081_nrt_nasateam_seaice/south/')

    try:
        localfile=open(path+reg+servfile,'wb')
        ftp.retrbinary('RETR '+servfile, localfile.write)
        localfile.close()
        ftp.quit()
        print(servfile+' was successfully downloaded.')
    except:
        ftp.quit()
        print(servfile+' was not found on the nsidc server.')

#======= Get and Process NSIDC ==============
# Wermold code to process .bin files and save as .txt
def processNSIDCice(strdate='default',nors='n'):
    #strdate=yyyymmdd

    if strdate == 'default':
        today=dt.datetime.now()
        strtod="%d%.2d%.2d" % (today.year,today.month,today.day)
        yest=today-dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)

    if nors == 'n': regpath='north'
    else: regpath='south'

    cadd='f18'
    path='/Users/wendye/Dropbox/RecentWarming/NSIDCiceDATA/'+regpath+'/nt_'+strdate+'_'+cadd+'_nrt_'+nors+'.bin'
    #path='/Users/wendye/Dropbox/RecentWarming/nt_'+strdate+'_'+cadd+'_nrt_'+nors+'.bin'
    #path='/Users/wendye/Dropbox/RecentWarming/NSIDCiceDATA/'+strdate[0:4]+'/nt_'+strdate+'_'+cadd+'_v1.1_n.bin'
    print(path)

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

    np.savetxt('Satellite_Fields/NSIDC_ICE/'+regpath+'/'+strdate+'.txt',pdata,fmt="%.2f")

#============== Get and process SLP ================
def getNCEPslp(year):
    servfile=f'slp.{year}.nc'
    localput=f'/Users/suzanne/Google Drive/UpTempO/SeaLevelPressure/slp.{year}.nc'
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

    # path=f'/Volumes/GoogleDrive/My Drive/UpTempO/SeaLevelPressure/slp.{year}.nc'
    path=f'/Users/suzanne/Google Drive/UpTempO/SeaLevelPressure/slp.{year}.nc'
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
# WErmold code to download and save as ascii
def processSST(strdate='default'):
    #strdate = 'yyyymmdd'
    print(strdate)
    if strdate == 'default':
        today=dt.datetime.now()
        strtod="%d%.2d%.2d" % (today.year,today.month,today.day)
        yest=today-dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)

        year="%d" % (yest.year)
        month="%.2d" % (yest.month)
    else:
        year=strdate[0:4]
        month=strdate[4:6]

    #thefile='oisst-avhrr-v02r01.'+strdate+'_preliminary.nc'
    thefile='oisst-avhrr-v02r01.'+strdate+'.nc'
    #if strdate != 'default': thefile='oisst-avhrr-v02r01.'+strdate+'.nc'
    theurl='https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/'+year+month+'/'+thefile
    if not os.path.isfile('Satellite_Fields/SST/'+year+'/MyData/SST-'+strdate+'.dat'):
        ncpath='/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/OISST-AVHRR-v2.1/'+thefile
        if not os.path.isfile('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/OISST-AVHRR-v2.1/'+thefile):
            thefile=thefile.replace('.nc','_preliminary.nc')
            ncpath='/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/OISST-AVHRR-v2.1/'+thefile

        print(ncpath)
        #----download if required---
        if not os.path.isfile(ncpath):
            with requests.get(theurl) as resp:
                ncdata=nc.Dataset('in-mem-file',mode='r',memory=resp.content)
                #return ncdata
                #opw=open(ncpath,'wb')
                #opw.write(ncdata)
                #opw.close()

            #ncdata=nc.Dataset(theurl)
        else:
            ncdata=nc.Dataset(ncpath)

        for dim in ncdata.dimensions.values(): print(dim)
        for var in ncdata.variables.values(): print(var)

        sst=ncdata['sst']
        lat=ncdata['lat']
        lon=ncdata['lon']
        lat=np.asarray(lat)
        lon=np.asarray(lon)
        sst=sst[0,0,:,:]

    ##    print('sst: ')
    ##    print(np.shape(sst))   (1,1,720,1440)
    ##    print('lat:')
    ##    print(np.shape(lat))   (720,)
    ##    print('lon:')
    ##    print(np.shape(lon))   (1440,)
    ##

        wgood=sst > -999.0
        sst[wgood]=sst[wgood]/100.
        sst=sst[500:720,:]
        lat=lat[500:720]

        sqlats=np.zeros((220,1440))
        sqlons=np.zeros((220,1440))
        for r in range(1440):
            sqlats[:,r]=lat
        for r in range(220):
            sqlons[r,:]=lon

    ##    flatlat=sqlats.flatten()
    ##    flatlon=sqlons.flatten()
    ##    sstxx,sstyy=pfuncs.LLtoXY(flatlat,flatlon,0.0)
    ##    sqxx=np.reshape(sstxx,(220,1440))
    ##    sqyy=np.reshape(sstyy,(220,1440))
    ##    np.savetxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/SST-XX.dat',sqxx,fmt="%.4f")
    ##    np.savetxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/SST-YY.dat',sqyy,fmt="%.4f")

        np.savetxt('/Users/wendye/Dropbox/RecentWarming/NOAA-Daily-SST/'+year+'/MyData/SST-'+strdate+'.dat',sst,fmt="%.2f")
        np.savetxt('Satellite_Fields/SST/'+year+'/MyData/SST-'+strdate+'.dat',sst,fmt="%.2f")



#========= Get SST ==================
def getSST(strdate='default'):
    #strdate = 'yyyymmdd'

    if strdate == 'default':
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate="%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    year="%d" % (objdate.year)   # this infor for url sub directories
    month="%.2d" % (objdate.month)
    print(strdate)
    # SST is available ~9am Pacific
    thefile='oisst-avhrr-v02r01.'+strdate+'_preliminary.nc'
    # thefile='oisst-avhrr-v02r01.'+strdate+'.nc'
    theurl=f'https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{year}{month}/{thefile}'

    ncpath=f'/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/sstNOAA/{year}/{thefile}'
    # if not os.path.exists(theurl):
    #     theurl = theurl.replace('_preliminary','')

   #----download yesterday's data, or go back one day at a time for one week to get data
    noFile = True
    numDaysBack = 0
    while noFile:
        print('line 320 in processfields', noFile,numDaysBack)
        print(theurl)
        if numDaysBack==7:
            break
        request = urllib.request.Request(theurl)
        request.get_method = lambda: 'HEAD'
        try:
            urllib.request.urlopen(request)
            noFile = False
            urllib.request.urlretrieve(theurl,ncpath)
            break
        except: # urllib.request.HTTPError:
            numDaysBack += 1
            objdate = objdate - dt.timedelta(days=1)
            strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
            thefile='oisst-avhrr-v02r01.'+strdate+'_preliminary.nc'
            # thefile='oisst-avhrr-v02r01.'+strdate+'.nc'
            theurl = f'https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{objdate.year}{objdate.month:02}/{thefile}'
            ncpath = f'/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/sstNOAA/{objdate.year}/{thefile}'

    if numDaysBack<7:
        ncdata=nc.Dataset(ncpath)
        sst=np.squeeze(ncdata['sst'])
        sst[sst<-900] = np.nan  # set invalids=-999 to nan
        lat=ncdata['lat'][:]
        lon=ncdata['lon'][:]
        sstlon, sstlat = np.meshgrid(lon,lat)
    else:
        sst,sstlon,sstlat = None, None, None

    return strdate, sst, sstlon, sstlat

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
