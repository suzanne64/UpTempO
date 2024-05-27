#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 12:36:50 2022

@author: suzanne
"""

import netCDF4 as nc
import numpy as np
import xarray as xr
import UpTempO_BuoyMaster as BM
import pandas as pd
from scipy import interpolate
from scipy import signal
import matplotlib.pyplot as plt
import datetime as dt
import os, shutil
import UpTempO_BuoyMaster as BM
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time


t1 = time.perf_counter()
# use global gebco bathymetry for UTO plots
# filenc = '/Users/suzanne/gebco/GEBCO_2019.nc'
filenc = '/Users/suzanne/gebco/GEBCO_2023.nc'
fnc = xr.open_dataset(filenc)
# print(fnc)

eelat = fnc['lat'].values
indn = np.argwhere(eelat>=50).flatten()
eelat = eelat[indn]
eelon = fnc['lon'].values
# eelon[eelon<0] += 360
# eelon = np.roll(eelon,int(eelon.shape[0]/2))


eelev = fnc['elevation'].values 
eelev = eelev[indn,:]
# eelev = np.roll(eelev,int(eelon.shape[0]/2),axis=1)
# smooth
eelevsm = signal.medfilt2d(eelev,9)

# reduce array sizes
inc = 10
eelat = eelat[::10]
eelon = eelon[::10]
eelev = eelevsm[::10,::10]

bscalegray=[50.,100.,500.,1000.,2000.,3000.]
bscaleblack=[28.,60.]
deepfillcol='beige' 

fig,ax = plt.subplots(1,1,figsize=(10,6))
ax = plt.subplot(1,1,1, projection=ccrs.NorthPolarStereo(-45))
ax.coastlines(zorder=3)
ax.contour(eelon,eelat,-eelev,bscalegray,colors='gray',linewidths=.5,transform=ccrs.PlateCarree())
ax.contour(eelon,eelat,-eelev,bscaleblack,colors='k',linewidths=1,transform=ccrs.PlateCarree())
ax.contourf(eelon,eelat,-eelev,[3000.,9000.],colors=deepfillcol,transform=ccrs.PlateCarree())
ax.set_title(f"GEBCO 2023 after reduction, smoothed, every {inc}th grid cell")
plt.show()

# save reduced grid
fileout = '/Users/suzanne/Google Drive/UpTempO/bathymetry/GEBCO_2023_arctic.nc'
if os.path.exists(fileout):
    os.remove(fileout)  # 'w' doesn't clobber 
with nc.Dataset(fileout,'w',format='NETCDF4') as ncfile:
    ncfile.createDimension('x',eelon.shape[0])
    ncfile.createDimension('y',eelat.shape[0])
    elon = ncfile.createVariable('elon','float32',('x',));  elon[:] = eelon
    elat = ncfile.createVariable('elat','float32',('y',));  elat[:] = eelat
    elev = ncfile.createVariable('elev','float32',('y','x'));  elev[:] = eelev

# read it back in
ds = xr.open_dataset('/Users/suzanne/Google Drive/UpTempO/bathymetry/GEBCO_2023_arctic.nc')
elat = ds['elat'].values
elon = ds['elon'].values
elev = ds['elev'].values
print(elat.shape,elon.shape,elev.shape)
bscalegray=[50.,100.,500.,1000.,2000.,3000.]
bscaleblack=[28.,60.]
deepfillcol='beige' 

fig,ax = plt.subplots(1,1,figsize=(10,6))
ax = plt.subplot(1,1,1, projection=ccrs.NorthPolarStereo(-45))
ax.coastlines(zorder=3)
ax.contour(elon,elat,-1*elev,bscalegray,colors='gray',linewidths=.5,transform=ccrs.PlateCarree())
ax.contour(elon,elat,-1*elev,bscaleblack,colors='k',linewidths=1,transform=ccrs.PlateCarree())
ax.contourf(elon,elat,-1*elev,[3000.,9000.],colors=deepfillcol,transform=ccrs.PlateCarree())
ax.plot(-178,58,'r*',transform=ccrs.PlateCarree())
ax.set_title("GEBCO 2023 after reading back in")
# arctic
ax.set_extent([-2.0e6,2.0e6,-2.55e6,2.55e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
# western arctic with Bering
ax.set_extent([-2.0e6,2.0e6,0,3.5e6],crs=ccrs.NorthPolarStereo(central_longitude=0))
plt.show()
t2=time.perf_counter()
print(t2-t1)


exit()

# what = ['5.00']
# whatf = [float(item) for item in what]
# print(whatf[-1])
# exit(-1)

mfiles = os.listdir('swift_telemetry/')
for item in mfiles:
    if item.endswith('.mat'):
        print(item)
        shutil.copy(f'swift_telemetry/{item}',f'swift_telemetry/latest_matfiles/{item}')        
exit()


columns = ['D0','T0','T1']
df = pd.DataFrame(columns=columns)
df['D0'] = [5,np.nan,6]
df['T0'] = [1,2,3]
df['T1'] = [1.2,2.2,3.3]
print(df.head())
print()
df.loc[(np.isnan(df['D0'])) & (~np.isnan(df['T0'])),'D0'] = 10
print(df.head())
print()
print(df.loc[[2]])
exit()

# columns = ['when','t0','t1']
# dfSpikeRem = pd.DataFrame(columns=columns)
# dfSpikeRem['when'] = ['% Removed','Before','After']
# dfSpikeRem.set_index('when',inplace=True)
# print(dfSpikeRem.head())
# dfSpikeRem['t0'].loc['Before'] = 2
# dfSpikeRem['t0'].loc['After'] = 1
# dfSpikeRem['t1'].loc['Before'] = 77
# dfSpikeRem['t1'].loc['After'] = np.nan
# dfSpikeRem['t0'].loc['% Removed'] = np.int((dfSpikeRem['t0'].loc['Before'] - dfSpikeRem['t0'].loc['After']) / dfSpikeRem['t0'].loc['Before'] *100)
# print()
# print(dfSpikeRem.head())
# print()
# print(dfSpikeRem.T.head())
# print(int(dfSpikeRem['t1']))
# dfSpikeRem.T.to_csv('what.csv')
# exit(-1)
# nan = np.nan
# t = [nan,nan,nan]
# if np.isnan(t).all():
#     print('ok')
# exit(-1)
tdepths = [0.14,0.44,5.0]
arr = np.array([1,np.nan,2,])
arrd = np.array([0.14,0.45,5])
arrdi = np.arange(0,int(tdepths[-1])+1)
print(arr[~np.isnan(arr)])
print(arrd[~np.isnan(arr)])
print(arrdi)
arri = np.interp(arrdi,arrd[~np.isnan(arr)],arr[~np.isnan(arr)])
print(arri)
exit(-1)
ok = ~np.isnan(arr)
xp = ok.ravel().nonzero()[0]
fp = arr[~np.isnan(arr)]
x  = np.isnan(arr).ravel().nonzero()[0]  # what we want to fill
print(arr)
print(ok)
print(xp)
print(fp)
print(x)
# Replacing nan values
arr[np.isnan(arr)] = np.interp(x, xp, fp)
print(arr)

exit(-1)
df = pd.DataFrame(columns=['Lon','Lat','T'])
if ('Lat' or 'wtf') in df.columns:
    print('wtf')
    exit(-1)
df['Lon'] = [180,-999,176]
df['Lat'] = [76,77,120]
df['T'] = [1,2,3]
print(len(df.loc[(df['Lat']>100),'Lat']))
exit(-1)


# L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
# L2path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2'
# figspath = '/Users/suzanne/Google Drive/UpTempO/level2'

# bid = '300234067936870'
# binf = BM.BuoyMaster(bid)
# abbv=binf['imeiabbv']

# # make unique buoy figures path
# try:
#     figspath = os.path.join(figspath,f'{binf["name"][0]}_{int(binf["name"][1]):02d}')
# except:
#     figspath = os.path.join(figspath,f'{binf["name"][0]}_{binf["name"][1]}')

# try:
#     level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'
# except:
#     level2Draft = f'{figspath}/UTO_{binf["name"][0]}-{binf["name"][1]}_{bid}_L2.dat'

# # Data file
# # copy to virtual webpage
# shutil.copy(f'{figspath}/{level2Draft}','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL2/{level2Draft}')
# # copy to dir where L2 data files live.
# shutil.copy(f'{figspath}/{level2Draft}','/Users/suzanne/Google Drive/UpTempO/UPTEMPO/WebDATA/LEVEL2/{level2Draft}')

# # Level 2 Webpage Plots
# for quan in ['Temp','Pressure','Submergence','Salinity','Tilt','Velocity']:
#     if quan ~= 'Submergence':
#     try:
#         shutil.copy(f'{figspath}/{quan}Series{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/{quan}Series{abbr}.png')
# try:
#     shutil.copy(f'{figspath}/PressureSeries{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/PressureSeries{abbr}.png')
# shutil.copy(f'{figspath}/TempSeries{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/TempSeries{abbr}.png')
# shutil.copy(f'{figspath}/TempSeries{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/TempSeries{abbr}.png')
# shutil.copy(f'{figspath}/TempSeries{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/TempSeries{abbr}.png')
# shutil.copy(f'{figspath}/TempSeries{abbv}L2.png','/Users/suzanne/uptempo_virtWebPage/UpTempO/WebPlots/TempSeries{abbr}.png')



# exit(-1)
# df1 = pd.DataFrame(columns=['Lon','T'])
# df1['Lon'] = [180,-999,176]
# df1['T'] = [1,2,3]
# print(df1.head())
# print()
# df1 = df1[df1.Lon != -999]
# print(df1.head())

# exit(-1)

# line = '% 6 = Ocean Pressure (dB) at Sensor #1(Nominal Depth = 20.0 m)'
# print(line.split('=',1)[-1])  # split on first instance of '='
# exit(-1)

# tdepths=[0,2.5,5,7.5,10,15]
# RA = 12
# pdepths = [0,20,40,60]

# print([ii for ii,item in enumerate(tdepths) if item>(pdepths[1]-RA)][0])

# exit(-1)

df1 = pd.DataFrame(columns=['D0','D1','D2','D3','FirstTpod'])
Dtcols = ['D0','D2','D3']
Dscols = ['D1','D3']
# df1['FirstTpod'] = [0,4,2]
df1['D0'] = [0.14,0.14,0.14,0.14]
df1['D1'] = [0.39,0.36,0.40,0.15]
df1['D2'] = [0.45,0.39,0.35,0.17]
df1['D3'] = [5.1,5,4.9,2.0]
df1['FirstTpod'] = [0,1,1,2]
df1['FirstSpod'] = [0,1,1,0]

df1['Dsst']     = df1.apply(lambda row: (row[Dtcols[int(row['FirstTpod'])]]),axis=1)
df1['Dssstest'] = df1.apply(lambda row: (row[Dscols[int(row['FirstSpod'])]]),axis=1)

# df1['wtf'] = df1.apply(lambda row: (row[df1[Dscols].sub(df1[Dtcols[df1['FirstTpod']]])]),axis=1)
# print(df1)
print()
# print(df1[Dscols].sub(df1[Dtcols[df1['FirstTpod']]],axis=0))
# exit(-1)
# for jj in range(len(df1)):
jj=3
print(df1)
# res = list(filter(lambda x: x>df1['Dsst'].iloc[jj],list(df1[Dscols].iloc[jj])))#[0]
# res = [(lambda x: x>df1['Dsst'].iloc[jj]) for x in list(df1[Dscols].iloc[jj])#[0]
# print(res)
# exit(-1)
print(df1['Dsst'].iloc[jj])
print(df1[Dscols].iloc[jj])
what = list(df1[Dscols].iloc[jj].ge(df1['Dsst'].iloc[jj]))
# print(Dscols[i for i, x in enumerate(what) if x][0])
exit(-1)
print()
print(df1.apply(lambda row: (row[df1[Dscols]].gt(df1['Dsst'])),axis=1))
# df1['FirstTpod'] = df1.apply(lambda row: (row[Tcols].gt(-1.9).idxmax()[1:]),axis=1)
# print(df1[Dscols].iloc[jj] >= df1['Dsst'].iloc[jj])
# print(df1)
# print(df1.apply(lambda row: (row)
exit(-1)







print('depth at FWT',df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj])
print('depths of Scols',df1[Dscols].iloc[jj].values)
# diffs = df1[Dscols].iloc[jj].values - df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj]
df1['diff'] = df1[Dscols].iloc[jj].sub(df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj]) #.ge(0)
# print('ge',df1[Dscols].iloc[jj].ge((df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj])) )#.ge(0)
# print(df1[Dscols[df1[Dscols].iloc[jj].sub(df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj]).ge(0)]])
# print((df1[Dscols].iloc[jj].values - df1[Dtcols[df1['FirstTpod'].loc[jj]]].iloc[jj]).gt(0))
print(df1)
# df1['Dsss'] = df1.apply(lambda row: (row[]),axis=1)
# print(df1.head())
exit(-1)
df1['Dsss'] = df1.apply(lambda row: (row[Dscols]>=row[Dtcols[int(row['FirstTpod'])]]),axis=1)

# df1 = pd.DataFrame(columns=['D0','D1','D2','D3','D4','D5','ridgedPressure'])
# # df1['FirstTpod'] = [0,4,2]
# df1['D0'] = [0,0.51,0]
# df1['D1'] = [2.5,2.4,2.4]
# df1['D2'] = [5.1,5,4.9]
# df1['D3'] = [7.3,7.3,7.5]
# df1['D4'] = [9.9,10,10]
# df1['D5'] = [14.9,15.2,15.1]
# df1['T0'] = [0,0.51,0]
# df1['T1'] = [-0.4,-0.4,-0.4]
# df1['T2'] = [-0.55,-0.5,-0.5]
# df1['T3'] = [-0.6,np.nan,-0.65]
# df1['T4'] = [-1,-1,np.nan]
# df1['T5'] = [-1.2,-1.2,-1.2]
# df1['ridgedPressure'] = [0,15,12]
# df1['FirstTpod'] = [2,2,2]
# # df1['sst'] = 

# Dcols = [col for col in df1.columns if col.startswith('D')]
# Tcols = [col for col in df1.columns if col.startswith('T')]

# # not depths,but from tdepths
# print(pd.Series(tdepths).gt(pdepths[1]-df1['ridgedPressure'].iloc[1]).idxmax())
# print()
# df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[1]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
# # df1['FirstTpod']=df1.apply(lambda row: int(pd.Series(tdepths).gt(pdepths[0]-row['ridgedPressure']).idxmax()) if row['ridgedPressure']>0 else int(row['FirstTpod']),axis=1)
# # df1['FirstTpod']=df1.apply(lambda row: int([ii for ii,item in enumerate(tdepths) if item>(pdepths[1]-row(df1['ridgedPressure']))][0]) if row(df1['ridgedPressure'])>0 else int(row['FirstTpod']),axis=1)
# df1['sst'] = df1.apply(lambda row: (row[Tcols[int(row['FirstTpod'])]]),axis=1)
# print(df1.head())
# print()

# for ii,row in df1.iterrows():
#     if df1['sst'].isnull().iloc[ii]:
#         while df1['sst'].isnull().iloc[ii] and df1['FirstTpod'].iloc[ii]<len(tdepths)-1:
#             print(ii,df1['sst'].iloc[ii],df1['FirstTpod'].iloc[ii])
#             df1['FirstTpod'].iloc[ii] += 1
#             df1['sst'].iloc[ii] = df1[Tcols[df1['FirstTpod'].iloc[ii]]].iloc[ii]
#             print(ii,df1['sst'].iloc[ii],df1['FirstTpod'].iloc[ii])
#             # input('Press enter to continue...')

# print(df1.head())
# print()
# exit(-1)

# Dcols = [col for col in df1.columns if col.startswith('D')]
# print(Dcols)
# for ii,row in df1.iterrows():
#     df1['Dsst'].iloc[ii] = df1[f"D{df1['FirstTpod'].iloc[ii]}"].iloc[ii]
# # df1['Dsst'] = df1.apply(lambda row: row[Dcols])
# # row[Tcols].gt(-1.9).idxmax()[1:])),axis=1))
# print(df1.head())
# exit(-1)
pdepths = [20,40,60]
tdepths = [0, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 50, 60]
df1 = pd.DataFrame(columns=['T0','T1','T2','T3','T4','T5'])
df1['FirstTpod'] = 0
df1['WaterIce'] = [2,1,2,1,1]
df1['T0'] = [-10,np.nan,1,-3,-4]
df1['T1'] = [-3,-4,1,-2,-0.9]
df1['T2'] = [-2,-1,1.2,-2,np.nan]
df1['T3'] = [-1,-1,1.4,-1,np.nan]
df1['T4'] = [0,0,1.6,0,np.nan]
df1['T5'] = [0,0,1.8,0,np.nan]
Tcols = [x for x in df1.columns if x.startswith('T')]

df1['FirstTpod'] = df1.apply(lambda row: (int(row[Tcols].gt(-1.9).idxmax()[1:])),axis=1)
print(df1.head())
print()
# if FWT = 0, but W/I says we're near ice, set FWT=1
df1.loc[(df1['FirstTpod']==0) & (df1['WaterIce']==1),'FirstTpod'] = 1
print(df1.head())
exit(-1)

# print(df1[Tcols].iloc[0].gt(-1.9).idxmax()[1:])
# exit(-1)
# print(Tcols)
# df1['metersofRidge'] = pdepths[0]-df1['ridgedPressure']
df1['metersofRidge'] = [0,8,5]
# the following doesn't work if metersofRidge = 0.
# df1['FirstTpod'] = df1.apply(lambda row: sum(x<=row['metersofRidge'] for x in tdepths),axis=1)    
# df1['FirstTpod'] = df1.apply(lambda row: sum(x<=-1.9 for x in row[Tcols]),axis=1)
df1['FirstTpod'] = df1.apply(lambda row: (row[Tcols].gt(-1.9).idxmax()[1:]),axis=1)
# for ii,row in df1.iterrows():
#     df1['sst'] = df1[Tcols[3]]
df1['sst'] = df1.apply(lambda row: (row[Tcols[np.int(row['FirstTpod'])]]),axis=1)
print(df1.head())
exit(-1)


# df1['FWT'] = df1[Tcols].ge(-1.9).idxmax()[1:]
for ii,row in df1.iterrows():  
    # print(df1[['T0','T1']].iloc[ii])    
    df1['FirstTpod'].iloc[ii] = pd.to_numeric(df1[Tcols].iloc[ii].ge(-1.9).idxmax()[1:],downcast='integer')
    fwt = np.int(df1.loc[ii,'FirstTpod'])
    df1.loc[ii,'sst' ] = df1.loc[ii,Tcols[np.int(df1.loc[ii,'FirstTpod'])]]
    

print(df1.head())
exit(-1)

tdepths = [0.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0]
pdepths = [20.0, 40.0, 60.0]

df1 = pd.DataFrame(columns=['ridgedPressure','metersofRidge','FirstTpod'])
df1['ridgedPressure'] = [15,12.9,11.9,13,14,16]
df1['metersofRidge'] = pdepths[0]-df1['ridgedPressure']
df1['FirstTpod'] = df1.apply(lambda row: sum(x<=row['metersofRidge'] for x in tdepths),axis=1)    

print(df1.head(6))

exit(-1)
# ils = [1]#,2,3]
# for ii,item in enumerate(ils):
#     print(item)
# fig1,ax1 = plt.subplots(1,1,figsize=(15,5),sharex=True)
# for item in ax1.ravel():
#     print(item)
# exit(-1)

# tdepths = [0.0, 4.3, 10]
# tdiffs = [tdepths[-1] - item for item in tdepths]
# pmeas = 13.2
# print([pmeas - item for item in tdiffs])
# exit(-1)


what = [20,0,60]
print(what)
deep = 0
what[:1] = 10
print(what)
exit(-1)
fig1,ax1 = plt.subplots(len(what),1)
for ii, ax in enumerate(np.array(ax1).reshape(-1)):  #fig1.axes
    ax.set_ylabel(f'{what[ii]}')
plt.show()
exit(-1)


df1 = pd.DataFrame(columns=['Dates'])
df1['Dates'] = pd.date_range(dt.datetime(1950,1,4),dt.datetime(1950,1,7),freq='60min')

df1['dayssince'] = df1['Dates'].apply(lambda x: (x-dt.datetime(1950,1,1)).days + (x-dt.datetime(1950,1,1)).seconds/86400)
print(df1['dayssince'])
exit(-1)

print('500',)
print(('500',))
print(['500'])
print(['500',])

exit(-1)
minYs=[-7.6, -np.inf, -17.2]
print([x for x in minYs if x != -np.inf])
print()
exit(-1)
print(-np.inf==float('-inf'))
exit(-1)
df=pd.DataFrame(columns=['P1','P2','P3'])
df['P1'] = [20,19,np.nan,np.nan]
df['P2'] = [40,39,39.5,38]
df['P3'] = [59,60,58,57]
Pcols = [col for col in df.columns if col.startswith('P')]
print(Pcols)
pdepths=[0,20,40,60]
tdepths=[0, 1, 4, 6.5, 9, 12, 14.5, 17, 20, 25, 30, 35, 40, 45, 50, 55, 60]

for ii,row in df.iterrows():
    pmeas = [df[col].iloc[ii] for col in Pcols]
    print('pmeas',pmeas)
    pmeas.insert(0,0.0)
    # if df[Pcols].iloc[ii].isnull().values.any():
    valid = np.where(~np.isnan(pmeas))[0].tolist()
    print([pmeas[i] for i in valid])
    print([pdepths[i] for i in valid])
    fi = interpolate.interp1d([pdepths[i] for i in valid],[pmeas[i] for i in valid],fill_value = 'extrapolate')
    tcalcdepths = fi(tdepths)
    fig7,ax7 = plt.subplots(1,1,figsize=(10,6))
    ax7.plot([-1*x for x in tdepths],[-1*x for x in tdepths],'b.-')
    ax7.plot([-1*x for x in tdepths],-1*tcalcdepths,'r.-')
    # ax7.plot(-1*tdepths,-1*tdepths,'b.-')
    # ax7.plot(-1*tdepths,-1*tcalcdepths,'r.-')
    plt.show()
exit(-1)
    # print()

exit(-1)
# df1 = pd.DataFrame(data=np.arange(26),columns=['metersofRidge'])
# tdepths = [0,2.5,5.0,7.5,10,15,20,25]
# print(sum(x<8 for x in tdepths))
# # exit(-1)
# df1['numZeros'] = df1.apply(lambda x: sum(x<=df1['metersofRidge'] for x in tdepths),axis=0)
# print(df1.head(10))
# exit(-1)

pdepths = [0,25]
tdepths = [0,2.5,5.0,7.5,10,15,20,25]
nomDiffs = np.diff(tdepths)

pmeas = [0,23.5]
pdepthsRidged = [0,24]
fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')
offset = pdepths[1] - pdepthsRidged[1]
tdepthsRidged = [x- offset for x in tdepths]  #( df1['P1corr'].iloc[ii] - pdepths[1])
tcalcdepths = fi(tdepthsRidged)
tcalcdepths[tcalcdepths<0] = 0
calcDiffs = np.diff(tcalcdepths)
print(nomDiffs)
print(f'ridged Press {pdepthsRidged[1]}',calcDiffs)
print()
# print('ridged Press 24',nomDiffs-calcDiffs)
# set calculated depths 'shallower' than FWT as 0
# for dcol in Dcols[:numZeros]:
#     df1.loc[index,dcol] = 0
# df1.loc[index,'FirstTpod'] = numZeros


fig,ax = plt.subplots(1,2,sharey=True)
ax[0].plot([-1*x for x in tdepths],[-1*x for x in tdepths],'.--',color='g')
ax[0].plot([-1*x for x in tdepths],[-1*x for x in tdepthsRidged],'b.--')
ax[0].plot([-1*x for x in tdepths],-1*tcalcdepths,'r.-')
ax[0].set_title(f'RidgedPressure {pdepthsRidged[1]} db')

pmeas = [0,23.5]
pdepthsRidged = [0,23]
fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')
offset = pdepths[1] - pdepthsRidged[1]
tdepthsRidged = [x- offset for x in tdepths]  #( df1['P1corr'].iloc[ii] - pdepths[1])
tcalcdepths = fi(tdepthsRidged)
tcalcdepths[tcalcdepths<0] = 0
calcDiffs = np.diff(tcalcdepths)
print()
print(f'ridged Press {pdepthsRidged[1]}',calcDiffs)
# exit(-1)
ax[1].plot([-1*x for x in tdepths],[-1*x for x in tdepths],'.--',color='g')
ax[1].plot([-1*x for x in tdepths],[-1*x for x in tdepthsRidged],'b.--')
ax[1].plot([-1*x for x in tdepths],-1*tcalcdepths,'r.-')
ax[1].set_title(f'RidgedPressure {pdepthsRidged[1]} db')


for axi in ax:
    axi.set_yticks(np.arange(-25,1),minor=True)
    axi.yaxis.grid(True,which='minor') #ax.grid()
    axi.set_yticks(np.arange(-25,1,5),minor=False)
    axi.yaxis.grid(True,which='major',color='k') #ax.grid()
    axi.set_xlabel('nominal tdepths')
plt.show()
exit(-1)
# if not df1['ridged'].iloc[ii] and not df1['dragging'].iloc[ii]:
#     pnoms = [df1[Pcols[0]].iloc[ii]]
#     pnoms.extend(pdepths[1:])
#     fi = interpolate.interp1d(pdepths,pmeas,fill_value = 'extrapolate')
#     tinvolved = tdepths
#     tcalcdepths[ii,:] = fi(tinvolved)
    
# elif df1['ridged'].iloc[ii]:
#     deepestZero = df1['FirstTpod'].iloc[ii]
#     pdepthsRidged = [-1*df1a['ridgedPressure'].iloc[ii]] #[x-tdepths[deepestZero-1] for x in pdepths[1:]]
#     pdepthsRidged.insert(0,0)
#     # print(pmeas)
#     # print(pdepthsRidged)
#     # exit(-1)
#     fi = interpolate.interp1d(pdepthsRidged,pmeas,fill_value = 'extrapolate')
#     offset = pdepths[1] - pdepthsRidged[1]
#     tdepthsRidged = [x- offset for x in tdepths]  #( df1['P1corr'].iloc[ii] - pdepths[1])
#     # print(tdepthsRidged)
#     # print(fi(tdepthsRidged))
#     # print(deepestZero)
    
#     tcalcdepths[ii,:] = fi(tdepthsRidged)
#     tcalcdepths[ii,:deepestZero] = 0
#     # print(tcalcdepths[ii,:])



df1=pd.DataFrame(columns=['T0','TspikeMag','TspikeLeft','TspikeRight'])
df1['T0'] = [0,1,2,-1,-1,-2,0,1,1,3,2]
# removing temperature spikes
df1['TspikeLeft'] = df1['T0'].diff()
df1['TspikeRight'] = df1['T0'].iloc[::-1].diff()
df1['TspikeMag'] = 0
# print(np.isnan(df1['TspikeLeft'].iloc[:2]))
# exit(-1)

for ii,row in df1.iterrows():
    # print(row)
    # print(np.sign(df1['TspikeLeft'].iloc[ii]))
    # print(np.sign(df1['TspikeRight'].iloc[ii]))
    # print(~np.isnan(df1['TspikeLeft'].iloc[ii]),np.isnan(df1['TspikeRight'].iloc[ii]))
    if ~np.isnan(df1['TspikeLeft'].iloc[ii]) and ~np.isnan(df1['TspikeRight'].iloc[ii]):
        print(ii,'not nans')
        if np.sign(df1['TspikeLeft'].iloc[ii])==1.0 and np.sign(df1['TspikeRight'].iloc[ii])==1.0:
            print(ii,'same sign')
            print(df1['TspikeLeft'].iloc[ii],df1['TspikeRight'].iloc[ii])
            df1['TspikeMag'].iloc[ii] = np.min((df1['TspikeLeft'].iloc[ii],df1['TspikeRight'].iloc[ii]))
            
        elif np.sign(df1['TspikeLeft'].iloc[ii])==-1.0 and np.sign(df1['TspikeRight'].iloc[ii])==-1.0:
            print(ii,'same sign')
            print(df1['TspikeLeft'].iloc[ii],df1['TspikeRight'].iloc[ii])
            df1['TspikeMag'].iloc[ii] = np.max((df1['TspikeLeft'].iloc[ii],df1['TspikeRight'].iloc[ii]))

print(df1)

exit(-1)


L1path = '/Users/suzanne/uptempo_virtWebPage/UpTempO/WebDATA/LEVEL1'
path = '/Users/suzanne/Google Drive/UpTempO/UPTEMPO/WebData/LEVEL2'
#bid = '300234063993850'    # 2016 06
bid = '300234064709310'    # 2017-01
binf = BM.BuoyMaster(bid)
filename1 = f'{L1path}/UpTempO_{binf["name"][0]}_{int(binf["name"][1]):02d}_{binf["vessel"]}-FINAL.dat'
filename2 = f'{path}/UTO_{binf["name"][0]}-{int(binf["name"][1]):02d}_{bid}_L2.dat'

f1 = open(filename1,'r')
f2 = open(filename2,'w')

lines = f1.readlines()
for ii,line in enumerate(lines):
    if line.startswith('%') and '%END' not in line:
        f2.write(line)




        
f1.close()
f2.close()
exit(-1)
    # f.write(f'%UpTempO {binf["name"][0]} #{int(binf["name"][1])}\n')
    # f.write(f'%Iridium ID: {bid}\n')
    # f.write(f'%WMO: {binf["wmo"]}\n')
    # f.write(f'%MANUFACTURER: {binf["brand"]}\n')
    # f.write(f'%DATE DEPLOYED: {binf["deploymentDate"]}\n')
    #
    # if binf["deploymentLat"]>0:
    #     hemilat = 'N'
    # else:
    #     hemilat = 'S'
    # if binf["deploymentLon"]>0:
    #     hemilon = 'E'
    # else:
    #     hemilon = 'W'
    # f.write(f'%POSITION DEPLOYED: {binf["deploymentLat"]:.2f}{hemilat} {binf["deploymentLon"]:.2f}{hemilon}\n')
    # # f.write(f'%DATE OF LAST TRANSMISSION: {df.loc['Year']}')
    # f.write(f'%\n')
    #
    # f.write(f'%DATA COLUMNS:\n')


exit(-1)

filegeb = '/Users/suzanne/gebco/GEBCO_2019.nc'
blat=73.
blon=150.
ds = xr.open_dataset(filegeb)
bathy = ds.sel(lon=slice(blon-10,blon+10),lat=slice(blat-5,blat+5)).load()
print(bathy.elevation.shape)
print(bathy.lon)
print(bathy.keys())
