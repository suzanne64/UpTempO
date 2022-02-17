#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:48:43 2022

@author: suzanne
"""
import re
import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt
import CalculateDepths as CD
import UpTempO_BuoyMaster as BM

level1Path = '/Volumes/GoogleDrive/My Drive/UpTempO/UPTEMPO/WebData/LEVEL-1'
level2Path = '/Volumes/GoogleDrive/My Drive/UpTempO/UPTEMPO/WebData/LEVEL-2'

bid='300234064735100'
binf = BM.BuoyMaster(bid)

# level1File = 'UpTempO_'+binf['name'][0]+'_'+binf['name'][1]+'_'+binf['vessel']+'-FINAL.dat'
level1File = f'UpTempO_{binf["name"][0]}_{int(binf["name"][1]):02d}_{binf["vessel"]}-FINAL.dat'

baseheader ={'year':'Year',         # key from Level 1, value from ProcessedRaw and used here
             'month':'Month',
             'day':'Day',
             'hour':'Hour',
             'Latitude':'Lat',
             'Longitude':'Lon'}
columns = ['Year','Month','Day','Hour','Lat','Lon']

pdepths = [0.]
tdepths = []
pcols = []
pnum = 1
tnum = 0  # 
# read in level-1 header
with open(f'{level1Path}/{level1File}','r') as f:
    lines = f.readlines()
    for ii,line in enumerate(lines):
        # print(ii,line)
        if line.startswith('%'):
            if 'Ocean Pressure' in line:
                pcols.append( int(re.search(r'\% (.*?)= Ocean Pressure',line).group(1).strip(' ')) )
                columns.append(f'P{pnum}')                
                pnum += 1
                pdepths.append( float(re.search(r'Nominal Depth = (.*?) m\)',line).group(1).strip(' ')) )
            if 'Temperature at nominal depth' in line:
                tdepths.append( float(re.search(r'at nominal depth (.*?) \(m\)',line).group(1).strip(' ')) )
                columns.append(f'T{tnum}')  
                tnum += 1
            if 'Sea Level Pressure' in line:
                columns.append('BP')
            if 'Battery Voltage' in line:
                columns.append('BATT')
            if 'Submergence Percent' in line:
                columns.append('SUB')
            if '%END' in line:
                data = np.array([ [float(item) for item in lines[jj].split()] for jj in np.arange(ii+1,len(lines))]) #ii+1,len(lines)+1)]
                df = pd.DataFrame(data=data,columns=columns)
                # print((df == -999).sum())
                # print((df == -99).sum())
                df[df==-999] = np.NaN
                df[df==-99] = np.NaN
                df.insert(6,'P0',0)
                pdepths = np.array(pdepths)
                tdepths = np.array(tdepths)
     

# dftest = pd.DataFrame({'Year':[2019,2018,2018,2020,2020],
#                       'Month':[1,2,2,6,6],
#                       'Day':[3,3,3,23,2],
#                       'T1':[0,2.5,2.5,np.NaN,7]})
# # print(dftest)
# # dftest.drop_duplicates(inplace=True)
# # dftest=dftest.reset_index(drop=True)
# # print(dftest)
# # print()
# # # print((dftest==3).sum())
# dft=pd.to_datetime(dftest[['Year','Month','Day']])
# print(dft.head())

# dftest.sort_values(by=['Year','Month','Day'],inplace=True)
# dftest=dftest.reset_index(drop=True)
# dft=pd.to_datetime(dftest[['Year','Month','Day']])
# print(dft.head())
# # print(dftest)
# # # print(num)
# exit(-1)


print(df.head())
print('number of rows',len(df.index))
print()
print()

# implement data clean up (see weCode/LEVEL_2_IDL_CODE/READ_ME.txt)
# remove duplicate lines
df.drop_duplicates(inplace=True)
df=df.reset_index(drop=True)  # pandas would keep the orig index if didn't drop=True

# all -99s and -999s have been set to np.NaN, reset NaNs to -999s when writing Level-2 ascii

# sort by increasing date, over four cols
df.sort_values(by=['Year','Month','Day','Hour'],inplace=True)
df=df.reset_index(drop=True)
# add dates column for plotting
df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
print(df.head())

Tcols = [col for col in df.columns if col.startswith('T')]
print(Tcols)
cList=['k','purple','blue','deepskyblue','cyan','limegreen','lime','yellow','darkorange','orangered','red','saddlebrown','darkgreen','olive','goldenrod','tan','slategrey']

fig,ax = plt.subplots(1,1,figsize=(20,10))
for ii,tcol in enumerate(Tcols):
    ax.plot(df['Dates'],df[tcol],cList[ii])
plt.show()
exit(-1)


# calculating depths by interpolation                
pressureCols = [col for col in df.columns if col.startswith('P')]
CalcDepthCols = [f'CalcDepth{col}' for col in df.columns if col.startswith('T')]
print(CalcDepthCols)

# make dataFrame for calculated depths of the thermistors
# dft = pd.DataFrame(columns=CalcDepthCols)
tcalcdepths = []
for ii in range(len(df)):
    fi = interpolate.interp1d(pdepths,df[pressureCols].iloc[ii])            
    # temperatureDepths.vstack(fi(tdepths))
    tcalcdepths.append(fi(tdepths))

tcalcdepths = np.asarray(tcalcdepths)
dftcalcdepths = pd.DataFrame(data=tcalcdepths,columns=CalcDepthCols)     
print(dftcalcdepths.head())      
# fig, ax = plt.subplots(1,2)
# ax[0].plot(-1*pdepths,-1*df[pressureCols].iloc[0],'ro',linewidth=2,label='P Depth Meas')
# ax[0].plot(-1*tdepths,-1*tdepths,'k--')
#     ax[0].plot(-1*tdepths,-1*temperatureDepths,'b*',label='T Depth Interp')      
#     ax[0].legend(loc='upper left')  
#     ax[0].set_ylabel('Depth, [m]')
#     ax[1].plot(tdepths,temperatureDepths-tdepths,'b*',label='differences')      
#     ax[1].legend()  
#     plt.show()
#     exit(-1)
                
                

# CD.CalculateDepths(bid)