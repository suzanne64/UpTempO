
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 12:36:50 2022

@author: suzanne
"""
import re, os
from polar_convert import polar_lonlat_to_xy, polar_lonlat_to_ij, polar_ij_to_lonlat
from polar_convert.constants import NORTH, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY
import numpy as np
import datetime as dt
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.spatial.distance import pdist
import pandas as pd
import UpTempO_BuoyMaster as BM


# L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
# L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'

icepath = '/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/NSIDC_ICE/north'
hemisphere = NORTH

def getL1(filename, bid):
    print('L1 file name:',filename)

    # baseheader ={'year':'Year',         # key from Level 1, value from ProcessedRaw and used here
    #              'month':'Month',
    #              'day':'Day',
    #              'hour':'Hour',
    #              'Latitude':'Lat',
    #              'Longitude':'Lon'}
    columns = ['Year','Month','Day','Hour','Lat','Lon']
        
    pdepths = []
    tdepths = []
    sdepths = []
    pcols = []
    pnum,tnum,snum = 1,0,0
    
    # convert Level 1 .dat to pandas dataFrame
    with open(filename,'r') as f:
        lines = f.readlines()
        for ii,line in enumerate(lines):
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
                    data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) 
                    print(data.shape,'after %END')
            else:
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii,len(lines))]) 
                print(data.shape,'in else')
                break
               
    df = pd.DataFrame(data=data,columns=columns)
    # print((df == -999).sum())
    # print((df == -99).sum())
    df[df==-999] = np.NaN
    df[df==-99] = np.NaN
    # drop a column if all values are NaN
    df.dropna(axis=1,how='all',inplace=True)
    # df.replace(-999,np.NaN)
    # df.replace(-99,np.NaN)
    if bid != '300534062158460' and bid != '300534062158480':    # these don't have pressures or depths
        df.insert(6,'P0',0.00)
    else: 
        df.insert(6,'P0',0.28)
    print(df.head())
    # print(df.isna().sum())
    # exit(-1)
    # add dates column for plotting
    df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        
    # implement data clean up (see weCode/LEVEL_2_IDL_CODE/READ_ME.txt)
    # remove duplicate lines
    #  if you want to look at duplicates for same Date, Lat and Lon
    # print(df[df.duplicated(['Dates','Lat','Lon'],keep=False)])
    # exit(-1)
    # dupes = df[df.duplicated(['Dates','Lat','Lon'],keep=False)]
    df.drop_duplicates(['Dates','Lat','Lon'],keep='last',inplace=True)  # like Wendy (see 2016-=06)
    df=df.reset_index(drop=True) 
        
    # sort by increasing date, over four cols
    df.sort_values(by=['Dates'],inplace=True)
    df=df.reset_index(drop=True)

    return df

def getL2(filename, bid):
    print('L2 file name:',filename)
    # get Level2 into dataFrame
    columns = ['Year','Month','Day','Hour','Lat','Lon']
    pdepths = []
    tdepths = []
    sdepths = []
    ddepths = []
    pcols = []
    pnum,tnum,snum,dnum = 1,0,0,0
    
    # binf = BM.BuoyMaster(bid)
    # print(binf)
        
    with open(filename,'r') as f:
        lines = f.readlines()
        for ii,line in enumerate(lines):
            if line.startswith('%'):
                if 'year' in line:
                    pass
                if 'Ocean Pressure (dB) at Sensor #' in line:
                    pcols.append( int(re.search(r'\% (.*?)= Ocean Pressure ',line).group(1).strip(' ')) )
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
                if 'Open Water or Ice Indicator' in line:
                    columns.append('WaterIce')
                if 'Calculated Depth at nominal depth' in line:
                    ddepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'D{dnum}') 
                    dnum += 1
                if 'First tpod in water' in line:
                    columns.append('FirstTpod')
            if line.strip('\n') == 'END':
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) #ii+1,len(lines)+1)]
                # only get columns that match Level1
                df = pd.DataFrame(data=data[:,:len(columns)],columns=columns)
                df[df==-999] = np.NaN
                df[df==-99] = np.NaN
                if bid != '300534062158460' and bid != '300534062158480':    # these don't have pressures or depths
                    df.insert(6,'P0',0.00)
                else: 
                    df.insert(6,'P0',0.28)
                # if pdepths:
                #     pdepths = np.array(pdepths)
                # if tdepths:
                #     tdepths = np.array(tdepths)
                # if sdepths:
                #     sdepths = np.array(sdepths)
                # if ddepths:
                #     ddepths = np.array(ddepths)

    df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])

    return df 

def plotL1vL2(df1,df2,bid,casestr=None):
    pathfigs = 'UPTEMPO/WebData/LEVEL1/figs'
    
    df1['datetime'] = pd.to_datetime(df1['Dates'])
    df1.set_index('datetime',inplace=True)
    df1.sort_index(inplace=True)
    print(df1.head()) #df1.drop('Dates')
    df2['datetime'] = pd.to_datetime(df2['Dates'])
    df2.set_index('datetime',inplace=True)
    df2.sort_index(inplace=True)
    print(df2.head()) #df2.drop('Dates')
    print()
    cols2plot = (df1.columns & df2.columns)
    print(len(cols2plot))

    for ii,col in enumerate(cols2plot):
        if ii>3:
            fig,ax = plt.subplots(1,1,figsize=(8,8))
            ax.plot(df1[col],'ro')
            ax.plot(df2[col],'b.')
            if col+'corr' in df1:
                ax.plot(df1[col+'corr'],'c.')
            ax.set_title(col,fontsize=20)
            plt.savefig(f'{pathfigs}/{bid}_{col}{casestr}.png',format='png')
            plt.show()
    # exit(-1)
#     # get columns for plotting
#     # Tcols = [col for col in df.columns if col.startswith('T')]
#     # Pcols = [col for col in df.columns if col.startswith('P')]
#     # Scols = [col for col in df.columns if col.startswith('S') and not col.startswith('SUB')]
    
#     print()
#     dfp = pd.DataFrame(columns=['t1','dTleft','dTright'])
#     dfp['t1'] = np.array([-2, -3, -0.5, 0.5, 0, -1.5,-2,-1])
#     dfp['dTleft'] = dfp['t1'].diff()
#     dfp['dTright']= dfp['t1'].diff().shift(-1).apply(lambda x: -1*x)  # neg of the gradient, shifted up by 1, so in same row as dTleft
        
#     dfp['samesign'] = np.where(dfp['dTleft'].apply(lambda x: np.sign(x)) == dfp['dTright'].apply(lambda x: np.sign(x)), True, False)
#     dfp['dTleftabs'] = dfp['dTleft'].abs()
#     dfp['dTrightabs']= dfp['dTright'].abs()
#     dfp['spike'] = dfp[['dTleftabs','dTrightabs']].min(axis=1)
#     print(dfp)
#     dfp['spike'].mask(~dfp['samesign'],inplace=True)   # mask says remove the True
#     print(dfp)

#     print()
#     # dfp['spike'] = dfp[(dfp['dTleft'].abs(), dfp['dTright'].abs())].min(axis=1)
#     print()
#     print(dfp)
#     # if signs are same, then we have a peak (both +) or a trough (both -)
#     # choose the dTdh with the lowest magnitude.
        
#     fig,ax= plt.subplots(1,1)
#     ax.plot(dfp['t1'],'ro-',markersize=1)
#     ax.grid()
#     plt.show()
#     exit(-1)
#     exit(-1)
# # let's plot!
 

def getBuoyIce(blon,blat,byear,bmonth,bday,sst,plott=0):
    delta = 45  # nsidc ice maps rotated -45degrees 
    grid_size = 25 #km
    bx,by = polar_lonlat_to_xy(blon+delta, blat, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY, hemisphere)
    bx *= 1000
    by *= 1000
    [bi,bj] = polar_lonlat_to_ij(blon, blat, grid_size, hemisphere)  #i is to x as y is to y and they do +delta    
    buoyloc = np.array([[bx,by]])
    
    # get ice map
    strdate = f'{int(byear)}{int(bmonth):02}{int(bday):02}'
    objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    if objdate < dt.datetime(2022,1,1):  # g02202(climate data record)
        icefile = f'{int(byear)}/seaice_conc_daily_nh_{strdate}_f17_v04r00.nc'
        ncdata=nc.Dataset(f'{icepath}/{icefile}')  
        ice=np.squeeze(ncdata['cdr_seaice_conc'])
        y=ncdata['ygrid'][:]
        x=ncdata['xgrid'][:]
        ice[ice==251] = np.nan  # pole_hole_mask, flags are not scaled
        icesrc = 'NSIDC-g02202'
    else:                                # 0081 (nrt/most recent)
        icefile = f'{int(byear)}/NSIDC0081_SEAICE_PS_N25km_{strdate}_v2.0.nc'
        ncdata=nc.Dataset(f'{icepath}/{icefile}')  
        # g_attdict = ncdata['crs'].__dict__
        # for k,v in g_attdict.items():
        #     print(k,v,type(v))
        # crs = ncdata['crs']
        # # print(crs)
        # true_scale_lat = crs.standard_parallel
        # Re = crs.semi_major_axis  # meters
        # e = float(re.search(r'degree",(.*?),AUTHORITY',crs.crs_wkt).group(1)) #eccentricity
        # print('flag meanings',ncdata.variables['F18_ICECON'].getncattr('flag_meanings'))
        # print('flag0 values',ncdata.variables['F18_ICECON'].getncattr('flag_values'))
        # print(ncdata['F18_ICECON'].shape)
        ice=np.squeeze(ncdata['F17_ICECON']).astype('float')  # np.squeeze converts nc dataset to np array
        y=ncdata['y'][:]
        x=ncdata['x'][:]
        icesrc = 'NSIDC-0081'
        # np.where(ice>1,np.nan,ice)
        # ice[ice==251.] = np.nan  # pole_hole_mask, flags are not scaled
        # ice[ice==252.] = np.nan  # unused
        # ice[ice==253.] = np.nan  # coast
        # ice[ice==254.] = np.nan  # land
        # ice[ice==255.] = np.nan  # missing data
    ice[ice>=250] = np.nan
 
    trim=10  # number cells in each direction for zooming in 
    ice200 = ice[:,np.arange(bi-trim,bi+trim)][np.arange(bj-trim,bj+trim),:]
    ice200wi = ice[:,np.arange(bi-trim,bi+trim)][np.arange(bj-trim,bj+trim),:]
    ice200wi[ice200wi>=0.15] = 1
    ice200wi[ice200wi<0.15]  = 2
    x200 = x[np.arange(bi-trim,bi+trim)]
    y200 = y[np.arange(bj-trim,bj+trim)]
    # if plott:
    #     extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
    #     fig0,ax0 = plt.subplots(1,1)
    #     ch0 = ax0.imshow(ice, extent=extent, cmap='turbo')
    #     ax0.plot(bx,by,'mo',markersize=5)
    #     ax0.set_xlim(-2.5e6,1.5e6)
    #     ax0.set_ylim(-1.5e6,2e6)
    #     ax0.set_title(f'IceConc from {icesrc} on {strdate}',fontsize=12)
    #     fig0.colorbar(ch0)
        
    #     extent200=[np.min(x200),np.max(x200),np.min(y200),np.max(y200)]
    #     fig1,ax1 = plt.subplots(1,1)
    #     ch1 = ax1.imshow(ice200wi, extent=extent200)
    #     ax1.plot(bx,by,'mo',markersize=5)
    #     ax1.set_title(f'Ice(1), Water(2), buoy at {blon:.1f}W, {blat:.1f}N, SST={sst:.1f}C')
    #     fig1.colorbar(ch1)

    icexx = np.repeat(x200.reshape(1,-1),len(y200),axis=0)
    iceyy = np.repeat(y200.reshape(-1,1),len(x200),axis=1)
 
    # if plott:
    #     fig2,ax2 = plt.subplots(2,2)
    #     chi = ax2[0,0].imshow(ice200,vmin=0, vmax=1, origin='upper',extent=extent200)
    #     fig2.colorbar(chi,ax=ax2[0,0])
    #     ax2[0,0].plot(bx,by,'ro',markersize=5)
        
    #     chx = ax2[1,0].imshow(icexx,origin='upper',extent=extent200)
    #     ax2[1,0].plot(bx,by,'ro',markersize=5)
    #     fig2.colorbar(chx,ax=ax2[1,0])
        
    #     chy = ax2[1,1].imshow(iceyy,origin='upper',extent=extent200)
    #     ax2[1,1].plot(bx,by,'ro',markersize=5)
    #     fig2.colorbar(chy,ax=ax2[1,1])
    
    # get distances from buoy
    icexxd = icexx.reshape(-1,1)
    iceyyd = iceyy.reshape(-1,1)
    icelocs = np.concatenate((icexxd,iceyyd),axis=1)

    alldists = np.concatenate( (buoyloc,icelocs), axis=0 )
    dist1 = pdist(alldists) # pdist calcs dists between all locs, first icexx.shape are with buoyloc
    dist1 = dist1[:icexxd.shape[0]].reshape((len(y200),len(x200)))
    # if plott:
    #     chd = ax1.contour(x200,y200,dist1/1000,levels=np.arange(0,250,25)) #,origin='upper',extent=extent200)
    #     chd.clabel(inline=True) #, chd.levels, inline=True,fontsize=10

        # chd = ax2[0,1].contour(x200,y200,dist1/1000,levels=np.arange(0,250,25)) #,origin='upper',extent=extent200)
        # ax2[0,1].plot(bx,by,'ro',markersize=5)
        # chd.clabel(inline=True) #, chd.levels, inline=True,fontsize=10
        # # fig2.colorbar(chd,ax=ax2[0,1])
        # print('distance map shape',dist1.shape,ice.shape)
    
    icemask = ice[:,np.arange(bi-trim,bi+trim)][np.arange(bj-trim,bj+trim),:]
    # icemask[icemask>200] = 5
    icemask[np.logical_and(icemask>=0.15,icemask<=1)] = 1
    icemask[icemask<0.15] = 0
    
    dist2 = dist1
    dist2[icemask==0] = np.nan  # open water
    mindist = np.nanmin(dist2)

    if np.isnan(mindist) and plott:
        extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
        fig0,ax0 = plt.subplots(1,1)
        ch0 = ax0.imshow(ice, extent=extent, cmap='turbo')
        ax0.plot(bx,by,'mo',markersize=5)
        ax0.set_xlim(-2.5e6,1.5e6)
        ax0.set_ylim(-1.5e6,2e6)
        ax0.set_title(f'IceConc from {icesrc} on {strdate}',fontsize=12)
        fig0.colorbar(ch0)
        
        extent200=[np.min(x200),np.max(x200),np.min(y200),np.max(y200)]
        fig1,ax1 = plt.subplots(1,1)
        ch1 = ax1.imshow(ice200wi, extent=extent200)
        ax1.plot(bx,by,'mo',markersize=5)
        ax1.set_title(f'Ice(1), Water(2), buoy at {blon:.1f}W, {blat:.1f}N, SST={sst:.1f}C')
        fig1.colorbar(ch1)
        chd = ax1.contour(x200,y200,dist1/1000,levels=np.arange(0,250,25)) 
        chd.clabel(inline=True) 

        plt.show()
        exit(-1)
    
    # if plott:
        # indd = np.argwhere(dist2==mindist)
        # ax1.plot(x200[indd[0,1]],y200[indd[0,0]],'mx',markersize=5)
        # plt.show()
        # exit(-1)
    indicator = 1
    if mindist/1000 > 35.4 or np.isnan(mindist):  # see http://psc.apl.washington.edu/UpTempO/Level2_QC_doc.php
        indicator = 2
    elif mindist/1000 > 17.7 and mindist/1000 <=34.5:
        if sst > -1.2:
            indicator = 2
    # print(f'min dist to ice {mindist/1000:.1f}km, sst={sst:.2f}C, ind={indicator}')

    return indicator, mindist


def getOPbias(pcol,pdepth,df,bid,figspath):
    binf = BM.BuoyMaster(bid)
    
    global coords
    coords=[]
    def onpick(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        # get the index of the point that was picked (clicked on)    
        ind = event.ind
        xd, yd = xdata[ind], ydata[ind]
        
        global coords
        coords.append([xd[0],yd[0]]) # take first, incase 'radius=3' grabs a couple of points
        print('coords ',coords)
        
        # draw it
        ax5.plot(xdata[ind],ydata[ind],'ro')
        event.canvas.draw()
        
        # disconnect after two clicks (per nominal ocean depth)
        num_markers = 2
        if np.mod(len(coords),num_markers) == 0:
            fig5.canvas.mpl_disconnect(cid)
            plt.close()
            
        return 
        
    # plot pressures to find bias        
    fig5,ax5 = plt.subplots(1,1,figsize=(25,5))
    cid = fig5.canvas.mpl_connect('pick_event', onpick)
    ax5.plot(df['Dates'],-1*df[pcol],'b.-',linewidth=1,picker=True,pickradius=1)  # actual L1 depths
    dt0 = dt.datetime(np.int(df['Year'].iloc[0]),np.int(df['Month'].iloc[0]),np.int(df['Day'].iloc[0]))
    ax5.set_xlim([dt0,dt0+dt.timedelta(days=30)])
    ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax5.set_title(f'First month of Ocean Pressure for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}, at nominal depth of {pdepth:.0f}m.',wrap=True,fontsize=20)
    ax5.grid()
    plt.show()
    fig5.savefig(f'{figspath}/OPbiasDetermination_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    plt.close()
    # OPbias1 = dfdaily[(dfdaily['Dates']>=coords[0][0]) & (dfdaily['Dates']<=coords[1][0])][pcol+'medians'].mean() - pdepth
    OPbias = df.loc[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]),pcol].median() - pdepth
    # OPbias3 = df[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0])][pcol].mode() - pdepth
    print('bias from median of L1 pressures btn two clicks',OPbias)
    # minP = df[ (df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]) & (df[pcol]>25)]
    # minP = df[ df[pcol]>25]
    # OPbias = pdepth - meanOPbias[pcol]
    df[pcol+'corr'] = df[pcol] - OPbias
    print(df.head(20))
    # exit(-1)
    # print(f'Ocean Pressure bias of {OPbias:.2f}m at {pdepth}m.')
    # fig5,ax5 = plt.subplots(1,1,figsize=(15,5))
    # ax5.plot(df['Dates'],-1*df[pcol],'g.',linewidth=1)  # actual depths
    # # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r',linewidth=1)   # corrected depths
    # # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r',linewidth=1)   # corrected depths
    # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r.',linewidth=1)   # corrected depths
    # ax5.set_title('P1 L1: (green), L1 corr (red)',fontsize=20)
    # # ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'max'],'gx-')          # min of the daily depths (max if + depths)
    # # line, = ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'medians'],'b+-',picker=True,pickradius=3) # making medians pickable
    # ax5.grid()
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-pdepth-OPbias,-pdepth-OPbias],'r--')
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-pdepth- -0.27,-pdepth- -0.27],'b--')

    # plt.show()
    # exit(-1)

    # def annotate(ax,text,x,y):
    #     text_annotation = Annotation(text,xy=(x,y),xycoords='data')
    #     ax.add_artist(text_annotation)

    return df, OPbias

def getRidgeDates(pcol,df): #pcol,pdepth,df,bid,figspath):
    # binf = BM.BuoyMaster(bid)
    
    global coords
    coords=[]
    def onpick(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        # get the index of the point that was picked (clicked on)    
        ind = event.ind
        xd, yd = xdata[ind], ydata[ind]
        
        global coords
        coords.append([xd[0],yd[0]]) # take first, incase 'radius=3' grabs a couple of points
        print('coords ',coords)
        
        # draw it
        ax5.plot(xdata[ind],ydata[ind],'ro')
        event.canvas.draw()
        
        # disconnect after two clicks (per nominal ocean depth)
        num_markers = 2
        if np.mod(len(coords),num_markers) == 0:
            fig5.canvas.mpl_disconnect(cid)
            plt.close()
            
        return 
        
    # make dataFrame to store daily values
    # columnsdaily = [pcol+'medians' for pcol in Pcols if pcol != 'P0']
    # columns = [pcol+'max',pcol+'medians']
    # dfdaily = pd.DataFrame(columns = columns)

    # following Wendy's FineTuneOPbias subroutine in QC_FUNCTIONS_UPTEMPO.pro
    # print(pdepth,pcol)
    # print()
    # print()
    # print(df.loc[df[pcol]>25,['Dates',pcol]])
    # meanOPbias = df.loc[df[pcol]>25,[pcol]].mean()
    # modeOPbias = df.loc[df[pcol]>25,[pcol]].mode()
    # print(f"mean depths of those greater than {pdepth} = \n{meanOPbias[pcol]}")
    # print(f"mode of depths greater than {pdepth} = \n{modeOPbias[pcol][0]}")
    # make daily dataframe
    # dfdaily['Dates'] = df.groupby(pd.Grouper(key='Dates',freq='D'))['Dates'].min().dt.floor('D') # this col needed for plotting
    # # find max depth each day
    # dfdaily[pcol+'max'] = df.groupby(pd.Grouper(key='Dates',freq='D'))[pcol].max()  # deepest
    # # compute running median of max depths
    # dfdaily[pcol+'medians'] = df.groupby(pd.Grouper(key='Dates',freq='D'))[pcol].max().rolling(7,center=True).median()
    # print(dfdaily.head())
    # exit(-1)
    # plot pressures to find bias        
    fig5,ax5 = plt.subplots(1,1,figsize=(25,5))
    cid = fig5.canvas.mpl_connect('pick_event', onpick)
    ax5.plot(df['Dates'],-1*df[pcol],'b.-',linewidth=1,picker=True,pickradius=1)  # actual L1 depths
    dt0 = dt.datetime(np.int(df['Year'].iloc[0]),np.int(df['Month'].iloc[0]),np.int(df['Day'].iloc[0]))
    # ax5.set_xlim([dt0,dt0+dt.timedelta(days=30)])
    ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax5.xaxis.set_major_formatter()
    # ax5.set_title(f'Ocean Pressure for buoy {binf["name"][0]}-{int(binf["name"][1]):02d}, at nominal depth of {pdepth:.0f}m.',wrap=True,fontsize=20)
    ax5.grid()
    plt.show()
    # fig5.savefig(f'{figspath}/OPbiasDetermination_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    # plt.close()
    # exit(-1)
    # print('daily', dfdaily.head())
    # print('GDI',coords[0][0],coords[1][0])
    # calculate OP bias = mean(median pressures) between two dates clicked on plot MINUS nominal depth which = positive value
    # print()
    # # OPbias1 = dfdaily[(dfdaily['Dates']>=coords[0][0]) & (dfdaily['Dates']<=coords[1][0])][pcol+'medians'].mean() - pdepth
    # OPbias = df[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0])][pcol].median() - pdepth
    # # OPbias3 = df[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0])][pcol].mode() - pdepth
    # print('bias from median of L1 pressures btn two clicks',OPbias)
    # # exit(-1)
    # # minP = df[ (df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]) & (df[pcol]>25)]
    # # minP = df[ df[pcol]>25]
    # # OPbias = pdepth - meanOPbias[pcol]
    # df[pcol+'corr'] = df[pcol] - OPbias
    # print(df.head(20))
    # exit(-1)
    # print(f'Ocean Pressure bias of {OPbias:.2f}m at {pdepth}m.')
    # fig5,ax5 = plt.subplots(1,1,figsize=(15,5))
    # ax5.plot(df['Dates'],-1*df[pcol],'g.',linewidth=1)  # actual depths
    # # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r',linewidth=1)   # corrected depths
    # # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r',linewidth=1)   # corrected depths
    # ax5.plot(df['Dates'],-1*df[pcol+'corr'],'r.',linewidth=1)   # corrected depths
    # ax5.set_title('P1 L1: (green), L1 corr (red)',fontsize=20)
    # # ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'max'],'gx-')          # min of the daily depths (max if + depths)
    # # line, = ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'medians'],'b+-',picker=True,pickradius=3) # making medians pickable
    # ax5.grid()
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-pdepth-OPbias,-pdepth-OPbias],'r--')
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-pdepth- -0.27,-pdepth- -0.27],'b--')

    # plt.show()
    # exit(-1)

    # def annotate(ax,text,x,y):
    #     text_annotation = Annotation(text,xy=(x,y),xycoords='data')
    #     ax.add_artist(text_annotation)

    return #df, OPbias

def getRidging(pcol,pdepth,df,bid,figspath):
    binf = BM.BuoyMaster(bid)
    df['ridging'] = 0
    global coords
    coords=[]
    def onpick(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        # get the index of the point that was picked (clicked on)    
        ind = event.ind
        xd, yd = xdata[ind], ydata[ind]
        
        global coords
        coords.append([xd[0],yd[0]]) # take first, incase 'radius=3' grabs a couple of points
        print('coords ',coords)
        
        # draw it
        ax5.plot(xdata[ind],ydata[ind],'ro')
        event.canvas.draw()
        
        # disconnect after two clicks (per nominal ocean depth)
        num_markers = 2
        if np.mod(len(coords),num_markers) == 0:
            fig5.canvas.mpl_disconnect(cid)
            plt.close()
            
        return 
        
    # plot pressures to find ridging      
    fig5,ax5 = plt.subplots(1,1,figsize=(25,5))
    cid = fig5.canvas.mpl_connect('pick_event', onpick)
    ax5.plot(df['Dates'],-1*df[pcol],'b.-',linewidth=1,picker=True,pickradius=1)  # actual L1 depths
    ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-1*meanOPbias[pcol],-1*meanOPbias[pcol]],'b',linewidth=1)  # actual depths
    # ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-25.27,-25.27],'r',linewidth=1)  # actual depths
    # ax5.set_ylim([])
    ax5.set_title(f'Ocean Pressure for buoy {binf["name"][0]}-{int(binf["name"][1]):0d}, at nominal depth of {pdepth:.0f}m.',wrap=True,fontsize=20)
    ax5.grid()
    # print(df[pcol].max())
    # plt.show()
    # exit(-1)
    # ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'max'],'gx-')          # deepest of the daily depths (max if + depths)
    # ax5.plot(dfdaily['Dates'],-1*dfdaily[pcol+'medians'],'r+-',picker=True,pickradius=3) # making medians pickable
    # plt.show()
    fig5.savefig(f'{figspath}/RidgingDetermination_{binf["name"][0]}-{int(binf["name"][1]):02d}.png')
    plt.show()
    plt.close()
    # set ridging to 1 if between two clicks and shallower than OPlimit
    fig6,ax6 = plt.subplots(1,1,figsize=(25,5))
    ax6.plot(df['Dates'],-1*df[pcol],'b.-')
    ax6.set_xlim([coords[0][0]-20, coords[1][0]+20])
    ax6.set_grid()
    plt.show()
    OPlimit = input('What is the deepest pressure for this ridging? ')
    df.loc[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]) & (df[pcol]<np.float(OPlimit)),'ridging'] = 1
    # find FWT for the this ridging
    # minP = df[ (df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]) & (df[pcol]>25)]
    # minP = df[ df[pcol]>25]
    # OPbias = pdepth - meanOPbias[pcol]
    # def annotate(ax,text,x,y):
    #     text_annotation = Annotation(text,xy=(x,y),xycoords='data')
    #     ax.add_artist(text_annotation)

    return df



def removeSpikes(df1,tdepths):
    # get columns that might need spike removal
    Tcols = [col for col in df1.columns if col.startswith('T')]
    Pcols = [col for col in df1.columns if col.startswith('P')]
    Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
    Dcols = [col for col in df1.columns if col.startswith('D') and not col.startswith('Da')]
    
    df1['datetime'] = pd.to_datetime(df1['Dates'])
    df1.set_index('datetime',inplace=True)
    df1.sort_index(inplace=True)
    # df1.drop(columns=['Dates'],inplace=True)
    
    for ii,col in enumerate(zip(Tcols,Dcols)):
        print()
        print(ii,col[0],col[1])
        if ii>=1:
            df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))
            # df1['dhbackfilll'] = df1['dh'].fillna(method='backfill')
            df1['dTdhL'] = df1[col[0]].diff() / df1['dh']
            df1['dTdhLsign'] = df1['dTdhL'].apply(lambda x: np.sign(x))
            df1['dTdhLsign'].replace(0,np.nan,inplace=True)
            # neg of the gradient, shifted up by 1, so in same row as dTleft and the spiked T
            df1['dTdhR']= df1[col[0]].diff().shift(-1).apply(lambda x: -1*x) / df1['dh'].replace(0,np.nan)
            df1['dTdhRsign'] = df1['dTdhR'].apply(lambda x: np.sign(x))
            df1['dTdhRsign'].replace(0,np.nan,inplace=True)
            
            df1['samesign'] = np.where(df1['dTdhLsign'] == df1['dTdhRsign'], True, False) # does not inclued two nans
            # df1['dTdhLabs'] = df1['dTdhL'].abs()
            # df1['dTdhRabs'] = df1['dTdhR'].abs()
            df1['spike'] = df1[['dTdhL','dTdhR']].abs().min(axis=1).mul(df1['dTdhLsign'])
            df1.drop(columns=['dTdhL','dTdhR','dTdhLsign','dTdhRsign'],inplace=True)
            # df1['spike'] = df1[[df1['dTdhL'].abs(),df1['dTdhR'].abs()].min(axis=1)]
            df1['spike'].mask(~df1['samesign'],inplace=True)   # mask says remove the True
            # print(df1.iloc[120:140,:])
            

            # OF NON SPIKE POINTS
            df1[col[0]+'within3m']= df1.loc[(df1[col[1]]>tdepths[ii]-3) & (df1[col[1]]<=tdepths[ii]+3) & (df1['samesign']),col[0]]
            df1[col[0]+'minRwithin3m']= df1.loc[(df1[col[1]]>tdepths[ii]-3) & (df1[col[1]]<=tdepths[ii]+3),col[0]].rolling('2D',center=True).min()
            df1[col[0]+'maxRwithin3m']= df1.loc[(df1[col[1]]>tdepths[ii]-3) & (df1[col[1]]<=tdepths[ii]+3),col[0]].rolling('2D',center=True).max()
            
            df1[col[0]+'minR'] = df1[col[0]].rolling('2D',center=True).min()
            df1[col[0]+'maxR'] = df1[col[0]].rolling('2D',center=True).max()
            print(df1.iloc[120:140, [df1.columns.get_loc(c) for c in ['T1','T1minR','T1maxR','D1','samesign','T1within3m','T1minRwithin3m','T1maxRwithin3m']]])
            fig1,ax1 = plt.subplots(2,1,figsize=(15,10))
            ax1[0].plot(df1['T1'],'g')
            ax1[0].plot(df1['T1within3m'],'m--')
            ax1[0].plot(df1['T1minR'],'b')
            ax1[0].plot(df1['T1maxR'],'r')
            ax1[1].plot(df1['D1'].mul(-1))
            
            plt.show()
            
            ###########
            # print('what up')
            # print(df1.loc[(df1[col[1]]>tdepths[ii]-3) & (df1[col[1]]<tdepths[ii]+3),col[0]].mean())
            # # print(df1.iloc[120:140,:])
            # print()
            # exit(-1)
            # # print(df1[~df[tcol+'max'],tcol+'max'].isnull())
            # print()
            # only looking at day = 2 data
            # print(df1[df1.index.day ==2])
            # print(df1['2018-12-04'])
            # print(df1['2018-12-04':'2018-12-06])  # range
            
            # print(df1[tcol].resample('2D').min())
            # fig,ax = plt.subplots(1,1)
            # # ax.plot(df1['Dates'],'r.-',markersize=1)
            # ax[1].plot(np.arange(1,12),df1['dTdhLeft'].iloc[1:12],'b+-')
            # ax[1].plot(np.arange(1,12),df1['dTdhRight'].iloc[2:13],'kx-')
            # ax[1].plot(df1[tcol].resample('2D').min(),'g')
            # ax[1].plot(df1[tcol].resample('2D').max(),'g')
            # # ax[1].plot([0,14],[0,0])
            # plt.show()
            # exit(-1)
            # df1['dTleft/dh'] = df1[tcol].diff() / df1['dh']
            # df1['dTright/dh']= df1[tcol].diff().apply(lambda x: -1*x) / df1['dh']
            # print(df1.head(20))
            # exit(-1)
            
            
            # fig,ax1 = plt.subplots(1,1,figsize=(20,10))
            # ax2 = ax1.twinx()
            # ax1.plot(df1[col[0]],'k',markersize=1)
            # ax2.plot(df1.loc[df1['spike']>0,'spike'],'r.-',markersize=0.5)  # this is either 0 or 1. 
            # ax2.plot(df1.loc[df1['spike']<0,'spike'],'b.-',markersize=0.5)  # this is either 0 or 1. 
            # ax1.plot(df1[col[0]+'minR'],'g--')
            # ax1.plot(df1[col[0]+'maxR'],'g--')
            # # ax2.plot(df1[tcol].resample('2D').max()-df1[tcol].resample('2D').min(),'r',markersize=1)
            # ax2.plot(df1[col[0]+'maxR'].sub(df1[col[0]+'minR']),'r',markersize=1)
            
            # ax.plot(df[tcol],'b--')
            # ax1.set_xlabel('Dates of Data')
            # ax1.set_ylabel('Temperature, degC')
            # ax2.set_ylabel('Spikes, dT/dhour')
            # ax1.set_title(f'{col[0]}',fontsize=16)
            # plt.show()
    exit(-1)
    return df1




