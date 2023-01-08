
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
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.spatial.distance import pdist
from scipy.interpolate import interp2d, griddata
import UpTempO_BuoyMaster as BM
import statistics

# L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
# L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'

icepath = '/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/NSIDC_ICE/north'
hemisphere = NORTH
icecolors=['dimgray','gray','darkgray','lightgray','aliceblue','powderblue']
icelevels=[0.2,0.3,0.4,0.5,0.75]

def getL1(filename, bid, figspath):
    print('L1 file name:',filename)
    # baseheader ={'year':'Year',         # key from Level 1, value from ProcessedRaw and used here
    #              'month':'Month',
    #              'day':'Day',
    #              'hour':'Hour',
    #              'Latitude':'Lat',
    #              'Longitude':'Lon'}
    columns = ['Year','Month','Day','Hour','Lat','Lon']
    colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    pdepths = []
    tdepths = []
    sdepths = []
    ddepths = []
    # pcols = []
    pnum,tnum,snum,dnum = 1,0,0,0

    # convert Level 1 .dat to pandas dataFrame
    with open(filename,'r') as f:
        lines = f.readlines()
        for ii,line in enumerate(lines):
            if line.startswith('%'):
                if 'DATE DEPLOYED' in line:
                    depdate = dt.datetime.strptime(line.partition(':')[-1].strip(' ').strip('\n'),'%m/%d/%Y')
                if 'year' in line:
                    pass
                if 'Pressure' in line and not 'Sea Level' in line:
                    # pcols.append( int(re.search(r'\% (.*?)= Ocean Pressure',line).group(1).strip(' ')) )
                    columns.append(f'P{pnum}')
                    pnum += 1
                    pdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ') ))

                if 'Temperature' in line and not 'Air' in line:
                    tdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'T{tnum}')
                    tnum += 1

                if 'Salinity' in line and not 'Temperature at Salinity Sensor' in line:
                    sdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'S{snum}')
                    snum += 1

                if 'Estimated depth at nominal' in line:
                    ddepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'Dest{dnum}')
                    dnum += 1

                if 'Sea Level Pressure' in line:
                    columns.append('BP')
                if 'Air Temperature' in line:
                    columns.append('Ta')
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

    print(columns)
    print('tdepths',tdepths)
    print()
    # exit(-1)
    df = pd.DataFrame(data=data,columns=columns)
    print(df.columns)
    print(df.head(40))
    print()
    print(df['Year'])
    # exit(-1)
    if bid in ['300234066712490','300234064739080']:  # need to sort T cols by depths
        origcols = df.columns.to_list()
        print('originals ',origcols)
        newcols = origcols[:6] # time and loc
        newcolnames = origcols[:6] # time and loc
        newcols.extend([col for col in origcols if col.startswith('P')])
        newcolnames.extend([col for col in origcols if col.startswith('P')])

        Tdict={}
        tcols = [col for col in df.columns if col.startswith('T')]
        for tdepth,tcol in zip(tdepths,tcols):
            Tdict[tcol] = tdepth
        Tdict = dict(sorted(Tdict.items(), key=lambda item:item[1]))
        newcols.extend(Tdict.keys())
        newcols.extend([col for col in origcols if col.startswith('S')])
        newcols.extend(['BATT'])
        newcolnames.extend([f'T{n}' for n in range(len(tcols))])
        newcolnames.extend([col for col in origcols if col.startswith('S')])
        newcolnames.extend(['BATT'])
        # rearrange the df
        df = df[newcols]
        # rename the temperature columns
        df.rename(columns=dict(zip(newcols,newcolnames)), inplace=True)
        print(df.columns)
        print()
        print(df.head())
        tdepths.sort()
        print(tdepths)
        
    # print((df == -999).sum())
    # print((df == -99).sum())
    df[df==-999] = np.NaN
    df[df==-99] = np.NaN
    # drop a column if all values are NaN
    df.dropna(axis=1,how='all',inplace=True)

    # add dates column for plotting
    df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
    print('first date before:', df['Dates'].iloc[0])
    # remove data before deployment date
    df = df[(df['Dates']>=depdate)]
    print('first date after removing those before deployment date:',df['Dates'].iloc[0])

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

    print(df.columns)
    pcols = [col for col in df.columns if col.startswith('P') and not col.endswith('0')]
    tcols = [col for col in df.columns if col.startswith('T')]
    scols = [col for col in df.columns if col.startswith('S') and 'SUB' not in col]
    dcols = [col for col in df.columns if col.startswith('D') and not col.startswith('Da')]
    print(dcols)
    # exit(-1)
    
    # invalidate locs if they are obviously erroneous
    if '300234065419120' in bid:  # 2017 05
        df.loc[(df['Lat']< 72.5) & (df['Lon']>-153) & (df['Lon']<-152.5),['Lat','Lon']] = np.NaN  # removes 1 point
        # interpolate (linearly) to fill
        df['Lat'].interpolate(inplace=True)
        df['Lon'].interpolate(inplace=True)

    # invalidate Px zero values (not including P0) and other pressure edits depending...
    for ii,pcol in enumerate(pcols):
        df.loc[df[pcol]==0,pcol] = np.nan
        if bid in ['300234063991680']:
            m = ((df[pcol] < pdepths[ii]-5) | (df[pcol] > pdepths[ii]+5))
            df[pcol][m] = np.nan
        if bid in ['300234064737080']:
            m = ((df[pcol] < pdepths[ii]-50) | (df[pcol] > pdepths[ii]+50))
            df[pcol][m] = np.nan
            df.loc[(df['P1']>30),'P1'] = np.NaN
        if bid in ['300234065419120']:  # 2017-05
            m = ((df[pcol] > pdepths[ii]+4))
            df[pcol][m] = np.nan

    # temperature data editing
    if '300234063991680' in bid:  # 2016 07
        # Drop first row, where temps have not stablized yet
        df.drop(index=df.index[0],axis=0,inplace=True)
        df.reset_index(inplace=True)
        # remove bad subsurface temps
        for tcol in tcols:
            if 'T0' not in tcol:
                m = ((df['Dates']<=dt.datetime(2016,9,5,21,0,0)) | (df['Dates']>=dt.datetime(2016,10,20)))
                df[tcol][m] = np.NaN

    if '300234062491420' in bid:  # 2016 04 
        for tcol in tcols:
            if 'T0' in tcol:
                df.loc[df['Dates']>dt.datetime(2018,11,5,18,0,0),tcol] = np.NaN
            if 'T0' not in tcol:
                df.loc[df[tcol]>6,tcol] = np.NaN

    # correct wrapped temperatures
    if '300234064737080' in bid:  # 2017 04  !!!!!!! ADD bid to WrapCorr list in LEVEL_QC.py
        #True Temperature = reported value - maximum allowed value - minimum allowed value  Wrapped Temps
        maxValue = 62
        minValue = -20
        df.loc[(df['T0']>40),'T0'] -= (maxValue - minValue)
        # remove erroneous
        df.loc[(df['Dates']<dt.datetime(2017,11,25))  & (df['T0']<-12),'T0'] = np.NaN
        
    if '300234064739080' in bid:  # 2017 W6 
        #True Temperature = reported value - maximum allowed value - minimum allowed value  Wrapped Temps
        maxValue = 36
        minValue = -5
        df.loc[(df['T0']>10) & ((df['Dates']< dt.datetime(2017,5,25)) | (df['Dates']>dt.datetime(2017,12,1))),'T0'] -= (maxValue - minValue)
       # # remove erroneous
       # df.loc[(df['Dates']<dt.datetime(2017,11,25)) & (df['T0']<-12),'T0'] = np.NaN
        df.loc[(df['Dates']<dt.datetime(2017,3,9,6,0,0)),tcols] = np.nan
        df.loc[(df['Dates']<dt.datetime(2017,3,9,4,0,0)),'S0'] = np.nan
        df.loc[(df['Dates']>dt.datetime(2017,3,11)) & 
               (df['Dates']<dt.datetime(2017,3,12)) &
               (df['S0']<27.4),'S0'] = np.nan

    if '300234067936870' in bid:  # 2019 W-9
        df = df.loc[(df['Dates']>=dt.datetime(2019,4,2,0,0,0))]
        df.reset_index(inplace=True)
        df.loc[(df['P1']< 8),'P1'] = np.nan
        print(df['T0'].max())
        print(df['T0'].min())
        maxValue = 36
        minValue = -5
        df.loc[(df['T0']>14),'T0'] -= (maxValue - minValue)
        df.loc[(df['Dates']>dt.datetime(2019,4,30)) & (df['T0']<-20),'T0'] = np.nan

    if '300234060320940' in bid:  # 2019 05
        for pcol in pcols:
            df.loc[(df[pcol]<0),pcol] = np.nan
        # correct depths for sea level pressure variations    
        pcolsSLP = [f'{col}SLP' for col in pcols]
        for ii,pco in enumerate(zip(pcolsSLP,pcols)):
            fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
            df[pco[0]] = np.NaN
            df.loc[~np.isnan(df['BP']),pco[0]] = df.loc[~np.isnan(df['BP']),pco[1]] - (df.loc[~np.isnan(df['BP']),'BP'] - 1013)*0.01
            ax8.plot(df['Dates'],-1*df[pco[0]],'.')
            ax8.set_title(f'Ocean Pressure: original corrected for SLP with BP data, {pdepths[ii]}')
            ax8.grid()
            plt.savefig(f'{figspath}/OPcorrectedSLP_{pdepths[ii]}.png')
        plt.show()
        df.drop(columns=pcolsSLP,inplace=True)

    # set unseasonably warm temperatures to invalid
    for tcol in tcols:
        df.loc[(df[tcol]>20),tcol] = np.nan
        df.loc[((df['Month']>=10) | (df['Month']<=5)) & (df[tcol]>6), tcol] = np.nan
        
    # set out of range submergence values to invalid
    if 'SUB' in df.columns:
        subcount = df['SUB'].value_counts()
        if 100.0 not in subcount or subcount[1.0] > subcount[100.0]:
            df['SUB'] *= 100.
        df.loc[(df['SUB']<0.),'SUB'] = np.NaN
        df.loc[(df['SUB']>100.),'SUB'] = np.NaN   # WHY CAN'T I DO OR???   gdi

    print('pdepths',pdepths)
    print('tdepths',tdepths)
    print('sdepths',sdepths)
    print()

    plotL1 = input('Do you want to plot L1 data to check ranges? : y for Yes, n for No ')
    binf = BM.BuoyMaster(bid)

    remcols = []
    if plotL1.startswith('y'):
        for col in df.columns:

            fig,ax = plt.subplots(1,1,figsize=(15,5))
            # if (col.startswith('D') or col.startswith('P')) and 'Da' not in col:
            if col.startswith('P'):
                ax.plot(df['Dates'],-1*df[col],'.')
            elif 'Lat' in col:
                # if #bid in ['300234064737080','300234065419120']:
                df.loc[(df['Lon'])<0,'Lon'] += 360
                ax.plot(df['Lon'],df[col],'.')
                ax.plot(df['Lon'].iloc[0],df[col].iloc[0],'go')
                ax.plot(df['Lon'].iloc[-1],df[col].iloc[-1],'ro')
            elif 'Lon' in col:
                remcols.append(col)
            elif 'T0' in col:
            # elif col.startswith('T'):                
                for ii,tcol in enumerate(tcols):
                    # fig,ax = plt.subplots(1,1,figsize=(15,5))
                    ax.plot(df['Dates'],df[tcol],'o',color=colorList[ii],ms=1)
                    # ax.set_title(tcol)
                    # plt.show()
                    # ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
            elif 'Dest0' in col:
                for ii,dcol in enumerate(dcols):
                    print(ii,dcol)
                    ax.plot(df['Dates'],-1*df[dcol],'o',color=colorList[ii],ms=1)
                    # ax.set_title(tcol)
                    # plt.show()
                    # ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
            elif col.startswith('T') and 'T0' not in col:
                remcols.append(col)
            elif col.startswith('Dest') and 'Dest0' not in col:
                remcols.append(col)
            else:
                ax.plot(df['Dates'],df[col],'.')
            if 'Year' in col:
                try:
                    ax.set_title(f'Level 1 {binf["name"][0]}-{int(binf["name"][1]):02d} {col}, Number of Data {len(df)}')
                except:
                    ax.set_title(f'Level 1 {binf["name"][0]}-{binf["name"][1]} {col}, Number of Data {len(df)}')
            else:
                try:
                    ax.set_title(f'Level 1 {binf["name"][0]}-{int(binf["name"][1]):02d} {col}')
                except:
                    ax.set_title(f'Level 1 {binf["name"][0]}-{binf["name"][1]} {col}')
            ax.grid()
            try:
                plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}.png')
            except:
                plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{binf["name"][1]}_{col}.png')
            plt.show()

    for col in remcols:
        try:
            os.remove(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}.png')
        except:
            os.remove(f'{figspath}/L1_{binf["name"][0]}_{binf["name"][1]}_{col}.png')

    return df,pdepths,tdepths,sdepths

def getL2(filename, bid):
    print('L2 file name:',filename)
    # get Level2 into dataFrame
    columns = ['Year','Month','Day','Hour','Lat','Lon']
    pdepths = []
    tdepths = []
    sdepths = []
    ddepths = []
    biodepths = []
    pcols = []
    pnum,tnum,snum,dnum,bionum = 1,0,0,0,0

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
                if 'CTD Pressure at Nominal' in line:
                    pcols.append( int(re.search(r'\% (.*?)= CTD Pressure ',line).group(1).strip(' ')) )
                    columns.append(f'P{pnum}')
                    pnum += 1
                    pdepths.append( float(re.search(r'at Nominal (.*?) \(m\)',line).group(1).strip(' ')) )
                    
                if 'Temperature at nominal' in line:
                    tdepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'T{tnum}')
                    tnum += 1
                if 'CTD Temperature' in line:
                    tdepths.append( float(re.search(r'at (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'T{tnum}')
                    tnum += 1
                    
                if 'Salinity at nominal depth' in line:
                    sdepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'S{snum}')
                    snum += 1
                if 'CTD Salinity' in line:
                    sdepths.append( float(re.search(r'at (.*?) \(m\)',line).group(1).strip(' ')) )
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
                    
                if 'Calculated Depth at nominal depth' in line and 'Bio' not in line:
                    ddepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'D{dnum}')
                    dnum += 1
                if 'First tpod in water' in line:
                    columns.append('FirstTpod')
                    
                if 'Bio' in line:
                    biodepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                    columns.append(f'Bio{bionum}')
                    bionum += 1
                    
            if line.strip('\n') == 'END':
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) #ii+1,len(lines)+1)]
                # only get columns that match Level1
                df = pd.DataFrame(data=data[:,:len(columns)],columns=columns)
                df[df==-999] = np.NaN
                df[df==-99] = np.NaN
                # if pdepths:
                #     pdepths = np.array(pdepths)
                # if tdepths:
                #     tdepths = np.array(tdepths)
                # if sdepths:
                #     sdepths = np.array(sdepths)
                # if ddepths:
                #     ddepths = np.array(ddepths)

    df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
    print(df.columns)
    print()
    print(df.head())
    # exit(-1)

    if bid in ['300234064739080']:  # need to sort T and D cols by depths
        origcols = df.columns.to_list()
        print('originals ',origcols)
        newcols = origcols[:6] # time and loc
        newcolnames = origcols[:6] # time and loc
        newcols.extend([col for col in origcols if col.startswith('P')])
        newcolnames.extend([col for col in origcols if col.startswith('P')])

        Tdict={}
        tcols = [col for col in df.columns if col.startswith('T')]
        for tdepth,tcol in zip(tdepths,tcols):
            Tdict[tcol] = tdepth
        Tdict = dict(sorted(Tdict.items(), key=lambda item:item[1]))
        newcols.extend(Tdict.keys())
        print('line 403',newcols)
        # exit(-1)
        newcols.extend([col for col in origcols if col.startswith('S')])
        
        Ddict={}
        dcols = [col for col in df.columns if col.startswith('D') and not col.startswith('Da')]
        print('line 408 in wI',dcols,ddepths)
        for ddepth,dcol in zip(ddepths,dcols):
            Ddict[dcol] = ddepth
        Ddict = dict(sorted(Ddict.items(), key=lambda item:item[1]))
        print(Ddict)
        newcols.extend(Ddict.keys())
        print()
        print('line 414',newcols)
        # exit(-1)

        newcols.extend(['BATT'])        
        newcols.extend(['WaterIce'])
        newcols.extend(['FirstTpod'])
        
        newcols.extend([col for col in df.columns if col.startswith('Bio')])
        newcols.extend(['Dates'])
    
        
        newcolnames.extend([f'T{n}' for n in range(len(tcols))])
        newcolnames.extend([col for col in origcols if col.startswith('S')])
        newcolnames.extend([f'D{n}' for n in range(len(dcols))])
        newcolnames.extend(['BATT'])
        newcolnames.extend(['WaterIce'])
        newcolnames.extend(['FirstTpod'])
        newcolnames.extend([col for col in origcols if col.startswith('Bio')])
        newcolnames.extend(['Dates'])
                        
        # rearrange the df
        df = df[newcols]
        # rename the temperature columns
        df.rename(columns=dict(zip(newcols,newcolnames)), inplace=True)
        print(df.columns)
        print()
        print(df.head())
        tdepths.sort()
        ddepths.sort()
        print(tdepths)
        print(ddepths)
    # exit(-1)

    return df, pdepths, tdepths, ddepths, sdepths, biodepths

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


def getBuoyIce(blon,blat,byear,bmonth,bday,sst,plott=0,bid=None,figspath=None):
    delta = 45  # nsidc ice maps rotated -45degrees
    grid_size = 25 #km
    bx,by = polar_lonlat_to_xy(blon+delta, blat, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY, hemisphere)
    bx *= 1000
    by *= 1000
    [bi,bj] = polar_lonlat_to_ij(blon, blat, grid_size, hemisphere)  #i is to x as j is to y and they do +delta
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

        if '300234060320940' in bid:
             # check ice cover
            if strdate in ['20200301','20200601','20200801']:
                print(strdate)
                fig2, ax2 = plt.subplots(1,figsize=(8.3,10))
                ax2 = plt.subplot(1,1,1,projection=ccrs.NorthPolarStereo(central_longitude=0))
                ax2.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
                kw = dict(central_latitude=90, central_longitude=-45, true_scale_latitude=70)
                ch = ax2.contourf(x,y,ice, colors=icecolors, levels=icelevels, vmin=0, vmax=0.9, extend='both',
                                  transform=ccrs.Stereographic(**kw))   #use either colors or cmap
                ax2.plot(blon,blat,'ro',ms=12,transform=ccrs.PlateCarree())
                ax2.gridlines(crs=ccrs.PlateCarree(),xlocs=np.arange(-180,180,45),color='gray')
                ax2.add_feature(cfeature.LAND,facecolor='tan')
                ax2.coastlines(resolution='50m',linewidth=0.5,color='black')

                fig2.colorbar(ch,ax=ax2)
                ax2.set_title(f'Ice map on {strdate}, Buoy Location red dot')
                fig2.savefig(f'{figspath}/IceMap_{strdate}.png')

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
    bi1 = np.max((bi-trim,0))
    bi2 = np.min((bi+trim,len(x)))
    bj1 = np.max((bj-trim,0))
    bj2 = np.min((bj+trim,len(y)))
        
    ice200 = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
    ice200wi = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
    ice200wi[ice200wi>=0.15] = 1
    ice200wi[ice200wi<0.15]  = 2
    x200 = x[np.arange(bi1,bi2)]
    y200 = y[np.arange(bj1,bj2)]
    # print(x200.shape)
    # print(y200.shape)
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

    icemask = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
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

def getBuoyBathyPoint(df):
    filegeb = '/Users/suzanne/gebco/GEBCO_2019.nc'
    ds = xr.open_dataset(filegeb)
    # gebco has longitudes east 
    # df.loc[(df['Lon']<0),'Lon'] += 360
    print('min lon, max lat buoy',df['Lon'].min(),df['Lon'].max(),df['Lat'].min(),df['Lat'].max())
    
    bathy = ds.sel(lon=slice(df['Lon'].min(),df['Lon'].max()),lat=slice(df['Lat'].min(),df['Lat'].max())).load()
    print(bathy.lon.shape)
    f = interp2d(bathy.lon,bathy.lat,bathy.elevation)
    for ii,row in df.iterrows():
        df['bathymetry'].iloc[ii] = f(df['Lon'].iloc[ii],df['Lat'].iloc[ii])
    # df.loc[(df['Lon']>180),'Lon'] -= 360
    # print(bathy.lon)
    # print(bathy.keys())

    return df

def getBuoyBathy(blon,blat,lonlim=10,latlim=10):
    filegeb = '/Users/suzanne/gebco/GEBCO_2019.nc'
    ds = xr.open_dataset(filegeb)
    bathy = ds.sel(lon=slice(blon-lonlim,blon+lonlim),lat=slice(blat-latlim,blat+latlim)).load()
    # print(bathy.elevation.shape)
    # print(bathy.lon)
    # print(bathy.keys())

    return bathy


def getOPbias(pcol,pdepth,df,bid,figspath):
    bidf = BM.BuoyMaster(bid)

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
    ax5.plot([df['Dates'].iloc[0],df['Dates'].iloc[-1]],[-1*pdepth,-1*pdepth],'r')
     # if bidf['name'][1].startswith('W'):
    #     startstr = input('Enter start date for pressure bias as yyyymmdd ')
    #     dt0 = dt.datetime(np.int(startstr[:4]),np.int(startstr[4:6]),np.int(startstr[6:]))
    #     ax5.set_xlim([dt0,dt0+dt.timedelta(days=30)])
    # else:
    dt0 = dt.datetime(np.int(df['Year'].iloc[0]),np.int(df['Month'].iloc[0]),np.int(df['Day'].iloc[0]))
    ax5.set_xlim([dt0,dt0+dt.timedelta(days=30)])
    ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    try:
        ax5.set_title(f'First month of Ocean Pressure for buoy {bidf["name"][0]}-{int(bidf["name"][1]):02d}, at nominal depth of {pdepth:.1f}m.',wrap=True,fontsize=20)
    except:
        ax5.set_title(f'First month of Ocean Pressure for buoy {bidf["name"][0]}-{bidf["name"][1]}, at nominal depth of {pdepth:.1f}m.',wrap=True,fontsize=20)
    ax5.grid()
    plt.show()
    try:
        fig5.savefig(f'{figspath}/OPbiasDetermination_{bidf["name"][0]}-{int(bidf["name"][1]):02d}_{pdepth:.1f}.png')
    except:
        fig5.savefig(f'{figspath}/OPbiasDetermination_{bidf["name"][0]}-{bidf["name"][1]}_{pdepth:.1f}.png')
    plt.close()
    # OPbias1 = dfdaily[(dfdaily['Dates']>=coords[0][0]) & (dfdaily['Dates']<=coords[1][0])][pcol+'medians'].mean() - pdepth
    bias = df.loc[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]),pcol].median() - pdepth
    # bias2 = df.loc[(df['Dates']>=coords[0][0]) & (df['Dates']<=coords[1][0]),pcol].mode() - pdepth
    print('bias from median of L1 pressures btn two clicks',bias)
    # print('bias from mode of L1 pressures btn two clicks',bias2)
    df[pcol] -= bias
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

    return df, bias

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


def removePspikes(bid,df1,pdepths,figspath,brand='Pacific Gyre'):
    # get columns that might need spike removal
    Pcols = [col for col in df1.columns if col.startswith('P')]
    spikeLimit = {'Pacific Gyre':{20:5,40: 9,60:16,80:16},
                  'Marlin-Yug':  {20:7,40:14,60:26,80:42},
                  'MetOcean':    {20:4,40: 8,60:12,80:12}
                  }
 
    # if len(Pcols)>1:
    # # compute all the spikes, according to table in Level2_QC_doc.php
    #     for ii,pcol in enumerate(Pcols):
    #         print()
    #         print(ii,pcol)
    #         if ii<len(pdepths):
    #             df1[f'dOP{int(pdepths[ii])}'] = -1* df1[pcol].sub(pdepths[ii])
    #     dOPcols = [col for col in df1.columns if col.startswith('dOP')]
    #     print('line 852 in waterIce',dOPcols)
    # else:
    
    for ii,pcol in enumerate(Pcols):
        fig,ax = plt.subplots(2,1,figsize=(15,5),sharex=True)
        df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))
        limit = min(spikeLimit[brand].keys(), key=lambda key: abs(key-pdepths[ii]))
        # pressure gradient
        df1['dPdh'] = df1[pcol].diff() / df1['dh']
        ax[0].plot(df1['Dates'],df1['dPdh'],'r.-')
        ax[0].set_title(f'Pressure change in db/hr for {pcol}')
        ax[1].plot(df1['Dates'],-1*df1[pcol],'r.-')
        df1.loc[(df1['dPdh'].abs()>spikeLimit[brand][limit]),pcol] = np.nan
        ax[1].plot(df1['Dates'],-1*df1[pcol],'b.-')
        # interpolat through nans
        df1[pcol].interpolate(method='linear',inplace=True)
        ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[spikeLimit[brand][limit],spikeLimit[brand][limit]],'--',color='gray')
        ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1*spikeLimit[brand][limit],-1*spikeLimit[brand][limit]],'--',color='gray')
        ax[0].set_xlim([df1['Dates'].iloc[0],df1.loc[(df1['dPdh'].last_valid_index()),'Dates']])  
        ax[1].plot(df1['Dates'],-1*df1[pcol],'g--')
        ax[1].set_title(f'Pressure original(r), after removal per table in Level2_QC_doc.php(b), after interpolation(g--), {pcol}')
        plt.savefig(f'{figspath}/{pcol}spikes.png')    
        plt.show()
        df1.drop(['dPdh','dh'],axis=1,inplace=True)
            
    # if '300234063991680' in bid:  # 2016 07
    #     df1.loc[(df1['dOP60']>4),Pcols] = np.nan
    #     df1.loc[(df1['dOP60']>4),[col for col in df1.columns if col.startswith('dOP')]] = np.nan

    # if len(Pcols)>1:  
    #     fig,ax = plt.subplots(len(Pcols)-1,1,figsize=(12,12),sharex=True)   
    #     for ii,dOPcol in enumerate(dOPcols[:-1]):
    #         ax[ii].plot(df1[dOPcol],df1[dOPcols[-1]],'.')
    #         x = np.arange(-5,30)
    #         if ii==0:
    #             y = 0.46*x - 0.005*x*x + 0.15
    #         if ii==1:
    #             y = 0.66*x + 0.02*np.square(x) - 0.0009*np.power(x,3) + 0.12
    #         ax[ii].plot(x,y,'g--') 
    #         ax[ii].plot(x-1.4,y,'g') 
    #         ax[ii].plot(x+1.4,y,'g') 
    #         ax[ii].set_ylabel(dOPcol)
    #         ax[ii].set_title('Buoy 2016-07 Pressure Anomalies from nominal')
    
    #     for ax in ax:
    #         ax.set_ylim([-5,7.5])    
    #         ax.set_xlim([-5,10]) 
    #         ax.set_xlabel(dOPcols[-1])
    #         ax.grid()
    #     plt.savefig(f'{figspath}/Pspikes.png')    
    #     plt.show()
    # df1.drop([col for col in df1.columns if col.startswith('dOP')],axis=1,inplace=True)
    
    return df1        



def removeTspikes(bid,df1,tdepths,figspath): # working from "Example of spike filtering algorithm in action" in Level2_QC_doc.php
    # get columns that might need spike removal
    Tcols = [col for col in df1.columns if col.startswith('T')]
    Dcols = [col for col in df1.columns if col.startswith('D') and not col.startswith('Da') and not col.startswith('Dest')]
    colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']
 
    # 1 compute spike magnitudes
    for ii,tcol in enumerate(Tcols):
        # print()
        # print(ii,tcol)
        df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))
        # temperature gradient
        df1['dTdhL'] = df1[tcol].diff() / df1['dh']
        df1['dTdhLsign'] = df1['dTdhL'].apply(lambda x: np.sign(x))
        df1['dTdhLsign'].replace(0,np.nan,inplace=True)
        # temperature gradient coming from the right 
        df1['dTdhR']= df1[tcol].iloc[::-1].diff() / df1['dh']
        df1['dTdhRsign'] = df1['dTdhR'].apply(lambda x: np.sign(x))
        df1['dTdhRsign'].replace(0,np.nan,inplace=True)

        df1['samesign'] = np.where(df1['dTdhLsign'] == df1['dTdhRsign'], True, False) # does not inclued two nans
        df1[f'spike{tcol[1:]}'] = df1[['dTdhL','dTdhR']].abs().min(axis=1).mul(df1['dTdhLsign'])
        df1[f'spike{tcol[1:]}'].mask(~df1['samesign'],inplace=True)   # mask says remove the True
        df1[f'spike{tcol[1:]}'].replace(np.nan,0,inplace=True)
        df1.drop(['dh','dTdhL','dTdhLsign','dTdhR','dTdhRsign','samesign'],axis=1,inplace=True)
        
    # fig,ax = plt.subplots(1,1)
    # spikecols = [col for col in df1.columns if col.startswith('spike')]
    # for ii,spikecol in enumerate(spikecols):
    #     ax.plot(df1['Dates'],df1[spikecol],'.-',color=colorList[ii])
    # plt.show()
    # exit(-1)
    # print(df1[['T5','T6','T11','T12','spike5','spike6','spike11','spike12']].head(50))        

    # 2. find envelope of min and max of non-spike points within 2day and 6m 
    #   get temperatures at 1m intervales in depth, make new dataframe 
    dfT = df1[[col for col in Tcols]]
    dfD = df1[[col for col in Dcols]]
    print('Tcols',Tcols)
    print('Dcols',Dcols)
    # fig10,ax10 = plt.subplots(2,1,sharex=True)
    # ch10 = ax10[0].imshow(dfD.T.to_numpy())
    # ax10[0].set_aspect('auto')
    # ax10[0].set_title('depths')
    # fig10.colorbar(ch10,ax=ax10[0])
    # ch10 = ax10[1].imshow(dfT.T.to_numpy())
    # ax10[1].set_title('temps')
    # ax10[1].set_aspect('auto')
    # fig10.colorbar(ch10,ax=ax10[1])
    # plt.show()
    tdata = dfT.to_numpy()
    #   make interpolated temps dataframe
    dfTi = pd.DataFrame(index=df1.index,columns=np.arange(0,int(tdepths[-1])+1))
    for ii,row in dfT.iterrows():
        dfTi.iloc[ii] = np.interp(np.arange(0,int(tdepths[-1])+1),dfD.iloc[ii],dfT.iloc[ii])
    tinterp = dfTi.to_numpy(dtype='float')
    
    # fig,ax = plt.subplots(1,1)
    # ch = ax.imshow(tdata.T,vmin=-5,vmax=5)
    # ax.set_aspect('auto')
    # fig.colorbar(ch,ax=ax)
    # fig1,ax1 = plt.subplots(1,1)
    # ch1 = ax1.imshow(tinterp.T,vmin=-5,vmax=5)
    # ax1.set_aspect('auto')
    # fig.colorbar(ch1,ax=ax1)
    # plt.show()
    # exit(-1)
    
    # remove dfTi temperatures if spikeMag is not zero, these are the temps we'll use to find min and max
    spikeCols = [col for col in df1.columns if col.startswith('spike')]
    for spikecol in spikeCols:
        dfTi.loc[(df1[spikecol] != 0),round(tdepths[int(spikecol[5:])])] = np.nan
    
    #   get min and max values within two days and 3m of thermistor measurement
    for ii,col in enumerate(zip(Tcols,Dcols)):
        df1[f'T{col[0][1:]}max'] = np.nan
        df1[f'T{col[0][1:]}min'] = np.nan
        df1[f'T{col[0][1:]}range'] = np.nan

        # if ii>=6:
        # Max and Min OF NON SPIKE POINTS
        for jj, row in df1.iterrows():
            if not np.isnan(df1[col[0]].iloc[jj]): 
                dateMask = (df1['Dates'] >= df1['Dates'].iloc[jj] - dt.timedelta(days=2)) & (df1['Dates'] <= df1['Dates'].iloc[jj] + dt.timedelta(days=2))
                df1[f'T{col[0][1:]}max'].iloc[jj] = dfTi.loc[dateMask, np.arange(max(round(tdepths[int(col[0][1:])])-3,0),min(round(tdepths[int(col[0][1:])])+4,int(tdepths[-1])+1))].max().max()
                df1[f'T{col[0][1:]}min'].iloc[jj] = dfTi.loc[dateMask, np.arange(max(round(tdepths[int(col[0][1:])])-3,0),min(round(tdepths[int(col[0][1:])])+4,int(tdepths[-1])+1))].min().min()
                df1[f'T{col[0][1:]}range'] = df1[f'T{col[0][1:]}max'] - df1[f'T{col[0][1:]}min']

        fig,ax = plt.subplots(1,1,figsize=(12,8))
        ax.plot(df1['Dates'],df1[col[0]],'k.-')
        # ax.set_ylim([-10,10])
        secax = ax.twinx()
        secax.spines['right'].set_color('red')
        secax.set_ylabel('Spike Magnitude, C/hr',color='r')
        secax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        secax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
        secax.plot(df1.loc[(df1[f'spike{col[0][1:]}']>=0),'Dates'],df1.loc[(df1[f'spike{col[0][1:]}']>=0),f'spike{col[0][1:]}'],'r.-')
        secax.plot(df1.loc[(df1[f'spike{col[0][1:]}']<=0),'Dates'],df1.loc[(df1[f'spike{col[0][1:]}']<=0),f'spike{col[0][1:]}'],'b.-')
        # secax.set_ylim([-10,10])
        ax.plot(df1['Dates'],df1[f'T{col[0][1:]}max'],'g.-')
        ax.plot(df1['Dates'],df1[f'T{col[0][1:]}min'],'g.-')
        ax.set_ylim([np.nanmin( [min(-1*df1[f'T{col[0][1:]}range'].div(2)),min(df1[f'spike{col[0][1:]}']), min(df1[f'T{col[0][1:]}'])]),
                     np.nanmax( [max(   df1[f'T{col[0][1:]}range'].div(2)),max(df1[f'spike{col[0][1:]}']), max(df1[f'T{col[0][1:]}'])])])
            
        # 3. use range (Tmax-Tmin) to set allowable thresholds for pos/neg spikes
        secax.plot(df1['Dates'],df1[f'T{col[0][1:]}range'].div(2),'r')        
        secax.plot(df1['Dates'],-1*df1[f'T{col[0][1:]}range'].div(2),'b')   
        secax.set_ylim([np.nanmin( [min(-1*df1[f'T{col[0][1:]}range'].div(2)),min(df1[f'spike{col[0][1:]}']), min(df1[f'T{col[0][1:]}'])]),
                        np.nanmax( [max(   df1[f'T{col[0][1:]}range'].div(2)),max(df1[f'spike{col[0][1:]}']), max(df1[f'T{col[0][1:]}'])])])
        ax.set_xlim([df1['Dates'].iloc[0],df1.loc[(df1[f'T{col[0][1:]}range'].last_valid_index()),'Dates']])
        ax.set_title(f'Finding Spikes for {col[0]}: temperature(k), temperature range(g), spikes(r/b), half range(r/b)')
        # plt.show()
        
        df1.loc[((df1[f'spike{col[0][1:]}']>df1[f'T{col[0][1:]}range'].div(2)) | (df1[f'spike{col[0][1:]}']<-1*df1[f'T{col[0][1:]}range'].div(2))) &
                ((df1[f'spike{col[0][1:]}'].abs()>1)) &
                ((df1[col[0]]>df1[f'T{col[0][1:]}max']) | (df1[col[0]]<df1[f'T{col[0][1:]}min'])),col[0]] = np.nan
        ax.plot(df1['Dates'],df1[col[0]],'m.')
        print(df1.columns)
        fig.savefig(f'{figspath}/Tspikes{col[0][1:]}.png')
        # plt.show()
  
    print('line 1050 water Ice')
    print(df1.columns)
    df1.drop([col for col in df1.columns if col.startswith('spike')],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'max' in col],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'min' in col],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'range' in col],axis=1,inplace=True)
    print('line 1056 water Ice')
    print(df1.columns)

    return df1

# def makeL2(df,bid,path):
#     binf = BM.BuoyMaster(bid)
#     filename = f'{path}/UTO_{binf['name'][0]}-{int(binf['name'][1]):02}
