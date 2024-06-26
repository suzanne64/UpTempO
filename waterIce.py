
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 12:36:50 2022

@author: suzanne
"""
import re, os
from polar_convert import polar_lonlat_to_xy, polar_lonlat_to_ij, polar_ij_to_lonlat
from polar_convert.constants import NORTH, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY
# from constants import NORTH, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY
import numpy as np
import datetime as dt
import netCDF4 as nc
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits import mplot3d 
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.spatial.distance import pdist
from scipy.interpolate import interp2d, griddata
import UpTempO_BuoyMaster as BM
import statistics
import itertools
from haversine import haversine


# L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
# L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'

icepath = '/Users/suzanne/Google Drive/UpTempO/Satellite_Fields/NSIDC_ICE/north'
hemisphere = NORTH
icecolors=['dimgray','gray','darkgray','lightgray','aliceblue','powderblue']
icelevels=[0.2,0.3,0.4,0.5,0.75]

def getL1(filename, bid, figspath=None):
    print('L1 file name:',filename)
    columns = ['Year','Month','Day','Hour','Lat','Lon']
    colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','gold','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    pdepths = []
    tdepths = []
    sdepths = []
    ddepths = []
    tiltdepths = []
    # pcols = []
    pnum,tnum,snum,dnum,tiltnum = 1,0,0,0,0

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
                    
                if 'Tilt' in line:
                    tiltdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'Tilt{tiltnum}')
                    tiltnum += 1

                if 'Sea Level Pressure' in line:
                    columns.append('BP')
                if 'Air Temperature' in line:
                    if bid not in ['300234060340370','300234061160500']:  # 2014 11 empty, 2020 01 all same value
                        columns.append('Ta')

                if 'Battery Voltage' in line:
                    columns.append('BATT')
                if 'Submergence Percent' in line:
                    columns.append('SUB')
                if 'GPS quality' in line:
                    columns.append('GPSquality')
                if 'SecondsToFix' in line:
                    columns.append('SecondsToFix')
                if '%END' in line:
                    data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))])
                    print(data.shape,'after %END')
            else:
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii,len(lines))])
                print(data.shape,'in else')
                break

    print(columns,len(columns),ii)
    print(data.shape,depdate)

    if bid == '300234068719480':
        data = data[:,:-1]   # 2019 03 has a column of all zeros with no heading name        
    if bid == '300234061160500':
        data = np.delete(data,44,1)  # remove Air Temp 2020 01 because they are all the same value.
        
    df = pd.DataFrame(data=data,columns=columns)
    print(df.columns)
    
    binf = BM.BuoyMaster(bid)
    print(binf)
    #####
    # exit()
    # if sdepths is not None:
    #     Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
    #     print('Scols',Scols)
    #     columns.extend(Scols)
    # columns.insert(0,'removeTspikes')
    # dfSpikeRem = pd.DataFrame(columns=columns)
    # dfSpikeRem['removeTspikes'] = ['% Removed','Before','After']
    # dfSpikeRem.set_index('removeTspikes',inplace=True)
    # print(dfSpikeRem.head())
    # print('Tcols',Tcols)
    # print('Scols',Scols)

    
    # remove columns that are all zeros or all NaNs
    zerosCols = df.any().to_dict()
    for key,value in zerosCols.items():
        if not value:
            if key not in ['SUB','Dest0']:
                df.drop(columns=key,inplace=True)
                print(key)
                exit(-1)
    print(df.columns)
    
    if bid in ['300234066712490','300234064739080']:  # need to sort T cols by depths
        #        2018 JW1          2020 JW2
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
        
    df[df==-999] = np.nan
    df[df==-99] = np.nan
    # drop a column if all values are NaN
    df.dropna(axis=1,how='all',inplace=True)

    # add dates column for plotting
    df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])

    # remove data before deployment date
    df = df[(df['Dates']>=depdate)]
    print('first date after removing those before deployment date:',df['Dates'].iloc[0])
    
    def calcVelocity(df):
        df['DateBTN'] = np.nan
        df['DateBTN'].iloc[1:] = [df['Dates'].iloc[i-1]+(df['Dates'].iloc[i] - df['Dates'].iloc[i-1])/2 for i in range(1,len(df))]
        df['DateBTN'] = pd.to_datetime(df['DateBTN'])
        # df['DateDiff'] = df.loc[:,'Dates'].diff()
        df['SecondsDiff'] = df.loc[:,'Dates'].diff()/np.timedelta64(1,'s')
        df['distm'] = np.nan
        
        df.loc[(df['Lon']>180),'Lon'] -= 360
        for ii in range(1,len(df)):
            loc1 = (df['Lat'].iloc[ii-1],df['Lon'].iloc[ii-1])
            loc2 = (df['Lat'].iloc[ii],  df['Lon'].iloc[ii])
            df['distm'].iloc[ii] = haversine(loc1,loc2,unit='m')
        df['velocity'] = df['distm'] / df['SecondsDiff']
        
        df.loc[(df['Lon']<-180),'Lon'] += 360
        df.drop(columns=['DateBTN','SecondsDiff','distm'],inplace=True)
        
        return df
    

    # make dataframe for saving editing stats
    # Edit = True
    editCols = ['GPSquality','Lat','Lon']
    Pcols = [col for col in df.columns if col.startswith('P')]
    editCols.extend(Pcols)
    Tcols = [col for col in df.columns if col.startswith('T') and 'Ta' not in col and 'Tilt' not in col]
    editCols.extend(Tcols)
    Scols = [col for col in df.columns if col.startswith('S') and not col.startswith('SUB')]
    editCols.extend(Scols)
    print()

    # initialize all cells to zero
    dfEdit = pd.DataFrame(0,columns=editCols, index = ['Raw',
                                                     'DuplicateRows',
                                                     'InitialAdjustment',
                                                     'RawActual',
                                                     'BuoyLocationsFlagged',
                                                     'WrappedTemperatures',
                                                     'TemperaturesTooWarm20',
                                                     'TemperaturesTooWarmDeep',
                                                     'TemperaturesTooWarmWinter',
                                                     'ConstantValue',
                                                     'OtherUnphysicalValues',
                                                     'PressureSpikesReplaced',
                                                     'TemperatureSpikesRemoved',
                                                     'Processed'])
    
    for ecol in editCols:
        print(ecol)
        if 'GPSquality' not in df.columns and ecol == 'GPSquality':
            dfEdit.loc['Raw',ecol] += 0
        else:
            print(df[ecol].count())
            dfEdit.loc['Raw',ecol] += df[ecol].count()

    # implement data clean up (see weCode/LEVEL_2_IDL_CODE/READ_ME.txt)
    dfEdit.loc['DuplicateRows',:] += df.duplicated(['Dates','Lat','Lon']).sum()
    # reset 'GPSquality' to zero if that var not available.
    if 'GPSquality' not in df.columns:
        dfEdit.loc['DuplicateRows','GPSquality'] = 0
    print(dfEdit.head(20))

    # # sum up number of processed data points
    # for ecol in dfEdit.columns:
    #     dfEdit.loc['Processed',ecol]  += (dfEdit.loc['Raw',ecol] - 
    #                                   dfEdit.loc['BuoyLocationsFlagged',ecol] -
    #                                   dfEdit.loc['InitialAdjustment',ecol] -
    #                                   dfEdit.loc['DuplicateRows',ecol] -
    #                                   dfEdit.loc['UnphysicalValues',ecol] -
    #                                   dfEdit.loc['TemperatureSpikesRemoved',ecol])
    # print(dfEdit.head(15))

    # remove duplicate rows
    df.drop_duplicates(['Dates','Lat','Lon'],keep='last',inplace=True)  # like Wendy (see 2016-=06)
    df.reset_index(drop=True,inplace=True)
    # make sure dates are sorted
    df.sort_values(by=['Dates'],inplace=True)
    df.reset_index(drop=True,inplace=True)

######### this has to be done AFTER initial adjustment and rawActual -- so in each paragraph
    # if df['Year'].iloc[0]>=2021:  # when we extract GPSquality with original data
    #     if bid not in ['300534062158480','300534062158460']:   # 2021-04, 2021-05 too late to get GPS and data in same download, but all 3s
    #         if 'GPSquality' in df.columns:  # what about microSWIFTs
    #             # fig,ax = plt.subplots(1,1)
    #             # ax.plot(df['Lon'],df['Lat'],'bo',markersize=10,markerfacecolor='b')
    #             # ax.plot(df.loc[(df['GPSquality']<3),'Lon'],df.loc[(df['GPSquality']<3),'Lat'],'ro',markersize=6,markerfacecolor='r')
    #             # plt.show()
    #             # exit()             
    #             dfEdit.loc['BuoyLocationsFlagged',:] = df.loc[(df['GPSquality']<3),'GPSquality'].count()
    #             df.loc[(df['GPSquality']<3),:] = np.nan
    #             df.dropna(axis=0,how='all',inplace=True)
    #             df.reset_index(inplace=True)
    #             print(dfEdit.head(15))
    # exit()
    print(df.columns)
    pcols = [col for col in df.columns if col.startswith('P') and not col.endswith('0')]
    tcols = [col for col in df.columns if col.startswith('T') and not col.startswith('Ta') and not col.startswith('Tilt')]
    scols = [col for col in df.columns if col.startswith('S') and 'SUB' not in col]
    dcols = [col for col in df.columns if col.startswith('D') and not col.startswith('Da')]
    tiltcols = [col for col in df.columns if col.startswith('Tilt')]
    print(tcols)
            

    # # invalidate Px zero values (not including P0) and other pressure edits depending...
    # for ii,pcol in enumerate(pcols):
    #     df.loc[df[pcol]==0,pcol] = np.nan

    # data editing
    if '300234060340370' in bid:  # 2014 11
        # no initial adjustment
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        # bad location, no GPSquality to help us
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lat']>100),'Lat'].count()
        df.loc[(df['Lat']>100),:] = np.nan
                
        # unphysical values
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']>20),'P1'].count()
        df.loc[(df['P1']>20),'P1'] = np.nan
        dfEdit.loc['ConstantValue','P2'] += df.loc[(df['P2']>32),'P2'].count()
        df.loc[(df['P2']>32),'P2'] = np.nan
        for tcol in tcols:
            dfEdit.loc['ConstantValue',tcol] += df.loc[(df[tcol]>10),tcol].count()
            df.loc[(df[tcol]>10),tcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','T3'] += df.loc[(df['T3']>0.5),'T3'].count()
        df.loc[(df['T3']>0.5),'T3'] = np.nan
        dfEdit.loc['ConstantValue','T0'] += df.loc[(df['T0']==df['T0'].min()),'T0'] .count()
        df.loc[(df['T0']==df['T0'].min()),'T0'] = np.nan
        
        print(dfEdit.head(15))
        # exit()
        
    if '300234060236150' in bid:  # 2014 13
        print(dfEdit.head(15))
        # no initial adjustment
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
                
        # unphysical values
        for pcol in pcols:
            dfEdit.loc['ConstantValue',pcol] += df.loc[(df[pcol]>100),pcol].count()
            df.loc[(df[pcol]>100),pcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[(df['Dates']>dt.datetime(2015,12,25,11,0,0)),'T0'].count()
        df.loc[(df['Dates']>dt.datetime(2015,12,25,11,0,0)),'T0'] = np.nan
        for tcol in tcols:
            if 'T0' not in tcol:
                dfEdit.loc['ConstantValue',tcol] += df.loc[(df['Dates']>dt.datetime(2016,1,8)) & (df[tcol]>-0.55),tcol].count()
                df.loc[(df['Dates']>dt.datetime(2016,1,8)) & (df[tcol]>-0.55),tcol] = np.nan                
        df.drop(df.columns[df.columns.str.startswith('Dest')],axis=1,inplace=True)
        print(dfEdit.head(15))
        # exit()
        
    if '300234062491420' in bid:  # 2016 04 
        # no initial adjustment
        print(dfEdit.head(15))
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
       
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lat']>75.10) & (df['Lat']<75.15) & (df['Lon']>-153.00) & (df['Lon']<-152.92),'Lat'].count()
        df.loc[(df['Lat']>75.10) & (df['Lat']<75.15) & (df['Lon']>-153.00) & (df['Lon']<-152.92),:] = np.nan

        # pressures
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']==0.0),'P1'].count()
        df.loc[(df['P1']==0.0),'P1'] = np.nan
        
        #  these TO are not wrapped. 
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[df['Dates']>dt.datetime(2018,11,5,18,0,0),'T0'].count()
        df.loc[df['Dates']>dt.datetime(2018,11,5,18,0,0),'T0'] = np.NaN
        for tcol in tcols:
            if 'T0' not in tcol:
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[df[tcol]>6,tcol].count()
                df.loc[df[tcol]>6,tcol] = np.NaN
        print(dfEdit.head(15))
        # exit()
        
    if '300234063991680' in bid:  # 2016 07
        print(dfEdit.head(15))
        # Drop first row, where temps have not stablized yet
        dfEdit.loc['InitialAdjustment',dfEdit.columns != 'GPSquality'] += 1
        df.drop(index=df.index[0],axis=0,inplace=True)
        df.reset_index(drop=True,inplace=True)
        
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lat']>73.72) & (df['Lat']<73.74) & (df['Lon']>-147.425) & (df['Lon']<-147.415),'Lat'].count()
        df.loc[(df['Lat']>73.72) & (df['Lat']<73.74) & (df['Lon']>-147.425) & (df['Lon']<-147.415),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lat']>74.10) & (df['Lat']<74.15) & (df['Lon']>-144.2) & (df['Lon']<-144.1),'Lat'].count()
        df.loc[(df['Lat']>74.10) & (df['Lat']<74.15) & (df['Lon']>-144.2) & (df['Lon']<-144.1),:] = np.nan
        
        # remove bad subsurface temps
        for tcol in tcols:
            if 'T0' not in tcol:
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df['Dates']>=dt.datetime(2016,10,20,2,0,0)),tcol].count()
                df.loc[(df['Dates']>=dt.datetime(2016,10,20,2,0,0)),tcol] = np.nan
                df.loc[(df[tcol]<-5) | (df[tcol]>2.5),tcol] = np.nan
        print(dfEdit.head(15))
        
        # pressures
        for ii,pcol in enumerate(pcols):
            dfEdit.loc['ConstantValue',pcol] += df.loc[(df[pcol] == 0),pcol].count()
            df.loc[(df[pcol] == 0),pcol] = np.nan
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df['Dates']>dt.datetime(2016,10,20,2,0,0)),pcol].count()
            df.loc[(df['Dates']>dt.datetime(2016,10,20,2,0,0)),pcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P2'] += df.loc[(df['P2']>100),'P2'].count()
        df.loc[(df['P2']>100),'P2'] = np.nan
                
        print(dfEdit.head(15))
        # exit()

    if '300234064737080' in bid:  # 2017 04
        print(dfEdit.head(15))
        # no initial adjustment
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
 
        #True Temperature = reported value - maximum allowed value - minimum allowed value  Wrapped Temps
        maxValue = 62
        minValue = -20
        dfEdit.loc['WrappedTemperatures','T0'] = df.loc[(df['T0']>40),'T0'].count()
        df.loc[(df['T0']>40),'T0'] -= (maxValue - minValue)
        
        # invalidate erroneous
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[(df['Dates']<dt.datetime(2017,11,25))  & (df['T0']<-12),'T0'].count()
        df.loc[(df['Dates']<dt.datetime(2017,11,25))  & (df['T0']<-12),'T0'] = np.NaN
        for tcol in tcols:
            if tcol not in 'T0':
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df['Dates']>dt.datetime(2018,7,1)),tcol].count()
                df.loc[(df['Dates']>dt.datetime(2018,7,1)),tcol] = np.nan
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']==0),'P1'].count()
        df.loc[(df['P1']==0),'P1'] = np.NaN
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']>30) | (df['P1']<-30),'P1'].count()
        df.loc[(df['P1']>30) | (df['P1']<-30),'P1'] = np.NaN
        print(dfEdit.head(15))
        # exit() 
        
    if '300234064739080' in bid:  # 2017 W6 
        #True Temperature = reported value - maximum allowed value - minimum allowed value  Wrapped Temps
        maxValue = 36
        minValue = -5
        df.loc[(df['T0']>10) & ((df['Dates']< dt.datetime(2017,5,25)) | (df['Dates']>dt.datetime(2017,12,1))),'T0'] -= (maxValue - minValue)
        # unphysical
        dfEdit.loc['UnphysicalValues',tcols] += df.loc[(df['Dates']<dt.datetime(2017,3,9,6,0,0)),tcols].count()
        df.loc[(df['Dates']<dt.datetime(2017,3,9,6,0,0)),tcols] = np.nan
        df.loc[(df['Dates']<dt.datetime(2017,3,9,4,0,0)),'S0'] = np.nan
        df.loc[(df['Dates']>dt.datetime(2017,3,11)) & 
               (df['Dates']<dt.datetime(2017,3,12)) &
               (df['S0']<27.4),'S0'] = np.nan

    if '300234067936870' in bid:  # 2019 W9
        print(dfEdit.head(15))
        # remove initial adjustment 
        dfEdit.loc['InitialAdjustment',dfEdit.columns != 'GPSquality'] += len(df.loc[(df['Dates']<dt.datetime(2019,4,2,0,0,0))])
        df = df.loc[(df['Dates']>=dt.datetime(2019,4,2,0,0,0))]
        df.reset_index(drop=True,inplace=True)
        
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # unwrap temperatures
        maxValue = 36
        minValue = -5
        dfEdit.loc['WrappedTemperatures','T0'] = df.loc[(df['T0']>14),'T0'].count()
        df.loc[(df['T0']>14),'T0'] -= (maxValue - minValue)
        # unphysical values
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[(df['Dates']>dt.datetime(2019,4,30)) & (df['T0']<-20),'T0'].count()
        df.loc[(df['Dates']>dt.datetime(2019,4,30)) & (df['T0']<-20),'T0'] = np.nan
        # # we need to find pdepths for this buoy. It's NOT 10dbar
        print(dfEdit.head(15))
        # exit()

    if '300234068514830' in bid:  # 2019 01
        # no initial adjustment needed
         
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lat']>73.62) & (df['Lat']<73.63) & (df['Lon']>155.13) & (df['Lon']<155.14),'Lat'].count()
        df.loc[(df['Lat']>73.62) & (df['Lat']<73.63) & (df['Lon']>155.13) & (df['Lon']<155.14),:] = np.nan

        # correct wrapped temps
        maxValue = df['T0'].max()
        minValue = df['T0'].min()
        dfEdit.loc['WrappedTemperatures','T0'] += df.loc[(df['T0']>14),'T0'].count()
        df.loc[(df['T0']>14),'T0'] -= (maxValue - minValue)
        
        # unphysical values
        for tcol in tcols[1:]:
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df['Dates']>dt.datetime(2020,10,30)),tcol].count()
                df.loc[(df['Dates']>dt.datetime(2020,10,30)),tcol] = np.nan
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df['Dates']>dt.datetime(2020,10,17)) & (df[tcol]>2),tcol].count()
                df.loc[(df['Dates']>dt.datetime(2020,10,17)) & (df[tcol]>2),tcol] = np.nan
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']==0.0),'P1'].count()        
        df.loc[(df['P1']==0.0),'P1'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']>100),'P1'].count()        
        df.loc[(df['P1']>100),'P1'] = np.nan 
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['Dates']>dt.datetime(2020,11,5)),'P1'].count()
        df.loc[(df['Dates']>dt.datetime(2020,11,5)),'P1'] = np.nan
        print(dfEdit.head(15))
         
    if '300234068519450' in bid:  # 2019 02
        print(dfEdit.head(15))
        dfEdit.loc['InitialAdjustment',dfEdit.columns != 'GPSquality'] += 1
        df = df.iloc[1:,:]  # drop first row
        df.reset_index(drop=True,inplace=True)
                
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # T0 has wrapped values
        maxValue = df['T0'].max()
        minValue = df['T0'].min()
        dfEdit.loc['WrappedTemperatures','T0'] += df.loc[(df['T0']>25),'T0'].count()
        df.loc[(df['T0']>25),'T0'] -= (maxValue - minValue)

        # unphysical values
        for pcol in pcols:
            dfEdit.loc['ConstantValue',pcol] += df.loc[(df[pcol]==0),pcol].count()
            df.loc[(df[pcol]==0),pcol] = np.nan
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df[pcol]>80),pcol].count()
            df.loc[(df[pcol]>80),pcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P2'] += df.loc[(df['P2']>45),'P2'].count()
        df.loc[(df['P2']>45),'P2'] = np.nan        
        for pcol in pcols[1:]:
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df['Dates']>dt.datetime(2022,5,18)),pcol].count() # counts non-Nan
            df.loc[(df['Dates']>dt.datetime(2022,5,18)),pcol] = np.nan

        print(dfEdit.head(15))
        # exit()
        
    if '300234068719480' in bid:  # 2019 03
        # no initial adjustment needed
        print(dfEdit.head(15))
                
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # pressures
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']==-99.9),'P1'].count()
        df.loc[(df['P1']==-99.9),'P1'] = np.nan
        print(dfEdit.head(15))
            
    if '300234060320930' in bid:  # 2019 04
        # no initial adjustment needed
        print(dfEdit.head(15))
                
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # reminder: lon/lat are not from this buoy, these locations jump around
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Dates']>dt.datetime(2020,8,1)),'Dates'].count()
        df = df.loc[(df['Dates']<=dt.datetime(2020,8,1))]
        # this bias is stateed under "Sensor Bias" in the L2 header
        for tcol in tcols:
            df.loc[:,tcol] += 0.2

    if '300234060320940' in bid:  # 2019 05
        # no initial adjustment needed
        print(dfEdit.head(15))
                
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # unphysical values
        for pcol in pcols:
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df[pcol]<0),pcol].count()
            df.loc[(df[pcol]<0),pcol] = np.nan
        df.drop(df.columns[df.columns.str.startswith('Dest')],axis=1,inplace=True)
        # this bias is stateed under "Sensor Bias" in the L2 header
        for ii,tcol in enumerate(tcols):
            df.loc[:,tcol] += 0.2
            if ii>0:
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df[tcol]<-1.9),tcol].count()
                df.loc[(df[tcol]<-1.9),tcol] = np.nan           
        print(dfEdit.head(15))
        # exit()
        
    if '300234061160500' in bid:  # 2020 01
        # no initial adjustment needed
        print(dfEdit.head(15))
                
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # count and invalidate unphysical pressures
        for pcol in pcols:
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df[pcol]<0),pcol].count()
            df.loc[(df[pcol]<0),pcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']>25) | (df['P1']<5),'P1'].count()  
        df.loc[(df['P1']>25) | (df['P1']<5),'P1'] = np.nan  
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['Dates']>dt.datetime(2021,1,12)) & (df['Dates']<dt.datetime(2021,1,19,6,0,0)),'P1'].count()
        df.loc[(df['Dates']>dt.datetime(2021,1,12)) & (df['Dates']<dt.datetime(2021,1,19,6,0,0)),'P1'] = np.nan
        # remove Ta if data are all the same value
        # ta = df['Ta'].to_numpy()
        # if (ta[0] == ta).all():
        #     df.drop(columns=['Ta'],inplace=True)   
        
        # remove Dest columns as they don't tell us much.
        df.drop(df.columns[df.columns.str.startswith('Dest')],axis=1,inplace=True)
        # invalidate low, constant temps
        for ii,tcol in enumerate(tcols):
            dfEdit.loc['ConstantValue',tcol] += df.loc[(df[tcol]<=-20),tcol].count()
            df.loc[(df[tcol]<=-20),tcol] = np.nan
            if ii>0:
                dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df[tcol]<-1.9),tcol].count()
                df.loc[(df[tcol]<-1.9),tcol] = np.nan           
        print(dfEdit.head(15))
        # exit()
        
    if '300534060649670' in bid:  # 2021 01
        # no initial adjustment needed
        print(dfEdit.head(15))
    
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan  
        print(dfEdit.head(15))
        # # unexplained wacky location
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>73.1) & (df['Lat']<73.2) & (df['Lon']>-150.7) & (df['Lon']<-150.6),'Lat'].count()
        df.loc[(df['Lat']>73.1) & (df['Lat']<73.2) & (df['Lon']>-150.7) & (df['Lon']<-150.6),:] = np.nan
        # this plot shows there are not nec'ly jumps in locs, but GPS<3 creates gaps.
        # fig,ax = plt.subplots(1,1,figsize=(20,8))
        # ax.plot(df['Dates'],df['Lat'],'.-')
        # plt.show()
        # exit()
                
        # pressures
        for pcol in pcols:
            dfEdit.loc['ConstantValue',pcol] += df.loc[(df[pcol]==0),pcol].count()
            df.loc[(df[pcol]==0),pcol] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P2'] += df.loc[(df['Dates']>dt.datetime(2021,8,31)),'P2'].count()
        df.loc[(df['Dates']>dt.datetime(2021,8,31)),'P2'] = np.nan
        # temperatures
        dfEdit.loc['OtherUnphysicalValues','T0'] += 1
        df['T0'].iloc[0] = np.nan
        # 10m T and S are bad, but we want to keep the columns
        dfEdit.loc['OtherUnphysicalValues','T4'] += df['T4'].count()
        df['T4'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','S1'] += df['S1'].count()        
        df['S1'] = np.nan
        print(dfEdit.head(15))
        
    if '300534060251600' in bid:  # 2021 02
        # no initial adjustment needed
        print(dfEdit.head(15))

        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan          
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Dates']>=dt.datetime(2021,12,23))].count() # these still need to be removed even tho' GPS=3
        df.loc[(df['Dates']>=dt.datetime(2021,12,23)),:] = np.nan
        print(dfEdit.head(15))

        # unwrap temps (T0)
        dfEdit.loc['WrappedTemperatures','T0'] += df.loc[(df['T0']>20),'T0'].count()
        df.loc[(df['T0']>20),'T0'] -= (df['T0'].max() - df['T0'].min())
        
        # temperatures
        dfEdit.loc['OtherUnphysicalValues','T0'] += 1
        df['T0'].iloc[0] = np.nan
        # pressures
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']<7.5),'P1'].count()
        df.loc[(df['P1']<7.5),'P1'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P2'] += df.loc[(df['P2']<15),'P2'].count()
        df.loc[(df['P2']<15),'P2'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P3'] += df.loc[(df['P3']<30),'P3'].count()
        df.loc[(df['P3']<30),'P3'] = np.nan
        print(dfEdit.head(15))
        # exit()
        
    if '300534060051570' in bid:  # 2021 03
        print(dfEdit.head(15))
        dfEdit.loc['InitialAdjustment',:] += df.loc[df['Dates']<dt.datetime(2021,9,30),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2021,9,30)),:]
        df.reset_index(drop=True,inplace=True)
        print(dfEdit.head(15))

        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan          
        print(dfEdit.head(15))
        # exit()
        
    if '300534062158480' in bid:  # 2021 04    No GPSquality
        print(dfEdit.head(15))
        dfEdit.loc['InitialAdjustment',dfEdit.columns != 'GPSquality'] += 1
        df = df.iloc[1:,:]  # drop first row
        df.reset_index(drop=True,inplace=True)

        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # GPSquality not available for this buoy
        # unphysical values
        dfEdit.loc['OtherUnphysicalValues','S0'] += df.loc[(df['S0']<25),'S0'].count()
        df.loc[(df['S0']<25),'S0'] = np.nan      
        print(dfEdit.head(15))

    if '300534062158460' in bid:  # 2021 05    No GPSquality
        print(dfEdit.head(15))
        dfEdit.loc['InitialAdjustment',dfEdit.columns != 'GPSquality'] += 1
        df = df.iloc[1:,:]  # drop first row
        df.reset_index(drop=True,inplace=True)

        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]

        # GPSquality not available for this buoy
        # salinities
        dfEdit.loc['OtherUnphysicalValues','S0'] += df.loc[(df['Dates']>dt.datetime(2021,11,6)) & (df['Dates']<dt.datetime(2021,11,7)) & (df['S0']<35),'S0'].count()
        df.loc[(df['Dates']>dt.datetime(2021,11,6)) & (df['Dates']<dt.datetime(2021,11,7)) & (df['S0']<35),'S0'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','S0'] += df.loc[(df['Dates']>dt.datetime(2021,11,8,16,0,0)) & (df['Dates']<dt.datetime(2021,11,8,20,0,0)) & (df['S0']<35.1),'S0'].count()
        df.loc[(df['Dates']>dt.datetime(2021,11,8,16,0,0)) & (df['Dates']<dt.datetime(2021,11,8,20,0,0)) & (df['S0']<35.1),'S0'] = np.nan
        print(dfEdit.head(15))

    if '300534062898720' in bid: # 2022 01     BuoyLocationsFlagged, UnphysicalValues
        # don't include data before buoy goes in water
        print(dfEdit.head(15))
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<dt.datetime(2022,9,9,4,0,0)),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2022,9,9,4,0,0)),:] 
        df=df.reset_index(drop=True)
        
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        # BuoyLocationsFlagged
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),'GPSquality'] = np.nan
        # bad?, two points disjointed in time, at end of time series
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Dates']>=dt.datetime(2023,2,23)),'Dates'].count()
        df.loc[(df['Dates']>=dt.datetime(2023,2,23)),:] = np.nan
        
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>85) | (df['Lat']<70),'Lat'].count()
        df.loc[(df['Lat']>85) | (df['Lat']<70),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lon']>-100),'Lon'].count()
        df.loc[(df['Lon']>-100),:] = np.nan

        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>72.56) & (df['Lat']<72.57) & (df['Lon']>-154.78) & (df['Lon']<-154.77),'Lat'].count()
        df.loc[(df['Lat']>72.56) & (df['Lat']<72.57) & (df['Lon']>-154.78) & (df['Lon']<-154.77),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>72.02) & (df['Lat']<72.03) & (df['Lon']>-152.81) & (df['Lon']<-152.80),'Lat'].count()
        df.loc[(df['Lat']>72.02) & (df['Lat']<72.03) & (df['Lon']>-152.81) & (df['Lon']<-152.80),:] = np.nan

        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>74.80) & (df['Lat']<74.85) & (df['Lon']>-163.70) & (df['Lon']<-163.65),'Lat'].count()
        df.loc[(df['Lat']>74.80) & (df['Lat']<74.85) & (df['Lon']>-163.70) & (df['Lon']<-163.65),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lat']>72.474) & (df['Lat']<72.476) & (df['Lon']>-154.739) & (df['Lon']<-154.738),'Lat'].count()
        df.loc[(df['Lat']>72.474) & (df['Lat']<72.476) & (df['Lon']>-154.739) & (df['Lon']<-154.738),:] = np.nan
        
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Dates']>dt.datetime(2022,10,7,22,0,0)) & (df['Dates']<dt.datetime(2022,10,8,0,0,0)) &
                                                        (df['Lat']>75.09) & (df['Lat']<75.10) &
                                                        (df['Lon']>-163.026) & (df['Lon']<-163.024),'Lat'].count()
        df.loc[(df['Dates']>dt.datetime(2022,10,7,22,0,0)) & (df['Dates']<dt.datetime(2022,10,8,0,0,0)) &
                                                        (df['Lat']>75.09) & (df['Lat']<75.10) &
                                                        (df['Lon']>-163.026) & (df['Lon']<-163.024),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Dates']>dt.datetime(2022,10,7,22,0,0)) & (df['Dates']<dt.datetime(2022,10,8,0,0,0)) &
                                                        (df['Lat']>75.07) & (df['Lat']<75.08) &
                                                        (df['Lon']>-163.008) & (df['Lon']<-163.006),'Lat'].count()
        df.loc[(df['Dates']>dt.datetime(2022,10,7,22,0,0)) & (df['Dates']<dt.datetime(2022,10,8,0,0,0)) &
                                                        (df['Lat']>75.07) & (df['Lat']<75.08) &
                                                        (df['Lon']>-163.008) & (df['Lon']<-163.006),:] = np.nan
        print(dfEdit.head(15))
        # exit()
       
        # pressures
        dfEdit.loc['ConstantValue','P1'] += len(df.loc[(df['P1']>20),'P1'])
        df.loc[(df['P1']>20),'P1'] = np.nan

        # # temperatures
        dfEdit.loc['OtherUnphysicalValues','T0'] += len(df.loc[(df['Dates']>dt.datetime(2022,10,20)) & (df['T0']<-2),'T0'])
        df.loc[(df['Dates']>dt.datetime(2022,10,20)) & (df['T0']<-2),'T0'] = np.nan  # UnphysicalValues

        for ii,tcol in enumerate(tcols):
            dfEdit.loc['ConstantValue',tcol] += len(df.loc[(df[tcol]==0.0) | (df[tcol]==-0.0001),tcol])
            df.loc[(df[tcol]==0.0) | (df[tcol]==-0.0001),tcol] = np.nan

        # # salinities
        # # major decrease, leave for now.
        # # df.loc[(df['Dates']>dt.datetime(2022,10,22,11,0,0)) & (df['Dates']<dt.datetime(2022,10,26)),scols] = np.nan
        for scol in scols:
            dfEdit.loc['ConstantValue',scol] += len(df.loc[(df[scol]==0.0) | (df[scol]==159.9323),scol])
            df.loc[(df[scol]==0.0) | (df[scol]==159.9323),scol] = np.nan
        print(dfEdit.head(15))
            
    if '300534062897730' in bid: # 2022 02        
        print(dfEdit.head(15))
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += len(df.loc[(df['Dates']<dt.datetime(2022,9,9,16,0,0)),'Dates'])
        df = df.loc[(df['Dates']>dt.datetime(2022,9,9,16,0,0)),:] 
        df.reset_index(drop=True,inplace=True)
               
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
 
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),'GPSquality'] = np.nan
        print(dfEdit.head(15))

        # wrapped T1 temps
        df.loc[(df['T1']>20),'T1'] -= (df['T1'].max() - df['T1'].min())
        # invalidate salinities after max salinity, NOT YET
        # imax = df['S0'].idxmax()
        # df['S0'].iloc[imax+1:] = np.nan
        print(dfEdit.head(15))

    if '300534063704980' in bid: # 2022 03 
        # no initial adjustment needed
        print(dfEdit.head(15))
        
        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),'GPSquality'] = np.nan
        print(dfEdit.head(15))

        # P5 pressures getting shallower for some reason, ending in constant value 
        dfEdit.loc['ConstantValue','P5'] += df.loc[(df['P5']==-10.13),'P5'].count()
        df.loc[(df['P5']==-10.13),'P5'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P5'] += df.loc[(df['Dates']>dt.datetime(2022,10,4)),'P5'].count()
        df.loc[(df['Dates']>dt.datetime(2022,10,4)),'P5'] = np.nan
       
        # unexplained offset in P1. Let interpolation fill the depths.
        dfEdit.loc['OtherUnphysicalValues','P1'] += len(df.loc[(df['Dates']>dt.datetime(2022,10,18,15,0,0)) & (df['Dates']<dt.datetime(2022,10,22)),'P1'])
        df.loc[(df['Dates']>dt.datetime(2022,10,18,15,0,0)) & (df['Dates']<dt.datetime(2022,10,22)),'P1'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']>12),'P1'].count()
        df.loc[(df['P1']>12),'P1'] = np.nan
        # temperatures
        dfEdit.loc['ConstantValue','T0'] += df.loc[(df['T0']==-0.01),'T0'].count()
        df.loc[(df['T0']==-0.01),'T0'] = np.nan
        print(dfEdit.head(15))
     
    if '300534063807110' in bid: # 2022 04  
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += len(df.loc[(df['Dates']<dt.datetime(2022,9,11,17,50,0)),'Dates'])
        df = df.loc[(df['Dates']>=dt.datetime(2022,9,11,17,50,0)),:] 
        df.reset_index(drop=True,inplace=True)

        dfEdit.loc['RawActual',:] =  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        # check for bad buoy locations
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan

        # pressures
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']>15) | (df['P1']==0),'P1'].count()       
        df.loc[(df['P1']>15) | (df['P1']==0),'P1'] = np.nan 
        # temperatures
        for tcol in tcols:
            dfEdit.loc['ConstantValue',tcol] += len(df.loc[(df[tcol]==0.0) | (df[tcol]==-0.0001),tcol])
            df.loc[(df[tcol]==0.0) | (df[tcol]==-0.0001),tcol] = np.nan
        # salinities
        for scol in scols:
            dfEdit.loc['ConstantValue',scol] += len(df.loc[(df[scol]>150) | (df[scol]<12),scol])
            df.loc[(df[scol]>150) | (df[scol]<12),scol] = np.nan
        
        # invalidate salinities after max salinity, NOT YET
        # imax = df['S0'].idxmax()
        # df['S0'].iloc[imax+1:] = np.nan
        # print(dfEdit.head(15))
        # exit()
 
    if '300534063803100' in bid: # 2022 05
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<=dt.datetime(2022,9,13,18,30,0)),'Dates'].count()
        df = df.loc[(df['Dates']>dt.datetime(2022,9,13,18,30,0)),:]
        df.reset_index(drop=True,inplace=True)

        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        # check for bad buoy locations
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan
        print(dfEdit.head(15))
        
        # pressures
        for pcol in pcols:
            dfEdit.loc['OtherUnphysicalValues',pcol] += df.loc[(df[pcol]<2) | (df[pcol]>70),pcol].count()       
            df.loc[(df[pcol]<2) | (df[pcol]>70),pcol] = np.nan
        # temperatures
        for tcol in tcols:
            dfEdit.loc['OtherUnphysicalValues',tcol] += df.loc[(df[tcol]<-10) | (df[tcol]>30),tcol].count()
            df.loc[(df[tcol]<-10) | (df[tcol]>30),tcol] = np.nan
        # salinities
        for scol in scols:
            dfEdit.loc['OtherUnphysicalValues',scol] += df.loc[(df[scol]<20),scol].count()
            print(df.loc[(df[scol]<20),scol].count())
            df.loc[(df[scol]<20),scol] = np.nan
        print(dfEdit.head(15))
        # exit()
    
    if '300534062892700' in bid: # 2022 06
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<=dt.datetime(2022,9,15,22,30,0)),'Dates'].count()
        df = df.loc[(df['Dates']>dt.datetime(2022,9,15,22,30,0)),:]
        df.reset_index(drop=True,inplace=True)

        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        print(dfEdit.head(15))
        
        # bad buoy locations
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan

        # temperatures        
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[(df['T0']<-1.9),'T0'].count()  # lone point
        df.loc[(df['T0']<-1.9),'T0'] = np.nan
        dfEdit.loc['ConstantValue','T1'] += df.loc[(df['T1']==0),'T1'].count()
        df.loc[(df['T1']==0),'T1'] = np.nan
        # salinities
        dfEdit.loc['ConstantValue','S0'] += df.loc[(df['S0']==0),'S0'].count()
        df.loc[(df['S0']==0),'S0'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','S0'] += df.loc[(df['S0']<20),'S0'].count()
        df.loc[(df['S0']<20),'S0'] = np.nan
        print(dfEdit.head(15))
        # exit()
        
    if '300534062894700' in bid: # 2022 07
        df = df.loc[(df['Dates']>dt.datetime(2022,9,17,17,0,0)),:]
        df.reset_index(drop=True,inplace=True)
        # correct wrapped temps
        df.loc[(df['T1']>20),'T1'] -= (df['T1'].max() - df['T1'].min())
        
        # invalidate salinities after max salinity, NOT YET
        # imax = df['S0'].idxmax()
        # df['S0'].iloc[imax+1:] = np.nan
        # df.loc[(df['S0']<1),'S0'] = np.nan  why do we have this?

    if '300534062894740' in bid: # 2022 08
        df = df.loc[(df['Dates']>dt.datetime(2022,9,20,2,10,0)),:]
        df.reset_index(drop=True,inplace=True)
        df.loc[(df['Lon']>-153) & (df['Lon']<-152.8) & (df['Lat']<72.6),:] = np.nan
        df.loc[(df['Lon']>-154.5) & (df['Lon']<-154.4) & (df['Lat']>73.9),:] = np.nan
        df.loc[(df['Lon']>-153.7) & (df['Lon']<-153.6) & (df['Lat']>73.9),:] = np.nan
        df.loc[(df['P1']>60),'P1'] = np.nan
        df.loc[(df['P1']<0),'P1'] = np.nan
        df.loc[(df['T0']>30),'T0'] = np.nan
        df.loc[(df['T1']>30),'T1'] = np.nan
        df.loc[(df['S0']<10),'S0'] = np.nan
        # invalidate salinities after max salinity, NOT YET
        # imax = df['S0'].idxmax()
        # df['S0'].iloc[imax+1:] = np.nan

    if '300534062896730' in bid: # 2022 09
        df = df.loc[(df['Dates']>=dt.datetime(2022,9,20,7,0,0)),:]
        df.reset_index(drop=True,inplace=True)
        for pcol in pcols:
            df.loc[(df[pcol]<10),pcol] = np.nan
            df.loc[(df[pcol]>80),pcol] = np.nan
        # 'removePspikes' does not take care of these (later on), so I'm doing it here.
        df.loc[(df['Dates']>dt.datetime(2023,4,1)) & (df['P3']<50),'P3'] = np.nan
        # unwrap T1
        df.loc[(df['T1']>40),'T1'] -= (df['T1'].max() - df['T1'].min())
        for ii,tcol in enumerate(tcols):
              df.loc[(df[tcol]>10),tcol] = np.nan
              if ii<2:
                  df.loc[(df[tcol]==-0.01) | (df[tcol]==0.0000),tcol] = np.nan
        # hand editing, removeTspikes doesn't take them all out.
        df.loc[(df['T5']>-1) & (df['Dates']>dt.datetime(2022,10,22)) & (df['Dates']<dt.datetime(2022,12,1)),'T5'] = np.nan
        df.loc[(df['T7']>1.5) & (df['Dates']>dt.datetime(2022,10,22)) & (df['Dates']<dt.datetime(2022,12,1)),'T7'] = np.nan
        df.loc[(df['T7']>-1) & (df['Dates']>dt.datetime(2022,11,7)),'T7'] = np.nan
        df.loc[(df['T9']<-2),'T9'] = np.nan
        df.loc[(df['T9']>1) & (df['Dates']>dt.datetime(2022,11,5)),'T9'] = np.nan
        df.loc[(df['T13']<-2),'T13'] = np.nan
        df.loc[(df['T13']>1) & (df['Dates']>dt.datetime(2022,11,1)),'T13'] = np.nan
        for ii,scol in enumerate(scols):
            if ii>0:
                df.loc[(df[scol]<20),scol] = np.nan
                df.loc[(df[scol]>40),scol] = np.nan
        # hand editing, there is no removeSspikes
        df.loc[(df['S0']<1),'S0'] = np.nan
        df.loc[(df['S1']<28) & (df['Dates']>dt.datetime(2022,10,26)),'S1'] = np.nan
        df.loc[(df['S1']<29) & (df['Dates']>dt.datetime(2022,11,2,15,0,0)),'S1'] = np.nan
        df.loc[(df['S1']<29.7) & (df['Dates']>dt.datetime(2022,11,24)),'S1'] = np.nan
        df.loc[(df['S2']<26),'S2'] = np.nan
        df.loc[(df['S2']<26.6) & (df['Dates']>dt.datetime(2022,10,5)),'S2'] = np.nan
        df.loc[(df['S2']<27.7) & (df['Dates']>dt.datetime(2022,10,24,5,0,0)),'S2'] = np.nan
        df.loc[(df['S2']<29) & (df['Dates']>dt.datetime(2022,11,3,5,0,0)),'S2'] = np.nan
        df.loc[(df['S2']<29.5) & (df['Dates']>dt.datetime(2022,11,21)),'S2'] = np.nan
        df.loc[(df['S3']<29) & (df['Dates']>dt.datetime(2022,11,1)),'S3'] = np.nan
        df.loc[(df['S3']<29.5) & (df['Dates']>dt.datetime(2022,11,13)),'S3'] = np.nan
        df.loc[(df['S4']<28),'S4'] = np.nan
        df.loc[(df['S5']<29.4),'S5'] = np.nan
        df.loc[(df['S5']<31.4) & (df['Dates']>dt.datetime(2022,10,30)) & (df['Dates']<dt.datetime(2022,12,1)),'S5'] = np.nan
        
        # intersection of T, S depths
        tsINTdepths = [de for de in sdepths if de in tdepths]
        # indices of intersection
        indS = [i for i,j in enumerate(sdepths) if j in tsINTdepths]
        indT = [i for i,j in enumerate(tdepths) if j in tsINTdepths]
        for ii, (inds,indt) in enumerate(zip(indS,indT)): 
            print(ii,inds,indt)
            if ii<4:
                df.loc[((df[tcols[indt]]<-3) | (df[tcols[indt]]>-1.642)) & (df['Dates']>dt.datetime(2023,4,1)) & (df['Dates']<dt.datetime(2023,5,1)),[tcols[indt],scols[inds]]] = np.nan
                df.loc[(df[scols[inds]]<26) & (df['Dates']>dt.datetime(2023,4,1)) & (df['Dates']<dt.datetime(2023,5,1)),[scols[inds]]] = np.nan  # tcols[indt],
            else:
                df.loc[((df[tcols[indt]]<-1.5) | (df[tcols[indt]]>-1.24)) & (df['Dates']>dt.datetime(2023,4,1)) & (df['Dates']<dt.datetime(2023,5,1)),[tcols[indt],scols[inds]]] = np.nan
                df.loc[(df[scols[inds]]<33) & (df['Dates']>dt.datetime(2023,4,1)) & (df['Dates']<dt.datetime(2023,5,1)),[scols[inds]]] = np.nan  #tcols[indt],
                
                
    if '300534062894730' in bid: # 2022 10
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<dt.datetime(2022,9,25,17,10,0)),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2022,9,25,17,10,0)),:]
        df.reset_index(drop=True,inplace=True)
        
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        # bad buoy locations
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan
        print(dfEdit.head(15))
        
        # remove whacky locations, even tho' GPSQuality = 3
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[( (df['Lon'].diff().abs()>0.005) | (df['Lat'].diff().abs()>0.002) ) & (df['Dates']<dt.datetime(2022,10,2)),'Lat'].count()
        df.loc[( (df['Lon'].diff().abs()>0.005) | (df['Lat'].diff().abs()>0.002) ) & (df['Dates']<dt.datetime(2022,10,2)),:] = np.nan
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lon']>-150.421) & (df['Lon']<-150.420) & (df['Lat']>73.00) & (df['Lat']<73.02),'Lat'].count()
        df.loc[(df['Lon']>-150.421) & (df['Lon']<-150.420) & (df['Lat']>73.00) & (df['Lat']<73.02),:] = np.nan

        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['Lon']>-151.77) & (df['Lon']<-151.76) & (df['Lat']>73.167) & (df['Lat']<73.168),'Lat'].count()
        df.loc[(df['Lon']>-151.77) & (df['Lon']<-151.76) & (df['Lat']>73.167) & (df['Lat']<73.168),:] = np.nan

        # pressures
        dfEdit.loc['ConstantValue','P1'] += df.loc[(df['P1']>60),'P1'].count()
        df.loc[(df['P1']>60),'P1'] = np.nan
        dfEdit.loc['OtherUnphysicalValues','P1'] += df.loc[(df['P1']<0),'P1'].count()
        df.loc[(df['P1']<0),'P1'] = np.nan
        # temperatures
        dfEdit.loc['ConstantValue','T0'] += df.loc[(df['T0']==-0.01),'T0'].count()
        df.loc[(df['T0']==-0.01),'T0'] = np.nan
        dfEdit.loc['ConstantValue','T1'] += df.loc[(df['T1']==37.4287),'T0'].count()
        df.loc[(df['T1']==37.4287),'T1'] = np.nan
        
        dfEdit.loc['OtherUnphysicalValues','T1'] += df.loc[(df['T1']<-10),'T1'].count()
        df.loc[(df['T1']<-10),'T1'] = np.nan
        # # salinities
        dfEdit.loc['OtherUnphysicalValues','S0'] += df.loc[(df['S0']<10),'S0'].count()
        df.loc[(df['S0']<10),'S0'] = np.nan
        
    if '300534062893700' in bid: # 2022 11
        # remove rows before buoy in water, according to P and S values
        dfEdit.loc['InitialAdjustment',:] += len(df.loc[(df['Dates']<dt.datetime(2022,9,25,20,30,0)),'Dates'])
        df = df.loc[(df['Dates']>=dt.datetime(2022,9,25,20,30,0)),:]
        df.reset_index(drop=True,inplace=True)
        
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        
        # bad buoy locations
        dfEdit.loc['BuoyLocationsFlagged',:] += df.loc[(df['GPSquality']<3),'GPSquality'].count()
        df.loc[(df['GPSquality']<3),:] = np.nan
        print(dfEdit.head(15))
        
        # T0 has some unexplainable offset (to warmer temps)
        dfEdit.loc['OtherUnphysicalValues','T0'] += df.loc[(df['Dates']>=dt.datetime(2022,9,30,13,0,0)),'T0'].count()
        df.loc[(df['Dates']>=dt.datetime(2022,9,30,13,0,0)),'T0'] = np.nan 
    
    if '300534062895730' in bid: # 2022 12
        # drop first two rows, data not settled
        df.drop(index=df.index[:2],axis=0,inplace=True)
        # print(df.loc[(df['GPSquality']<3),:])
        # exit(-1)
        # df.loc[(df['Lon']>-145) & (df['Lon']<-135),:] = np.NaN  # removes 1 point
        # fig,ax = plt.subplots(1,1)
        # ax.plot(df['Lon'],df['Lat'],'.')
        # plt.show()
        # exit(-1)
        
    if '300434064041440' in bid: # 2023 01
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        df.drop(columns=['BATT'],inplace=True)  # these data aren't real
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        
    if '300434064042420' in bid: # 2023 02
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        df.drop(columns=['BATT'],inplace=True)  # these data aren't real
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        
    if '300434064046720' in bid: # 2023 03
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        df.drop(columns=['BATT'],inplace=True)  # these data aren't real
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        
    if '300434064042710' in bid: # 2023 04
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        df.drop(columns=['BATT'],inplace=True)  # these data aren't real
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        

    if '300534062891690' in bid: # 2023 05
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<dt.datetime(2023,7,29,6,15,0)),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2023,7,29,6,15,0)),:] 
        df=df.reset_index(drop=True)
        
    if '300534062893740' in bid: # 2023 06
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<dt.datetime(2023,7,29,11,15,0)),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2023,7,29,11,15,0)),:] 
        df=df.reset_index(drop=True)

    if '300534062895700' in bid: # 2023 07
        # don't include data before buoy goes in water
        dfEdit.loc['InitialAdjustment',:] += df.loc[(df['Dates']<dt.datetime(2023,7,29,15,55,0)),'Dates'].count()
        df = df.loc[(df['Dates']>=dt.datetime(2023,7,29,15,55,0)),:] 
        df=df.reset_index(drop=True)
    
    if '300534063449630' in bid: # 2023 08
        df = df.loc[(df['Dates']>=dt.datetime(2023,9,16,20,35,0)),:] 
        

    if '300434064040440' in bid: # 2023 09
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        # velocityname = f'{figspath}/Velocity_{binf["name"][0]}_{int(binf["name"][1]):02d}.csv'
        # df.to_csv(velocityname,float_format='%.4f',index=False)
        # exit()

    if '300434064048220' in bid: # 2023 10
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        
        fig,ax = plt.subplots(2,1,figsize=(10,5),sharex=True)
        ax[0].plot(df['Dates'],df['velocity'],'bo-')
        ax[0].set_ylim([0,2])
        ax[0].set_title('microSWIFT Buoy 2023_10: original speeds')
        ax[0].text(dt.datetime(2023,9,22),1.5,f"{df['velocity'].count()} points")
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        ax[1].plot(df['Dates'],df['velocity'],'bo-')
        ax[1].set_ylim([0,2])
        ax[1].set_title('microSWIFT Buoy 2023_10: speeds > 2 m/s culled')
        ax[1].text(dt.datetime(2023,9,22),1.5,f"{df['velocity'].count()} points")
        fig.savefig(f'{figspath}/velocitiesBeforeAfter.png',)
        # plt.show()
        # exit()
        # velocityname = f'{figspath}/Velocity_{binf["name"][0]}_{int(binf["name"][1]):02d}.csv'
        # df.to_csv(velocityname,float_format='%.4f',index=False)
        # exit()
        
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Lon']>-168.55) & (df['Lon']<-168.5) & (df['Lat']>73.3) & (df['Lat']<73.5),'Lat'].count()
        df.loc[(df['Lon']>-168.55) & (df['Lon']<-168.5) & (df['Lat']>73.3) & (df['Lat']<73.5),:] = np.nan
 
    
    if '300434064044730' in bid: # 2023 11
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        # cull high velocities (in lieu of GPS quality)
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        # velocityname = f'{figspath}/Velocity_{binf["name"][0]}_{int(binf["name"][1]):02d}.csv'
        # df.to_csv(velocityname,float_format='%.4f',index=False)
        # exit()
        
    if '300434064045210' in bid: # 2023 12
        dfEdit.loc['RawActual',:] +=  dfEdit.loc['Raw',:] - dfEdit.loc['DuplicateRows',:] - dfEdit.loc['InitialAdjustment',:]
        df = calcVelocity(df)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['velocity']>2),'velocity'].count()
        df.loc[(df['velocity']>2),:] = np.nan
        # velocityname = f'{figspath}/Velocity_{binf["name"][0]}_{int(binf["name"][1]):02d}.csv'
        # df.to_csv(velocityname,float_format='%.4f',index=False)
        dfEdit.loc['BuoyLocationsFlagged',dfEdit.columns != 'GPSquality'] += df.loc[(df['Dates']>dt.datetime(2023,11,6)),'Lat'].count()
        df.loc[(df['Dates']>dt.datetime(2023,11,6)),:] = np.nan
        
        print(dfEdit.head(15))
        # exit()

    if '300534062897690' in bid: # 2023 13
        pass

##################
    # drop a column if all values are NaN
    if '300534060649670' not in bid:  # we want to keep 'T4' and 'S2' in 2019_05
        df.dropna(axis=1,how='all',inplace=True)
        
    for tcol in tcols:  # warm temps: any > 20, winter months > 6
        dfEdit.loc['TemperaturesTooWarm20',tcol] += df.loc[(df[tcol]>20),tcol].count()
        df.loc[(df[tcol]>20),tcol] = np.nan  
        if '300234067936870' not in bid:  # not 2019 W9, where the sensor is sitting on the ice until Jun 24, 2019
            dfEdit.loc['TemperaturesTooWarmWinter',tcol] += df.loc[(df[tcol]>6) & ( (df['Dates'].dt.month>=10) | (df['Dates'].dt.month<=5) ),tcol].count()
            df.loc[(df[tcol]>6) & ( (df['Dates'].dt.month>=10) | (df['Dates'].dt.month<=5) ),tcol] = np.nan
            
    print(dfEdit.head(15))

    # drop a row if all values are NaN, reset index
    df.dropna(axis=0,how='all',inplace=True)
    df.reset_index(drop=True,inplace=True)
    print('line 921',len(df))
    # exit()
    # fig,ax = plt.subplots(1,1,figsize=(12,6))
    # ch = ax.scatter(df['Lon'],df['Lat'],s=4,c=df['Day'],cmap='turbo')
    # fig.colorbar(ch,ax=ax)
    # plt.show()
    # exit(-1)
    
    # check influence of 'correcting' for SLP
    # if bid in ['300234060320940','300234060320930']:  # 2019 04,05
    #     # correct depths for sea level pressure variations    
    #     pcolsSLP = [f'{col}SLP' for col in pcols]
    #     print(pcols)
    #     print(pcolsSLP)
    #     for ii,pco in enumerate(zip(pcolsSLP,pcols)):
    #         fig8,ax8 = plt.subplots(1,1,figsize=(15,5))
    #         df[pco[0]] = np.NaN
    #         df.loc[~np.isnan(df['BP']),pco[0]] = df.loc[~np.isnan(df['BP']),pco[1]] - (df.loc[~np.isnan(df['BP']),'BP'] - 1013)*0.01
    #         ax8.plot(df['Dates'],-1*df[pco[1]],'r.')  # orig press
    #         ax8.plot(df['Dates'],-1*df[pco[0]],'b.')                # corr press
    #         ax8.set_title(f'Ocean Pressure: original (r) corrected for SLP with BP data (b), {pdepths[ii]}')
    #         ax8.grid()
    #         plt.savefig(f'{figspath}/OPcorrectedSLP_{pdepths[ii]}.png')
    #     # plt.show()
    #     df.drop(columns=pcolsSLP,inplace=True)
        
    # set unseasonably warm temperatures to invalid
    # for tcol in tcols:
    #     df.loc[(df[tcol]>20),tcol] = np.nan
    #     df.loc[((df['Month']>=10) | (df['Month']<=5)) & (df[tcol]>6), tcol] = np.nan
        
    # set out of range submergence values to invalid
    if 'SUB' in df.columns:
        if df.loc[(df['SUB']!=-999),'SUB'].max() <=1:  # check if range is 0-1, if so covert to %
            df['SUB'] *= 100.
        df.loc[(df['SUB']<0.) | (df['SUB']>100.),'SUB'] = np.NaN 

    if bid in '300234067936870':  # 2019 W9 changed May 2023 to reflect pressure data beginning of time series. Not sure what is going on.
        pdepths = [9.0]
        tdepths = [-1, 3.3, 9.]
        
    print('pdepths',pdepths)
    print('tdepths',tdepths)
    print('sdepths',sdepths)
    print()

    plotL1 = input('Do you want to plot L1 data to check ranges? : y for Yes, n for No ')

    remcols = []
    if plotL1.startswith('y'):
        for col in df.columns:

            fig,ax = plt.subplots(1,1,figsize=(15,5))
            # if (col.startswith('D') or col.startswith('P')) and 'Da' not in col:
            if col.startswith('P'):
                ax.plot(df['Dates'],-1*df[col],'.')
                # ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
            elif 'Lat' in col:
                if bid in ['300234060340370','300234060236150','300234064737080','300234065419120','300234068514830','300234067939910','300534063807110','300534062896730']:  
                    # 2014-11, 2014-13, 2017-04, 2017-05, 2019-01 2020-JW2, 2022-04 2022-09
                    df.loc[(df['Lon'])<0,'Lon'] += 360
                ax.plot(df['Lon'],df[col],'.-')
                ax.plot(df['Lon'].iloc[0],df[col].iloc[0],'go')
                ax.plot(df['Lon'].iloc[-1],df[col].iloc[-1],'ro')
                # to see where GPSquality is culled.
                # ax.plot(df.loc[(df['GPSquality']<3),'Lon'],df.loc[(df['GPSquality']<3),col],'co')
            elif 'Lon' in col:
                remcols.append(col)
            elif 'S0' in col:
                for ii,scol in enumerate(scols):
                    ax.plot(df['Dates'],df[scol],'*',color=colorList[ii],ms=3)
            elif 'T0' in col:
            # elif col.startswith('T'):                
                for ii,tcol in enumerate(tcols):
                    ax.plot(df['Dates'],df[tcol],'*',color=colorList[ii],ms=3)
            elif 'Ta' in col:
                ax.plot(df['Dates'],-1*df[col],'.')
            elif 'Dest0' in col:
                for ii,dcol in enumerate(dcols):
                    ax.plot(df['Dates'],-1*df[dcol],'o',color=colorList[ii],ms=1)
            elif 'Tilt0' in col:
                for ii,tiltcol in enumerate(tiltcols):
                    ax.plot(df['Dates'],df[tiltcol],'o-',color=colorList[ii],ms=1)
            elif col.startswith('S') and 'S0' not in col and 'SUB' not in col:
                remcols.append(col)
            elif col.startswith('T') and 'T0' not in col and 'Ta' not in col:
                remcols.append(col)
            elif col.startswith('Dest') and 'Dest0' not in col:
                remcols.append(col)
            elif col.startswith('Tilt') and 'Tilt0' not in col:
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
            if 'Lat' in col:
                fig1,ax1 = plt.subplots(1,1,figsize=(15,5))
                ax1.plot(df['Dates'],df[col],'.')
                ax1.grid()
                ax1.set_title('Latitude with time to see gaps in GPSquality if there are any.')
                try:
                    plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}_withTime.png')
                except:
                    plt.savefig(f'{figspath}/L1_{binf["name"][0]}_{binf["name"][1]}_{col}_withTime.png')
                
                # fig2,ax2 = plt.subplots(1,1,figsize=(15,5))
                # colors = df['Dates']
                # ch = ax2.scatter(df['Lon'],df['Lat'],c=colors,s=3,cmap='prism')
                # fig2.colorbar(ch)
                # plt.show()

    for col in remcols:
        try:
            os.remove(f'{figspath}/L1_{binf["name"][0]}_{int(binf["name"][1]):02d}_{col}.png')
        except:
            os.remove(f'{figspath}/L1_{binf["name"][0]}_{binf["name"][1]}_{col}.png')
            
    if 'index' in df.columns:
        df.drop(columns=['index'],inplace=True)
    print('end of getL1 columns',df.columns)
    
    # if not Edit:
    #     dfEdit = None

    return df,pdepths,tdepths,sdepths,ddepths,tiltdepths,dfEdit


def getL2(filename, bid):
    print('L2 file name:',filename)
    # get Level2 into dataFrame
    columns = ['Year','Month','Day','Hour','Lat','Lon']
    pdepths = []
    tdepths = []
    sdepths = []
    ddepths = []
    tiltdepths = []
    # pcols = []
    pnum,tnum,snum,dnum,tiltnum = 1,0,0,0,0

    # convert Level 2 .dat to pandas dataFrame
    with open(filename,'r') as f:
        lines = f.readlines()
        for ii,line in enumerate(lines):
            if line.startswith('%'):
                if 'year' in line:
                    pass
                if 'Ocean Pressure (dB) at Sensor' in line:
                    # pcols.append( int(re.search(r'\% (.*?)= Ocean Pressure',line).group(1).strip(' ')) )
                    columns.append(f'P{pnum}')
                    pnum += 1
                    pdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ') ))

                if 'Temperature (C) at nominal depth' in line:
                    tdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'T{tnum}')
                    tnum += 1

                if 'Salinity (psu) at nominal depth' in line:
                    sdepths.append( float(re.findall("\d+\.?\d+", line)[-1].strip(' ')) )
                    columns.append(f'S{snum}')
                    snum += 1
                    
                if 'Sea Level Pressure (mBar)' in line:
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
                    
                if 'First Wet Thermistor' in line and '=' in line:
                    columns.append('FirstTpod')
                if 'Sea Surface Temperature' in line and not 'Depth' in line and '=' in line:
                    columns.append('sst')
                if 'Sea Surface Temperature Depth' in line and '=' in line:
                    columns.append('Dsst')
                    
                if 'First Wet Conductivity Sensor' in line and '=' in line:
                    columns.append('FirstSpod')
                if 'Sea Surface Salinity' in line and not 'Depth' in line and '=' in line:
                    columns.append('sss')
                if 'Sea Surface Salinity Depth' in line and '=' in line:
                    columns.append('Dsss')
                    
                # if 'Bio' in line:
                #     biodepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                #     columns.append(f'Bio{bionum}')
                #     bionum += 1
                
            if line.strip('\n') == 'END':
                
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) #ii+1,len(lines)+1)]
                df = pd.DataFrame(data,columns=columns)
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
    # print(df.columns)
    # print()
    # print(df.head())

    # if bid in ['300234064739080']:  # need to sort T and D cols by depths
    #     origcols = df.columns.to_list()
    #     print('originals ',origcols)
    #     newcols = origcols[:6] # time and loc
    #     newcolnames = origcols[:6] # time and loc
    #     newcols.extend([col for col in origcols if col.startswith('P')])
    #     newcolnames.extend([col for col in origcols if col.startswith('P')])

    #     Tdict={}
    #     tcols = [col for col in df.columns if col.startswith('T')]
    #     for tdepth,tcol in zip(tdepths,tcols):
    #         Tdict[tcol] = tdepth
    #     Tdict = dict(sorted(Tdict.items(), key=lambda item:item[1]))
    #     newcols.extend(Tdict.keys())
    #     print('line 403',newcols)
    #     # exit(-1)
    #     newcols.extend([col for col in origcols if col.startswith('S')])
        
    #     Ddict={}
    #     dcols = [col for col in df.columns if col.startswith('D') and not col.startswith('Da')]
    #     print('line 408 in wI',dcols,ddepths)
    #     for ddepth,dcol in zip(ddepths,dcols):
    #         Ddict[dcol] = ddepth
    #     Ddict = dict(sorted(Ddict.items(), key=lambda item:item[1]))
    #     print(Ddict)
    #     newcols.extend(Ddict.keys())
    #     print()
    #     print('line 414',newcols)
    #     # exit(-1)

    #     newcols.extend(['BATT'])        
    #     newcols.extend(['WaterIce'])
    #     newcols.extend(['FirstTpod'])
        
    #     newcols.extend([col for col in df.columns if col.startswith('Bio')])
    #     newcols.extend(['Dates'])
    
        
    #     newcolnames.extend([f'T{n}' for n in range(len(tcols))])
    #     newcolnames.extend([col for col in origcols if col.startswith('S')])
    #     newcolnames.extend([f'D{n}' for n in range(len(dcols))])
    #     newcolnames.extend(['BATT'])
    #     newcolnames.extend(['WaterIce'])
    #     newcolnames.extend(['FirstTpod'])
    #     newcolnames.extend([col for col in origcols if col.startswith('Bio')])
    #     newcolnames.extend(['Dates'])
                        
    #     # rearrange the df
    #     df = df[newcols]
    #     # rename the temperature columns
    #     df.rename(columns=dict(zip(newcols,newcolnames)), inplace=True)
    #     print(df.columns)
    #     print()
    #     print(df.head())
    #     tdepths.sort()
    #     ddepths.sort()
    #     print(tdepths)
    #     print(ddepths)
    # # exit(-1)

    return df, pdepths, tdepths, sdepths, ddepths, tiltdepths

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
    # print(blon,blat,byear,bmonth,bday)
    delta = 45  # nsidc ice maps rotated -45degrees
    grid_size = 25 #km
    bx,by = polar_lonlat_to_xy(blon+delta, blat, TRUE_SCALE_LATITUDE, EARTH_RADIUS_KM, EARTH_ECCENTRICITY, hemisphere)
    bx *= 1000
    by *= 1000
    [bi,bj] = polar_lonlat_to_ij(blon, blat, grid_size, hemisphere)  #i is to x as j is to y and they do +delta
    buoyloc = np.array([[bx,by]])
    # print('buoyloc',buoyloc)
    # print('list of b',bx,by,bi,bj)

    # get ice map
    strdate = f'{int(byear)}{int(bmonth):02}{int(bday):02}'
    # print('strdate',strdate)
    objdate = dt.datetime.strptime(strdate,'%Y%m%d')
    if objdate < dt.datetime(2023,7,1):  # g02202(climate data record)
        icefile = f'{int(byear)}/seaice_conc_daily_nh_{strdate}_f17_v04r00.nc'
        ncdata=nc.Dataset(f'{icepath}/{icefile}')
        ice=np.squeeze(ncdata['cdr_seaice_conc'])
        y=ncdata['ygrid'][:]
        x=ncdata['xgrid'][:]
        ice[ice==251] = np.nan  # pole_hole_mask, flags are not scaled
        icesrc = 'NSIDC-g02202'

        icemapDate = {'300234060320940':['20200301','20200601','20200801'],
                      '300234060320930':['20200301','20200601','20200731'],
                      '300534062894730':['20221020'] }
        if bid in icemapDate.keys():
             # check ice cover
            if strdate in icemapDate[bid]:
                if not os.path.isfile(f'{figspath}/IceMap_{strdate}.png'):
                    print('line 996',strdate)
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
        try:
            ice=np.squeeze(ncdata['F17_ICECON']).astype('float')  # np.squeeze converts nc dataset to np array
        except:
            ice=np.squeeze(ncdata['F18_ICECON']).astype('float')  # np.squeeze converts nc dataset to np array
                
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
    # print('locs day',blon,blat,byear,bmonth,bday)
    # print(bi1,bi2,bj1,bj2,len(x),len(y))
    # print(ice.shape)
    ice200 = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
    x200 = x[np.arange(bi1,bi2)]
    y200 = y[np.arange(bj1,bj2)]
    x200g,y200g = np.meshgrid(x200,y200)

    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.contourf(x200g,y200g,ice200, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_title(f'ice200 from {icesrc} on {strdate}',fontsize=12)
    # fig0.colorbar(ch0)

    ice200wi = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
    ice200wi[ice200wi>=0.15] = 1
    ice200wi[ice200wi<0.15]  = 2
    x200 = x[np.arange(bi1,bi2)]
    y200 = y[np.arange(bj1,bj2)]
    # print(x200.shape,y200.shape,ice200wi.shape)
    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.contourf(x200g,y200g,ice200wi, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_title(f'ice200wi from {icesrc} on {strdate}',fontsize=12)
    # fig0.colorbar(ch0)
    # plott = 1
    # if plott:
    #     if bday==22:
    #         extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
    #         fig0,ax0 = plt.subplots(1,1)
    #         ch0 = ax0.imshow(ice, extent=extent, cmap='turbo')
    #         ax0.plot(bx,by,'mo',markersize=5)
    #         ax0.set_xlim(-2.5e6,1.5e6)
    #         ax0.set_ylim(-1.5e6,2e6)
    #         ax0.set_title(f'IceConc from {icesrc} on {strdate}',fontsize=12)
    #         fig0.colorbar(ch0)
    
    #         extent200=[np.min(x200),np.max(x200),np.min(y200),np.max(y200)]
    #         fig1,ax1 = plt.subplots(1,1)
    #         ch1 = ax1.imshow(ice200wi, extent=extent200)
    #         ax1.plot(bx,by,'mo',markersize=5)
    #         ax1.set_title(f'Ice(1), Water(2), buoy at {blon:.1f}W, {blat:.1f}N, SST={sst:.1f}C')
    #         fig1.colorbar(ch1)
    #         plt.show()
            # exit()

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
    dist1[np.isnan(ice200wi)] = np.nan
    # print('dist1 shape',dist1.shape)
    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.contourf(icexx,iceyy,dist1, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_title(f'dist1 from {icesrc} on {strdate}',fontsize=12)
    # fig0.colorbar(ch0)
    # if plott:
    #     chd = ax1.contour(x200,y200,dist1/1000,levels=np.arange(0,250,25)) #,origin='upper',extent=extent200)
    #     chd.clabel(inline=True) #, chd.levels, inline=True,fontsize=10

        # chd = ax2[0,1].contour(x200,y200,dist1/1000,levels=np.arange(0,250,25)) #,origin='upper',extent=extent200)
        # ax2[0,1].plot(bx,by,'ro',markersize=5)
        # chd.clabel(inline=True) #, chd.levels, inline=True,fontsize=10
        # # fig2.colorbar(chd,ax=ax2[0,1])
        # print('distance map shape',dist1.shape,ice.shape)

    icemask = ice[:,np.arange(bi1,bi2)][np.arange(bj1,bj2),:]
    icemask[np.logical_and(icemask>=0.15,icemask<=1)] = 1
    icemask[icemask<0.15] = 0
    
    # if bday==22:
    #     extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
    #     fig0,ax0 = plt.subplots(1,1)
    #     ch0 = ax0.imshow(ice, extent=extent, cmap='turbo',vmin=0,vmax=0.15)
    #     ax0.plot(bx,by,'mo',markersize=5)
    #     ax0.set_xlim(-2.5e6,1.5e6)
    #     ax0.set_ylim(-1.5e6,2e6)
    #     ax0.set_title(f'IceConc from {icesrc} on {strdate}',fontsize=12)
    #     fig0.colorbar(ch0)
    
    #     # icemask[icemask>200] = 5
    #     fig0,ax0 = plt.subplots(1,1)
    #     ch0 = ax0.imshow(icemask, extent=extent, cmap='turbo')
    #     ax0.plot(bx,by,'mo',markersize=5)
    #     ax0.set_xlim(-2.5e6,1.5e6)
    #     ax0.set_ylim(-1.5e6,2e6)
    #     ax0.set_title(f'Icemask',fontsize=12)
    #     fig0.colorbar(ch0)
    #     plt.show()
    #     exit()

    dist2 = dist1
    # extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.imshow(dist1, extent=extent, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_xlim(-2.5e6,1.5e6)
    # ax0.set_ylim(-1.5e6,2e6)
    # ax0.set_title(f'dist1',fontsize=12)
    # fig0.colorbar(ch0)
    dist2[icemask==0] = np.nan  # setting open water to nan
    # print('dist2 shape',dist2.shape)
    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.contourf(icexx,iceyy,dist2, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_title(f'dist2 from {icesrc} on {strdate}',fontsize=12)
    # fig0.colorbar(ch0)
    # plt.show()
    mindist = np.nanmin(dist2)
    # print(mindist)
    # exit()
    # extent=[np.min(x), np.max(x), np.min(y), np.max(y)]
    # fig0,ax0 = plt.subplots(1,1)
    # ch0 = ax0.imshow(dist2, extent=extent, cmap='turbo')
    # ax0.plot(bx,by,'mo',markersize=5)
    # ax0.set_xlim(-2.5e6,1.5e6)
    # ax0.set_ylim(-1.5e6,2e6)
    # ax0.set_title(f'dist2',fontsize=12)
    # fig0.colorbar(ch0)
    # plt.show()
    # exit()

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
    filegeb = '/Users/suzanne/gebco/GEBCO_2023.nc'
    ds = xr.open_dataset(filegeb)
    # gebco has longitudes east 
    # df.loc[(df['Lon']<0),'Lon'] += 360
    df.loc[(df['Lon']>180),'Lon'] -= 360
    print('min lon, max lat buoy',df['Lon'].min(),df['Lon'].max(),df['Lat'].min(),df['Lat'].max())
    
    bathy = ds.sel(lon=slice(df['Lon'].min(),df['Lon'].max()),lat=slice(df['Lat'].min(),df['Lat'].max())).load()
    print('line 817',bathy.lon.shape)
    f = interp2d(bathy.lon,bathy.lat,bathy.elevation)
    for ii,row in df.iterrows():
        df['bathymetry'].iloc[ii] = f(df['Lon'].iloc[ii],df['Lat'].iloc[ii])
    # df.loc[(df['Lon']>180),'Lon'] -= 360
    # print(bathy.lon)
    # print(bathy.keys())

    return df

def getBuoyBathy(blon,blat,lonlim=10,latlim=10):
    filegeb = '/Users/suzanne/gebco/GEBCO_2023.nc'
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
    # ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax5.xaxis.set_major_locator(mdates.DayLocator(interval=5))
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


def removePspikes(bid,df1,pdepths,figspath,brand='Pacific Gyre',dt1=None,dt2=None,dfEdit=None):
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
        print(df1[pcol].count(),len(df1))

        df1['mask'] = df1[pcol].isna()  # mask because interpolate interpolates through all the nans
        fig,ax = plt.subplots(2,1,figsize=(15,5),sharex=True)
        df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))
        limit = min(spikeLimit[brand].keys(), key=lambda key: abs(key-pdepths[ii]))
        # pressure gradient
        df1['dPdh'] = df1[pcol].diff() / df1['dh']
        ax[0].plot(df1['Dates'],df1['dPdh'],'r.-')
        ax[0].set_title(f'Pressure change in db/hr for {pcol}')
        ax[1].plot(df1['Dates'],-1*df1[pcol],'r.-')
        dfEdit.loc['PressureSpikesReplaced',pcol] += df1.loc[(df1['dPdh'].abs()>spikeLimit[brand][limit]),pcol].count()
        df1.loc[(df1['dPdh'].abs()>spikeLimit[brand][limit]),pcol] = np.nan

        ax[1].plot(df1['Dates'],-1*df1[pcol],'b.-')
        # interpolat through nans, mask out original nans
        df1[pcol].interpolate(method='linear',inplace=True)
        df1.loc[(df1['mask']),pcol] = np.nan

        ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[spikeLimit[brand][limit],spikeLimit[brand][limit]],'--',color='gray')
        ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1*spikeLimit[brand][limit],-1*spikeLimit[brand][limit]],'--',color='gray')
        ax[0].set_xlim([df1['Dates'].iloc[0],df1.loc[(df1['dPdh'].last_valid_index()),'Dates']])  
        ax[1].plot(df1['Dates'],-1*df1[pcol],'g.',ms=3)
        ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        if dt1 is not None:
            ax[0].set_xlim([dt1,dt2])
        ax[1].set_title(f'Pressure original(r), after removal per table in Level2_QC_doc.php(b), after interpolation(g--), {pcol}')
        plt.savefig(f'{figspath}/{pcol}spikes.png')    
        plt.show()
        df1.drop(['dPdh','dh'],axis=1,inplace=True)
    df1.drop(columns=['mask'],inplace=True)
    
    return df1, dfEdit


def removeTspikes(bid,df1,tdepths,figspath,Dcols=None,sdepths=None,dfEdit=None): # working from "Example of spike filtering algorithm in action" in Level2_QC_doc.php
    # get columns that might need spike removal
    Tcols = [col for col in df1.columns if col.startswith('T') and not col.startswith('Tilt')]
    if Dcols is None:
        Dcols = [col for col in df1.columns if col.startswith('D') and not col.startswith('Da') and not col.startswith('Dest') and not col.startswith('Dss')]
    if sdepths is not None:
        Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
 
    colorList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','gold','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

    for ii,tcol in enumerate(Tcols):
        print(ii,tcol)
        print(df1[tcol].count())
  
        # finding T spikes per Level2_QC_doc_2023.php, section 4, ii), d)
        # time gradient in hours
        df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))
        # temperature gradient coming from the left
        df1['dTdhL'] = df1[tcol].diff() / df1['dh']
        df1['dTdhLsign'] = df1['dTdhL'].apply(lambda x: np.sign(x))
        df1['dTdhLsign'].replace(0,np.nan,inplace=True)
        # temperature gradient coming from the right 
        df1['dTdhR']= df1[tcol].iloc[::-1].diff() / df1['dh']
        df1['dTdhRsign'] = df1['dTdhR'].apply(lambda x: np.sign(x))
        df1['dTdhRsign'].replace(0,np.nan,inplace=True)

        df1['samesign'] = np.where(df1['dTdhLsign'] == df1['dTdhRsign'], True, False) # does not inclued two nans
        df1[f'spike{tcol[1:]}'] = df1[['dTdhL','dTdhR']].abs().min(axis=1).mul(df1['dTdhLsign'])
        # df1[f'spike{tcol[1:]}'] = df1.loc[(df1[f'spike{tcol[1:]}']<=1),f'spike{tcol[1:]}'] = 0  # added this 7/17/23
        # df1[tcol] = df1.loc[(df1[f'spike{tcol[1:]}']>1),tcol] = np.nan  # added this 7/17/23
        
        df1[f'spike{tcol[1:]}'].mask(~df1['samesign'],inplace=True)   # mask says remove the True
        df1[f'spike{tcol[1:]}'].replace(np.nan,0,inplace=True)
        df1[f'NonSpikeT{tcol[1:]}'] = df1.loc[(df1[f'spike{tcol[1:]}']==0),tcol]
        # fig,ax = plt.subplots(1,1,figsize=(12,6))
        # ax.plot(df1['Dates'],df1[f'spike{tcol[1:]}'],'r.')
        # ax.set_title('all temps(g), non-spike temps(m), spike(r)')
        # ax.set_ylabel(f'Tspike business for {tcol}')
        # secax = ax.twinx()
        # secax.spines['right'].set_color('green')        
        # secax.set_ylabel(f'Temperatures at {tcol}, C',color='g')
        # secax.plot(df1['Dates'],df1[tcol],'g.')
        # secax.plot(df1['Dates'],df1[f'NonSpikeT{tcol[1:]}'],'m.',ms=3)
        # # print(df1.head(10))
        # plt.show()
        df1.drop(['dh','dTdhL','dTdhLsign','dTdhR','dTdhRsign','samesign'],axis=1,inplace=True)
        
    fig,ax = plt.subplots(1,1)
    spikecols = [col for col in df1.columns if col.startswith('spike')]
    print('spikecols',spikecols)
    for ii,spikecol in enumerate(spikecols):
        ax.plot(df1['Dates'],df1[spikecol],'.-',color=colorList[ii])
    plt.show()

    # 2. find envelope of min and max of non-spike points within 2day and 6m 
    #   get temperatures at 1m intervales in depth, make new dataframe 
    dfT = df1[[col for col in df1.columns if col.startswith('NonSpikeT')]]
    dfD = df1[[col for col in Dcols]]
    print('dfT',dfT.shape)
    print(dfT.head(10))
    print('Dcols',Dcols)
    # exit(-1)
    fig10,ax10 = plt.subplots(2,1,sharex=True)
    ch10 = ax10[0].imshow(dfD.T.to_numpy())
    ax10[0].set_aspect('auto')
    ax10[0].set_title('depths')
    fig10.colorbar(ch10,ax=ax10[0])
    ch10 = ax10[1].imshow(dfT.T.to_numpy())
    ax10[1].set_title('temps')
    ax10[1].set_aspect('auto')
    fig10.colorbar(ch10,ax=ax10[1])
    plt.show()
    tdata = dfT.to_numpy()
    #   make interpolated temps dataframe
    dfTi = pd.DataFrame(index=df1.index,columns=np.arange(0,int(tdepths[-1])+1))
    print(len(dfTi))
    print(dfTi.columns)    
    for ii,row in dfT.iterrows():
        d = np.array(dfD.iloc[ii])
        t = np.array(dfT.iloc[ii])
        if ~np.isnan(t).all():
            dfTi.iloc[ii] = np.interp(np.arange(0,int(tdepths[-1])+1),d[~np.isnan(t)],t[~np.isnan(t)])
        # print(ii,dfTi.iloc[ii])
    tinterp = dfTi.to_numpy(dtype='float')
    print('tinterp shape',tinterp.shape)
    fig11,ax11 = plt.subplots(1,1)
    ch11 = ax11.imshow(tinterp.T)
    ax11.set_aspect('auto')
    ax11.set_title('temperatures interpolated to 1m depths')
    fig11.colorbar(ch11)
    plt.show()
    
    #   get min and max values within two days and 3m of thermistor measurement
    tidepths = np.arange(0,int(tdepths[-1])+1)
    # print('tidepths',tidepths)
    # exit(-1)
    for ii,col in enumerate(zip(Tcols,Dcols)):
        df1[f'T{col[0][1:]}max'] = np.nan
        df1[f'T{col[0][1:]}min'] = np.nan
        df1[f'T{col[0][1:]}range'] = np.nan

        # if ii>=6:
        # Max and Min OF NON SPIKE POINTS
        for jj, row in df1.iterrows():
            if not np.isnan(df1[col[0]].iloc[jj]): 
                dateMask = (df1['Dates'] >= df1['Dates'].iloc[jj] - dt.timedelta(days=1)) & (df1['Dates'] <= df1['Dates'].iloc[jj] + dt.timedelta(days=1))
                df1[f'T{col[0][1:]}max'].iloc[jj] = dfTi.loc[dateMask, np.arange(max(round(tdepths[int(col[0][1:])])-3,0),min(round(tdepths[int(col[0][1:])])+4,int(tdepths[-1])+1))].max().max()
                df1[f'T{col[0][1:]}min'].iloc[jj] = dfTi.loc[dateMask, np.arange(max(round(tdepths[int(col[0][1:])])-3,0),min(round(tdepths[int(col[0][1:])])+4,int(tdepths[-1])+1))].min().min()
                df1[f'T{col[0][1:]}range'] = df1[f'T{col[0][1:]}max'] - df1[f'T{col[0][1:]}min']

        fig,ax = plt.subplots(1,1,figsize=(12,8))
        l1 = max(round(tdepths[int(col[0][1:])])-3,0)
        l2 = min(round(tdepths[int(col[0][1:])])+4,int(tdepths[-1])+1)
        for ll in np.arange(l1,l2):
            ax.plot(df1['Dates'],dfTi.loc[:,ll],'gray',linewidth=0.5)
        ax.plot(df1['Dates'],df1[col[0]],'kx-')
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
        minYs = [min(-1*df1[f'T{col[0][1:]}range'].div(2)), min(df1[f'spike{col[0][1:]}']), min(df1[f'T{col[0][1:]}'])]
        minY = np.nanmin([x for x in minYs if x != -np.inf])
        maxYs = [max(   df1[f'T{col[0][1:]}range'].div(2)), max(df1[f'spike{col[0][1:]}']), max(df1[f'T{col[0][1:]}'])]
        maxY = np.nanmin([x for x in maxYs if x != -np.inf])
        print()
        # ax.set_ylim(minY,maxY)
            
        # 3. use range (Tmax-Tmin) to set allowable thresholds for pos/neg spikes
        secax.plot(df1['Dates'],df1[f'T{col[0][1:]}range'].div(2),'r')        
        secax.plot(df1['Dates'],-1*df1[f'T{col[0][1:]}range'].div(2),'b')   
        
        # secax.set_ylim(minY,maxY)
        try:
            ax.set_xlim([df1['Dates'].iloc[0],df1.loc[(df1[f'T{col[0][1:]}range'].last_valid_index()),'Dates']])
        except:
            ax.set_xlim([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]])
        ax.set_title(f'Finding Spikes for {col[0]}: temperature(k), temperature range(g), spikes(r/b), half range(r/b)')
        # plt.show()
        
        print('before spike removal', col[0],df1[col[0]].count())
        # remove salinity at same depth, if applicable, and do it before  removing the temperature
        try: 
            jj = sdepths.index(tdepths[ii])
            
            dfEdit.loc['TemperatureSpikesRemoved',Scols[jj]] += len(df1.loc[((df1[f'spike{col[0][1:]}']>df1[f'T{col[0][1:]}range'].div(2)) | (df1[f'spike{col[0][1:]}']<-1*df1[f'T{col[0][1:]}range'].div(2))) &
                    ((df1[f'spike{col[0][1:]}'].abs()>1)) &
                    ((df1[col[0]]>df1[f'T{col[0][1:]}max']) | (df1[col[0]]<df1[f'T{col[0][1:]}min'])),Scols[jj]])
            df1.loc[((df1[f'spike{col[0][1:]}']>df1[f'T{col[0][1:]}range'].div(2)) | (df1[f'spike{col[0][1:]}']<-1*df1[f'T{col[0][1:]}range'].div(2))) &
                    ((df1[f'spike{col[0][1:]}'].abs()>1)) &
                    ((df1[col[0]]>df1[f'T{col[0][1:]}max']) | (df1[col[0]]<df1[f'T{col[0][1:]}min'])),Scols[jj]] = np.nan
            
        except:
            print('that depth not in sdepths')
        # remove temp if spike is outside half of range and ( > max or < min)  
        dfEdit.loc['TemperatureSpikesRemoved',col[0]] += len(df1.loc[((df1[f'spike{col[0][1:]}']>df1[f'T{col[0][1:]}range'].div(2)) | (df1[f'spike{col[0][1:]}']<-1*df1[f'T{col[0][1:]}range'].div(2))) &
                ((df1[f'spike{col[0][1:]}'].abs()>1)) &
                ((df1[col[0]]>df1[f'T{col[0][1:]}max']) | (df1[col[0]]<df1[f'T{col[0][1:]}min'])),col[0]])
        df1.loc[((df1[f'spike{col[0][1:]}']>df1[f'T{col[0][1:]}range'].div(2)) | (df1[f'spike{col[0][1:]}']<-1*df1[f'T{col[0][1:]}range'].div(2))) &
                ((df1[f'spike{col[0][1:]}'].abs()>1)) &
                ((df1[col[0]]>df1[f'T{col[0][1:]}max']) | (df1[col[0]]<df1[f'T{col[0][1:]}min'])),col[0]] = np.nan
                
        ax.plot(df1['Dates'],df1[col[0]],'m.')
        print(df1.columns)
        print(df1.head())
        fig.savefig(f'{figspath}/Tspikes{col[0][1:]}.png')
  
    df1.drop([col for col in df1.columns if col.startswith('spike')],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if col.startswith('NonSpike')],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'max' in col],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'min' in col],axis=1,inplace=True)
    df1.drop([col for col in df1.columns if 'range' in col],axis=1,inplace=True)
    print(df1.columns)
    
    return df1, dfEdit

def removeSspikes(bid,df1,sdepths,figspath,dt1=None,dt2=None):
    # THIS DOES NOT WORK YET
    # get columns that might need spike removal
    Scols = [col for col in df1.columns if col.startswith('S') and not col.startswith('SUB')]
    Scols=['S3']
    # spikeLimit = 0.2  # psu/hour

    # used for testing limits
    columns=[f'{item:.2f}' for item in np.arange(0.05,0.3,0.05)]
    columns.insert(0,'None')
    dfLimit = pd.DataFrame(columns=columns)
    for jj,spikeLimit in enumerate(np.arange(0.05,0.3,0.05)): # psu/hour
        print(spikeLimit)
        for ii,scol in enumerate([item for item in Scols]):
            dfLimit['None'] = df1[scol].count()
            df1['mask'] = df1[scol].isna()  # mask because interpolate interpolates through all the nans
            df1[f'{scol}MA'] = df1[scol]  #  work on a copy
            
            fig,ax = plt.subplots(2,1,figsize=(15,5),sharex=True)
            df1['dh'] = df1['Dates'].diff().apply(lambda x: x/np.timedelta64(1,'h'))    
            # salinity gradient
            df1['dSdh'] = df1[f'{scol}MA'].diff() / df1['dh']
            # ax[0].plot(df1['Dates'],df1[scol].diff(),'.-')
            # ax[0].grid()
            # ax[1].plot(df1['Dates'],df1['dh'],'.-')
            # ax[1].grid()
            # ax[2].plot(df1['Dates'],df1['dSdh'],'.-')
            # ax[2].grid()
            ax[0].plot(df1['Dates'],df1['dSdh'],'r.-')
            ax[0].set_title(f'Salinity change in psu/hr for {scol}')
            ax[1].plot(df1['Dates'],df1[f'{scol}MA'],'r.-')
            print('Before',np.int(df1[f'{scol}MA'].count()),f'{spikeLimit:.2f}')
            # df1.loc[(df1['dSdh'].abs()>spikeLimit),scol] = np.nan   # USED FOR WHEN WE ARE NOT TESTING LIMITS
            # dfLimit.loc[ii,f'{spikeLimit:.2f}'] = np.int(df1[scol].count())
            # ax[1].plot(df1['Dates'],df1[scol],'b.-',ms=6)
            df1.loc[(df1['dSdh'].abs()>spikeLimit),f'{scol}MA'] = np.nan
            dfLimit.loc[ii,f'{spikeLimit:.2f}'] = np.int(df1[f'{scol}MA'].count())
            ax[1].plot(df1['Dates'],df1[f'{scol}MA'],'b.-',ms=6)
            # interpolate through nans, mask out original nans
            df1[f'{scol}MA'].interpolate(method='linear',inplace=True)
            df1.loc[(df1['mask']),f'{scol}MA'] = np.nan
            print('After',df1[f'{scol}MA'].count())
    
            ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[spikeLimit,spikeLimit],'--',color='gray')
            ax[0].plot([df1['Dates'].iloc[0],df1['Dates'].iloc[-1]],[-1*spikeLimit,-1*spikeLimit],'--',color='gray')
            ax[0].set_xlim([df1['Dates'].iloc[0],df1.loc[(df1['dSdh'].last_valid_index()),'Dates']])  
            ax[1].plot(df1['Dates'],df1[f'{scol}MA'],'g.',ms=3)
            ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            if dt1 is not None:
                ax[0].set_xlim([dt1,dt2])
            ax[1].set_title(f'Salinity original(r), after removal >{spikeLimit:.2f}(b), after interpolation(g--), {scol}')
            plt.savefig(f'{figspath}/{scol}spikes{spikeLimit:.2f}.png')    
            plt.show()
            # print(dfLimit.head())
            # exit(-1)
            df1.drop(['dSdh','dh',f'{scol}MA'],axis=1,inplace=True)
        df1.drop(columns=['mask'],inplace=True)
    dfLimit.to_csv(f'{figspath}/SspikeLimits.csv')
    
    return df1        



# def makeL2(df,bid,path):
#     binf = BM.BuoyMaster(bid)
#     filename = f'{path}/UTO_{binf['name'][0]}-{int(binf['name'][1]):02}
