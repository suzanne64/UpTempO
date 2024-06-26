#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 13:36:09 2021

@author: suzanne
"""

import matplotlib.pyplot as plt  # ver 3.5
import numpy as np
import datetime as dt
# import cmocean

import cartopy.crs as ccrs
# import pyepsg
import cartopy.feature as cfeature
import ProcessFields as pfields
import IABPplots as iplots

def UpTempOArcticMap(strdate=None): #nors='n'):
    # iceplot = 1
    # sstplot = 1
    if strdate == None:
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    # get satellite ice concentration data
    # if ice data looks wack
    wackice = 1
    if wackice:  # go back a day
        objdate = dt.datetime.now() - dt.timedelta(days=2)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    # get satellite ice concentration data
    icedate, ice, icexx, iceyy = pfields.getICE(strdate,nors='n')
    print('Date of ice map',icedate,ice.shape)
    if wackice:  # reset for title
        objdate = dt.datetime.strptime(strdate,'%Y%m%d') + dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    icecolors=['0.4','0.5','0.6','0.725','0.85','1.0']
    icelevels=[0.2,0.3,0.4,0.5,0.75]

    # get satellite sst data
    # if sst data looks wack
    wacksst = 0
    if wacksst:  # go back a day
        objdate = dt.datetime.now() - dt.timedelta(days=2)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    sstdate, sst, sstlon, sstlat = pfields.getSST(strdate)   
    if wacksst:  # reset for title
        objdate = dt.datetime.strptime(strdate,'%Y%m%d') + dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    # something has changed with the sst, starting Jan 6, 2024
    # make land mask
    landmask = np.full(sst.shape,fill_value=np.nan)
    landmask[np.isnan(sst)] = 1
    landlevels=[0.99, 1.01]

    featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    featbar=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]   # SST

    # # establish contour levels and colors
    # featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    # featbar=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]   # SST
    # featcolors=['darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange']#,'orangered','red','saddlebrown']
    # featbar=[-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0] #,3.000001,4.0,5.0]   # SST
    # else:
    #     featbar=[-30.,-20.,-10.,-5.,-1.,0.0,1.0,5.0,10.,20.,30.]
    
    fig1, ax1 = plt.subplots(1,figsize=(8.3,10))
    ax1 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
    ax1.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
    ax1.add_feature(cfeature.LAND,facecolor='gray')
    ax1.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
    kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
    # both of these set_extent commands work well
    # ax1.set_extent([-180,180,65,90],crs=ccrs.PlateCarree())
    if sst is not None:
        chsst = ax1.contourf(sstlon,sstlat,sst,levels=featbar,colors=featcolors,extend='both',transform=ccrs.PlateCarree()) #,levels=featbar, colors=featcolors, extend='both'
        chland = ax1.contourf(sstlon,sstlat,landmask,levels=landlevels,transform=ccrs.PlateCarree(),cmap='gist_gray') 
    else:
        ax1.text(-10,74,'SST data unavailable',color='k',fontsize=10,transform=ccrs.PlateCarree())

    if ice is not None:
        chice = ax1.contourf(icexx,iceyy,ice, colors=icecolors, levels=icelevels, vmin=0, vmax=0.9, extend='both',
                      transform=ccrs.Stereographic(**kw))   #use either colors or cmap
    else:
        ax1.text(10,88,'ICE data unavailable',color='k',fontsize=10,transform=ccrs.PlateCarree())
    # fig1.colorbar(chice)  

    BeringSea = 0  # this is 1 for microSWIFTs in Bering Sea
    if not BeringSea:
        ax1.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
    else:
        ax1.set_extent([-2.0e6,2.0e6,-2.55e6,3.5e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
    #     ax1.plot(-178,62,'v',transform=ccrs.PlateCarree())
    # ax1.set_title(f'SST on {strdate}')
    # fig1.colorbar(chsst)
    # plt.show()
    # exit()
       
    ax1.set_title(f'UpTempO Buoy Positions {objdate.month}/{objdate.day}/{objdate.year}',fontsize=20)
    
    # establish labels dictionary
    outlabs = {0: {'name':'Alaska',    'lon':-145, 'lat':67, 'rot1':0,   'col':'w'},
               1: {'name':'Russia',    'lon': 155, 'lat':69, 'rot1':0,   'col':'w'},
               2: {'name':'Greenland', 'lon': -50, 'lat':76, 'rot1':0,   'col':'w'},
               3: {'name':'85N',       'lon': 162, 'lat':86, 'rot1':-25, 'col':'dimgrey'},
               4: {'name':'80N',       'lon': 162, 'lat':81, 'rot1':-25, 'col':'dimgrey'},
               5: {'name':'75N',       'lon': 162, 'lat':76, 'rot1':-25, 'col':'dimgrey'},
               6: {'name':'90E',       'lon':  90, 'lat':84, 'rot1':0,   'col':'dimgrey'},
               7: {'name':'135E',      'lon': 141, 'lat':84, 'rot1':45,  'col':'dimgrey'},
               8: {'name':'180E',      'lon': 188, 'lat':83, 'rot1':90,  'col':'dimgrey'},
               9: {'name':'135W',      'lon':-124, 'lat':82, 'rot1':-45, 'col':'dimgrey'},
               10:{'name':'90W',       'lon': -90, 'lat':82, 'rot1':0,   'col':'dimgrey'}
              }    
    for i,o in enumerate(outlabs):
        if i <= 2: fs=14
        else: fs=11
        ax1.text(outlabs[i]['lon'],outlabs[i]['lat'],outlabs[i]['name'],rotation=outlabs[i]['rot1'],
                color=outlabs[i]['col'],fontsize=fs,transform=ccrs.PlateCarree())
    
    return ax1

def UpTempOAntarcticMap(strdate=None,nors='s',defaultPlot=False):

    if strdate == None:
        objdate = dt.datetime.now() - dt.timedelta(days=1)
        strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    else:
        objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    # establish contour levels and colors
    featcolors=['k','darkslateblue','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown']
    featbar=[-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,2.0,3.0,4.0,5.0]   # SST
    icecolors=['0.4','0.5','0.6','0.725','0.85','1.0']
    icelevels=[0.2,0.3,0.4,0.5,0.75]
    # else:
    #     featbar=[-30.,-20.,-10.,-5.,-1.,0.0,1.0,5.0,10.,20.,30.]  # for salinity

    if defaultPlot is False:
        # get satellite ice concentration data
        icedate, ice, icexx, iceyy = pfields.getICE(strdate,nors=nors)
        print('Date of ice map',icedate,ice.shape)
        # get satellite sst data
        sstdate, sst, sstlon, sstlat = pfields.getSST(strdate)
        print('Date of sst map',sstdate,sst.shape)    
    
    fig1, ax1 = plt.subplots(1,figsize=(5,5))
    ax1 = plt.subplot(1,1,1,projection=ccrs.SouthPolarStereo(central_longitude=0))
    ax1.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
    ax1.add_feature(cfeature.LAND,facecolor='gray')
    # ax1.add_feature(cfeature.OCEAN,facecolor='lightblue')
    ax1.coastlines(resolution='50m',linewidth=0.5,color='darkgray')
    kw = dict(central_latitude=-90, central_longitude=0, true_scale_latitude=71)
    # both of these set_extent commands work well
    # ax1.set_extent([-180,180,65,90],crs=ccrs.PlateCarree())
    ax1.set_extent([-3.0e6,3.3e6,-3e6,3e6],crs=ccrs.SouthPolarStereo(central_longitude=0))
    if defaultPlot is False:
        if sst is not None:
            ax1.contourf(sstlon, sstlat, sst, transform=ccrs.PlateCarree(),levels=featbar, colors=featcolors, extend='both')
        else:
            ax1.text(-10,74,'SST data unavailable',color='k',fontsize=10,transform=ccrs.PlateCarree())
    # # fig1.colorbar(ch)
        if ice is not None:
            ax1.contourf(icexx,iceyy,ice, colors=icecolors, levels=icelevels, vmin=0, vmax=0.9, extend='both',
                              transform=ccrs.Stereographic(**kw))   #use either colors or cmap
        else:
            ax1.text(10,88,'ICE data unavailable',color='k',fontsize=10,transform=ccrs.PlateCarree())
            # fig1.colorbar(ch)   
        ax1.set_title(f'UpTempO Buoy Positions {objdate.month}/{objdate.day}/{objdate.year}',fontsize=20)
    else:
        ax1.set_title('Currently No Buoys Deployed',fontsize=20)
        
    # # establish labels dictionary
    outlabs = {0: {'name':'Antarctica', 'lon':-145, 'lat':-87, 'rot1':0,   'col':'w'},
                1: {'name':'75S',       'lon': -44, 'lat':-75, 'rot1':35, 'col':'dimgrey'},
                2: {'name':'70S',       'lon': -44, 'lat':-70, 'rot1':35, 'col':'dimgrey'},
                3: {'name':'65S',       'lon': -44, 'lat':-65, 'rot1':35, 'col':'dimgrey'},
                4: {'name':'60S',       'lon': -44, 'lat':-60, 'rot1':35, 'col':'dimgrey'},
                5: {'name':'135W',      'lon':-134, 'lat':-60, 'rot1':45,   'col':'dimgrey'},
                6: {'name':'135E',      'lon': 142, 'lat':-60, 'rot1':-45,  'col':'dimgrey'},
                7: {'name':'180E',      'lon': 182, 'lat':-65, 'rot1':90,  'col':'dimgrey'},
              }    
    for i,o in enumerate(outlabs):
        # if i <= 4: fs=14
        # else: fs=11
        ax1.text(outlabs[i]['lon'],outlabs[i]['lat'],outlabs[i]['name'],rotation=outlabs[i]['rot1'],
                color=outlabs[i]['col'],fontsize=11,transform=ccrs.PlateCarree())
    
    return ax1

