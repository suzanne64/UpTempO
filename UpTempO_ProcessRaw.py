#!/usr/bin/python
import os
import sys
import time
import datetime as dt
import BuoyTools_py3_toot as BT
import UpTempO_BuoyMaster as BM
import UpTempO_HeaderCodes as HC
import UpTempO_Python as upy
import numpy as np
import pandas as pd
import scipy.io as sio
from itertools import chain
from microSWIFTtelemetry import pull_telemetry_as_var
import matlab.engine
# import matlabengineforpython

def processDATA(bid,df,hinf,fts=1,pmod='PG',L2p=False):

    binf=BM.BuoyMaster(bid)
    print(binf)
    if bid == '300534062158480' or bid == '300534062158460':
        binf['tdepths'] = [binf['tdepths'][-1]]  # all the data in Temperature0cm col are null, col has been removed

    #find variables to look for
    fvars=['Date','Lat','Lon']
    print(bid,binf)
    print()

    pcols = [col for col in hinf.keys() if col.startswith('P') or col.startswith('CTD-P')]
    pcolsD = {}
    if 'CTDpdepths' in binf:
        CTDpdepths = binf['CTDpdepths']
    if 'pdepths' in binf:
        pdepths = binf['pdepths']
    for pcol in pcols:
        if pcol.startswith('CTD-P'):
            pcolsD[pcol] = CTDpdepths.pop(0)
        if pcol.startswith('P'):
            pcolsD[pcol] = pdepths.pop(0)
    pcolsd = dict(sorted(pcolsD.items(), key=lambda item:item[1]))
    fvars.extend(pcolsD.keys())
    print('fvars after pcols',fvars)
    # # depths
    # if 'ddepths' in binf:
    #     tdeps=binf['tdepths']
    #     ddep=binf['ddepths']
    #
    #     nd=len(binf['ddepths'])
    #     for i in range(nd):
    #         cindex=tdeps.index(ddep[i])
    #         si="%d" % (cindex)
    #         fvars.append('D'+si)
    # if 'ED1_ind' in binf:
    #     nd=len(binf['tdepths'])
    #     for i in range(nd):
    #         si="%d" % (i+1)
    #         fvars.append('D'+si)

    # temperatures
    # tcols can be Ts T1 T10 T11 T12 T2, must sort before zipping with depths in a dict
    tcols = [col for col in hinf.keys() if col.startswith('T') and col != 'Thull'] #or col.startswith('CTD-T')]
    tcolsorted=[]
    if 'Ts' in tcols:
        tcolsorted = [tcols.pop(0)]
    tcolsorted.extend(sorted(tcols, key=lambda x:int(x.partition('T')[2])))
    if 'Thull' in hinf.keys():
        tcolsorted.append('Thull')
    tcolsorted.extend([col for col in hinf.keys() if col.startswith('CTD-T')])

    tcolsD = {}
    if 'tdepths' in binf:
        tdepths = binf['tdepths']
    if 'CTDtdepths' in binf:
        CTDtdepths = binf['CTDtdepths']
    if 'HULLtdepths' in binf:
        HULLtdepths = binf['HULLtdepths']

    for tcol in tcolsorted:
        tcol
        if tcol.startswith('CTD-T'):
            tcolsD[tcol] = CTDtdepths.pop(0)
        if tcol.startswith('T') and not tcol.startswith('Thull'):
            tcolsD[tcol] = tdepths.pop(0)
        if tcol.startswith('Thull'):
            tcolsD[tcol] = HULLtdepths.pop(0)
    tcolsD = dict(sorted(tcolsD.items(), key=lambda item:item[1]))
    fvars.extend(tcolsD.keys())
    print('fvars after tcols',fvars)

    # salinities
    scols = [col for col in hinf.keys() if (col.startswith('S') or col.startswith('CTD-S')) and 'SUB' not in col]
    scolsD = {}
    if 'sdepths' in binf:
        sdepths = binf['sdepths']
    if 'CTDsdepths' in binf:
        CTDsdepths = binf['CTDsdepths']
    if 'HULLsdepths' in binf:
        HULLsdepths = binf['HULLsdepths']

    for scol in scols:
        if scol.startswith('CTD-S'):
            scolsD[scol] = CTDsdepths.pop(0)
        if scol.startswith('S') and not scol.startswith('Shull'):
            scolsD[scol] = sdepths.pop(0)
        if scol.startswith('Shull'):
            scolsD[scol] = HULLsdepths.pop(0)
    scolsD = dict(sorted(scolsD.items(), key=lambda item:item[1]))
    fvars.extend(scolsD.keys())
    print('fvars after scols',fvars)
    
    # microSWIFT drifters include speed and direction
    if 'spddepths' in binf:
        spdcols = [col for col in hinf.keys() if col.startswith('spd')]
        fvars.extend(spdcols)
    if 'dirdepths' in binf:
        dircols = [col for col in hinf.keys() if col.startswith('dir')]
        fvars.extend(dircols)
    print('fvars after microSWIFTS',fvars)

    # and the rest
    if 'bp_ind' in binf: fvars.append('BP')
    if 'ta_ind' in binf: fvars.append('Ta')
    if 'vbatt_ind' in binf: fvars.append('BATT')
    if 'sub_ind' in binf: fvars.append('SUB')
    if 'gps_ind' in binf: fvars.append('GPSquality')

    df = df.filter(fvars,axis=1)
    # sort by Date in Ascending orderbuoys
    df.sort_values(by='Date',inplace=True)
    # break up 'Date' into year, month, day, decimal hour
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Hour'] = df['Date'].dt.hour + df['Date'].dt.minute/60
    fvars.insert(0,'Year')
    fvars.insert(1,'Month')
    fvars.insert(2,'Day')
    fvars.insert(3,'Hour')
    df = df[fvars]
    df.drop(columns='Date',inplace=True)
    # print(df.head())
    # print()
    # print(df.tail())
    # exit()
    # for buoys that give pressure in decibars.
    if bid in ['300234068519450','300534062895730','300534060251600','300534060051570','300534062897690']:
        #        2019-02           2022-12           2021-02           2021-03           2023-13
        pcols = [col for col in df.columns if col.startswith('P') or col.startswith('CTD-P')]
        for pcol in pcols:
            df[pcol] = df[pcol]/10

    # ###########  df.loc[df['SUB']>1] = np.nan ???

    # we process SASSIE earlier than before declaring the buoys dead
    if L2p:
        df.to_csv('UPTEMPO/L2p_SASSIE/'+bid+'.csv',index=False)
    else:
        df.to_csv('UPTEMPO/Processed_Data/'+bid+'.csv',index=False)

    #year,month,day,hour,lat,lon, OCEAN PRESSURES, ESTIMATED DEPTHS, TEMP DEPTHS, temps, Hull Temps, CTD-Temps, salis, Hull Salis, CTD-Salis, bp, ta, batt, sub
    # sto=[]
    # rown=0
    # for d in data:  #(dict(zip(sascol,sascolumns.keys()))),inplace=True)
    #     if ',' in d: sd=d.split(',')
    #     else: sd=d.split(';')
    #
    #     try:
    #         cdate=sd[hinf['Date']]
    #     except:
    #         print('failed sd[hinf[Date]]')
    #         print('d: '+d)
    #         print(rown)
    #         return 0
    #     rown+=1
    #     if '/' in cdate: spl='/'
    #     else: spl='-'
    #     #cyear,cmonth,cday,chour,cmin,csec,cdoy,q=BT.processDate(cdate,spliton=spl)
    #     thedate,thetime=cdate.split(' ')
    #     cyear,cmonth,cday=thedate.split(spl)
    #     chour,cmin,csec=thetime.split(':')
    #
    #     fchr=float(chour)+float(cmin)/60.
    #     chour="%.4f" % fchr
    #
    #     clat=sd[hinf['Lat']]
    #     clon=sd[hinf['Lon']]
    #
    #     if 'Ts' in hinf: its=hinf['Ts']
    #     else: its = -1
    #
    #     outline=[cyear,cmonth,cday,chour,clat,clon]
    #     for f in fvars[3:]:
    #         # print(f)
    #         if sd[hinf[f]]:
    #             if f.startswith('P') or f.startswith('CTD-P'): # in f) and (f != 'BP'):
    #                 fp=float(sd[hinf[f]])
    #                 if pmod == 'PG':
    #                     if bid != '300534060649670' and bid != '300534062898720':
    #                         fp=fp*.1  # 300534060649670 already comes in dB
    #                 if pmod == 'MY':
    #                     cbp=float(sd[hinf['BP']])
    #                     fp=MY_OP_Correction(fp,cbp)
    #                 pout="%.3f" % fp
    #                 outline.append(pout)
    #             elif f.startswith('D'):
    #                 fp=float(sd[hinf[f]])
    #                 pout="%.3f" % fp
    #                 outline.append(pout)
    #             else: outline.append(sd[hinf[f]])
    #         else: outline.append('-999')
    #     jout=' '.join(outline)
    #     sto.append(jout)

    # outhead='Year Month Day Hour Lat Lon '
    # jvars=' '.join(fvars[3:])
    # outhead+=jvars
    #
    # opw=open('UPTEMPO/Processed_Data/'+bid+'.dat','w')
    # opw.write(outhead+'\n')
    # # write to file in ascending time.
    # for s in reversed(sto):
    #     opw.write(s+'\n')
    # opw.close()
    #

def processARGOS(bid):   # needs to be redone working with pd.read_csv()    for processData

    rawpath='UPTEMPO/ARGOS_LastDownload_'+bid+'.dat'
    opf=open(rawpath,'r')
    data=opf.read()
    opf.close()
    data=data.split('return&gt;')[1]
    data=data.split('\n')
    head=data[0]
    data=data[1:]
    data=[da for da in data if da]
    data=[da for da in data if ('&' not in da) and ('</pre>' not in da)]


    header=head.split(';')
    hinf=HC.ARGOS_HeaderCodes(header)

    processDATA(bid,header,data,hinf,fts=0,pmod='MY') #fts=0 means don't look for Ts. Ts=T1 for this data
                                                     #pmod is the code for how to correct Ocean Pressure data. For PG data, it's a simple multiplication by .1.
                                                     #   For Marlin-Yug buoys, SLP has to be subtracted. The ARGOS buoy is a MY
    appendProcessed(bid,order=1)
    #WebFormat(bid,fts=0)


def processPG(bid,L2p=False):

    if L2p:
        binf = BM.BuoyMaster(bid)
        rawpath = f'UPTEMPO/L2p_SASSIE/UpTempO_{bid}_09-01-2022-06-01-2023.csv'
    else:
        rawpath='UPTEMPO/PG_LastDownload_'+bid+'.csv'
    df = pd.read_csv(rawpath,parse_dates=['DeviceDateTime'])
    # drop columns that are never used
    dropcols = ['DataId','DeviceName']
    for item in ['SecondsToFix','TransmissionRetry','CtSensorError','SamplingRate','TimeToFirst3DFix']:
        print(item)
        if item in df.columns:
            dropcols.append(item)
    dropcols.extend([col for col in df.columns if col.startswith('TiltPod')])
    dropcols.extend([col for col in df.columns if col.startswith('PodMag')])
    dropcols.extend([col for col in df.columns if 'Conductivity' in col])
    df.drop(columns=list(dropcols),inplace=True)
    
    # drop a column if all values are NaN
    df.dropna(axis=1,how='all',inplace=True)
    print(df.columns)

    # opr=open(rawpath,'r')
    # data=opr.read()
    # opr.close()
    # data=data.replace('"','')
    # data=data.split('\n')[0:-1]
    # header=data[0].split(',')

    # if DepthPods in header and NO PressurePods, change names to PressurePods,
    #  because the measurements are indeed pressure. 2/4/2021 sd
    #  BUT they are already dB, don't need to /10, in processDATA above
    # depthstring = any('DepthPod' in item for item in header)
    # pressstring = any('PressurePod' in item for item in header)
    depthstring = [item for item in df.columns if 'DepthPod' in item]
    pressstring = [item for item in df.columns if 'PressurePod' in item]
    # if pressstring or depthstring:
    #     print('HELP!')
    #     exit(-1)
    if depthstring and not pressstring:
        for ditem in depthstring:
            pitem = f'PressurePod{ditem[-1]}'
            df.rename(columns={ditem:pitem},inplace=True)
        # header = [h.replace('Depth','Pressure') for h in header]
        # # re-number PressurePods 1 through end
        # n=1
        # for ii,h in enumerate(header):
        #     if h.startswith('PressurePod'):
        #       header[ii]=f'{h[:-1]}{n}'
        #       n += 1
    print(df.columns)
    print('line 271')
    # data=data[1:]  # all but header line
    # data=[da for da in data if da]  # what does this do?
    #
    # if column is all null, remove

    # dataspl=[]
    # iiempty = None
    # for da in data:
    #     dataspl.append(da.split(','))
    # for ii in range(len(header)):
    #     colii = [da[ii] for da in dataspl]
    #     if all(not item for item in colii):
    #         iiempty = ii
    # if iiempty:
    #     del header[iiempty]
    #     # put back in same format for processDATA
    #     data=[]
    #     for ii,da in enumerate(dataspl):
    #         del da[iiempty]
    #         data.append(','.join(da))

    hinf=HC.PG_HeaderCodes([col for col in df.columns])
    # hinf=HC.PG_HeaderCodes(header)
    df.rename(columns=(dict(zip([col for col in df.columns],hinf.keys()))),inplace=True)
    print('after rename',df.columns)
    print()
    binf=BM.BuoyMaster(bid)
    print()
    print(binf)
    
    processDATA(bid,df,hinf,L2p=L2p)  #fts=1 by default (Ts column is different from T1)
                                       #fts=0 Ts coloum is same as T1
                                       #pmod=0.1 by default (value to multiply Ocean Pressure by)
    # # # LastUpdate bid.dat file now contains all the data (not just data since last update)
    # processDATA(bid,header,data,hinf)  #fts=1 by default (Ts column is different from T1)
    #                                    #fts=0 Ts coloum is same as T1
    #                                    #pmod=0.1 by default (value to multiply Ocean Pressure by)
    # # LastUpdate bid.dat file now contains all the data (not just data since last update)
    # opr=open('UPTEMPO/LastUpdate/'+bid+'.dat','r')
    # data=opr.read()
    # opr.close()
    # data=data.replace(';',' ')
    # data=data.split('\n')
    # data=[da for da in data if da]
    #
    # have=[data[0]]            # header
    # order = -1
    # if order == -1:
    #     nd=len(data)
    #     for i in range(nd):
    #         if data[nd-1-i] not in have: have.append(data[nd-1-i])
    # else:
    #     for d in data:
    #         if d not in have: have.append(d)
    #
    # opw=open('UPTEMPO/Processed_Data/'+bid+'.dat','w')
    # for h in have: opw.write(h+'\n')
    # opw.close()

    # appendProcessed(bid,order=-1)

    WebFormat(bid)

def processMicroSWIFT(ID,bid):
    
    # eng = matlab.engine.start_matlab()
    # eng.addpath('/Users/suzanne/git_repos/SWIFT-codes/GeneralTools')
    
    # startswift = dt.datetime(2024,5,16) 
    # starttime = f'{startswift.year}-{startswift.month:02d}-{startswift.day:02d}T00:00:00'
    # endtime = ''    # leaving endtime blank, says get data up to present.
    start = dt.datetime(2024,5,16)
    end = dt.date.today()+dt.timedelta(days=1)
    print('swift dates',start,end,ID)

    SWIFT_dict, errors_dict = pull_telemetry_as_var(buoy_id=ID,
                                                start_date=start,
                                                end_date=end,
                                                var_type='dict')
    print(SWIFT_dict.keys()) # e.g. SWIFT_dict['datetime']
    print(SWIFT_dict['datetime'][0])
    print(SWIFT_dict['datetime'][-1])
    print()
    dfSwift = pd.DataFrame(columns=['datetime','longitude','latitude','temperature','salinity'])
    dfSwift['datetime'] = SWIFT_dict['datetime']
    dfSwift['longitude'] = np.array(SWIFT_dict['longitude'])
    dfSwift['latitude'] = np.array(SWIFT_dict['latitude'])
    dfSwift['temperature'] = np.array(SWIFT_dict['temperature'])
    dfSwift['salinity'] = np.array(SWIFT_dict['salinity'])
    dfSwift['voltage'] = np.array(SWIFT_dict['voltage'])

    # for processing with .m code (2023 data retrieval)
    # swiftPath = 'swift_telemetry'
    # os.chdir(swiftPath)
    # print(ID,starttime,endtime)
    # allbatterylevels, lasttime, lastlat, lastlon = eng.pullSWIFTtelemetry(ID,starttime,endtime,swiftPath)
    # what = eng.pullSWIFTtelemetry(ID,starttime,endtime) #,swiftPath)
    # print('after what')
    # os.chdir('../')
    
    # swiftFile=f'microSWIFT{ID}_telemetry.mat'
    
    # swift_struct = sio.loadmat(f'{swiftPath}/{swiftFile}')
    # SWIFT = swift_struct['SWIFT']
    

    # # time, lat, lon are all the same length.   
    # # CTdepth, salinity, watertemp, driftspd, driftdirT can be multiple depths at same time, position
    # time = np.array([jtem for jtem in chain(*[item.tolist() for item in chain(*SWIFT[0,:]['time'])])])
    # print(time[:4],len(time),ID)
    # print('line 384 processMicroSWIFT')
    # print(np.argwhere(np.isnan(time)))
    # #  I AM NOT SURE WHY WE HAVE TO SUBTRACT 366 DAYS...
    # dates = [dt.datetime.combine(dt.datetime.fromordinal(int(t))-dt.timedelta(days=366),dt.datetime.min.time()) + dt.timedelta(days=t-int(t)) for t in time]  # + dt.timedelta(days=1) - dt.timedelta(days=366) 
    # lat = np.array([jtem for jtem in chain(*[item.tolist() for item in chain(*SWIFT[0,:]['lat'])])])
    # lon = np.array([jtem for jtem in chain(*[item.tolist() for item in chain(*SWIFT[0,:]['lon'])])])
    # battery = np.array([jtem for jtem in chain(*[item.tolist() for item in chain(*SWIFT[0,:]['battery'])])])
    # as of June, 2024, using python package microSWIFTtelemetry
    # dates = 
    # make a dictionary relating times to geophysical vars
    # timedepth = {}
    # for ii in range(lat.shape[0]):
    #     timedepth[ii] = {'time':SWIFT[0,:]['time'][ii].ravel(),
    #                      'CTdepth':SWIFT[0,:]['CTdepth'][ii].ravel(),
    #                      'WaterTemp':SWIFT[0,:]['watertemp'][ii].ravel(),
    #                      'Salinity':SWIFT[0,:]['salinity'][ii].ravel(),
    #                      'DriftSpd':SWIFT[0,:]['driftspd'][ii].ravel(),
    #                      'DriftDirT':SWIFT[0,:]['driftdirT'][ii].ravel()
    #                      }

    # find all unique depths
    # CTdepth = np.array([jtem for jtem in chain(*[item.tolist() for item in chain(*SWIFT[0,:]['CTdepth'])])])
    # unique, counts = np.unique(CTdepth, return_counts=True)
    # ndepths = len(unique)
    # print('line 780',unique,ndepths)
    # # get column names for dataframe
    # columns = ['Date','Lat','Lon']
    # [columns.append(f'CTdepth-{ii}') for ii in range(ndepths)]
    # [columns.append(f'WaterTemp-{ii}') for ii in range(ndepths)]
    # [columns.append(f'Salinity-{ii}') for ii in range(ndepths)]
    # columns.append('BATT')
    # [columns.append(f'DriftSpd-{ii}') for ii in range(ndepths)]
    # [columns.append(f'DriftDirT-{ii}') for ii in range(ndepths)]
    # # create dataFrame
    # dfSwift = pd.DataFrame(columns=columns)
    # print(dfSwift.columns)

    # dfSwift['Date'] = dates 
    # dfSwift['Lat'] = lat
    # dfSwift['Lon'] = lon
    # dfSwift['BATT'] = battery

    # for ii in range(ndepths):  # establish columns
    #     dfSwift[f'CTdepth-{ii}'] = np.nan
    #     dfSwift[f'WaterTemp-{ii}'] = np.nan
    #     dfSwift[f'Salinity-{ii}'] = np.nan
    #     dfSwift[f'DriftSpd-{ii}'] = np.nan
    #     dfSwift[f'DriftDirT-{ii}'] = np.nan

    # for k,v in timedepth.items():

    #     for ii in range(ndepths):
    #         if ii==0:
    #             # print(dfSwift[k,f'CTdepth-{ii}'])
    #             dfSwift.at[k,f'CTdepth-{ii}'] = v['CTdepth'][ii]
    #             # print(dfSwift[f'CTdepth-{ii}',0])
    #             dfSwift.at[k,f'WaterTemp-{ii}'] = v['WaterTemp'][ii]
    #             dfSwift.at[k,f'Salinity-{ii}'] = v['Salinity'][ii]
    #             dfSwift.at[k,f'DriftSpd-{ii}'] = v['DriftSpd'][ii]
    #             dfSwift.at[k,f'DriftDirT-{ii}'] = v['DriftDirT'][ii]
    #         else:
    #             try:
    #                 dfSwift.at[k,f'CTdepth-{ii}'] = v['CTdepth'][ii]
    #             except:
    #                 pass
    #             try:
    #                 dfSwift.at[k,f'WaterTemp-{ii}'] = v['WaterTemp'][ii]
    #             except:
    #                 pass
    #             try:
    #                 dfSwift.at[k,f'Salinity-{ii}'] = v['Salinity'][ii]
    #             except:
    #                 pass
    #             try:
    #                 dfSwift.at[k,f'DriftSpd-{ii}'] = v['DriftSpd'][ii]
    #             except:
    #                 pass
    #             try:
    #                 dfSwift.at[k,f'DriftDirT-{ii}'] = v['DriftDirT'][ii]
    #             except:
    #                 pass
    # print(dfSwift.head())

    # remove depth columns, they are only for header.
    # dfSwift.drop(columns=[item for item in dfSwift.columns if item.startswith('CTdepth-')],inplace=True)
    # hinf=HC.PG_HeaderCodes([col for col in dfSwift.columns[3:]])
    # mapper = {k:v for (k,v) in zip(dfSwift.columns[3:],hinf)}
    print('line 494')
    print(dfSwift.columns)
    hinf=HC.PG_HeaderCodes([col for col in dfSwift.columns])
    mapper = {k:v for (k,v) in zip(dfSwift.columns,hinf)}
    dfSwift.rename(columns=mapper,inplace=True)
    print('dfSWIFT columns',dfSwift.columns)
    # exit()
    print(hinf)
    print()
    processDATA(bid,dfSwift,hinf)  
    
    # WebFormat(f'microSWIFT-{bid}')


def appendProcessed(bid,order=-1,fts=1):
    #fts = look for Ts data (1) or not (0)
    #order = new data is in chronological order(1) or new data is in reverse order(-1)
    #ARGOS: fts=0, order=1
    #PG: fts=1, order=-1

    opr=open('UPTEMPO/LastUpdate/'+bid+'.dat','r')
    data=opr.read()
    opr.close()
    data=data.replace(';',' ')
    data=data.split('\n')
    data=[da for da in data if da]

    if os.path.isfile('UPTEMPO/Processed_Data/'+bid+'.dat'):
        oph=open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
        have=oph.read()
        oph.close()
        have=have.split('\n')
        have=[h for h in have if h]
    else: have=[data[0]]

    if order == -1:
        nd=len(data)
        for i in range(nd):
            if data[nd-1-i] not in have: have.append(data[nd-1-i])
    else:
        for d in data:
            if d not in have: have.append(d)

    # remove data measured before deploymentDate (see BM.BuoyMaster)
    binf = BM.BuoyMaster(bid)
    deploymentDate = binf['deploymentDate']
    depmonth, depday, depyear = deploymentDate.split('/')
    depdate = dt.datetime(int(depyear), int(depmonth), int(depday))
    for h in have[1:]:
        hyear, hmonth, hday = h.split(' ')[:3]
        if dt.datetime(int(hyear), int(hmonth), int(hday)) < depdate:
            have.remove(h)

    opw=open('UPTEMPO/Processed_Data/'+bid+'.dat','w')
    for h in have: opw.write(h+'\n')
    opw.close()


#======================================================================
def WebFormat(bid,fts=1,order=-1,newdead=0,L2p=False):

    # get info and make proper header
    # wmo=BT.lookupWMO(bid)
    binf=BM.BuoyMaster(bid)  # contains specific buoy info in 'buoy cards'
    binfn1="%.2d" % int(binf['name'][1])
    wmo = binf['wmo']

    sensor = {'PG':'Pacific Gyre',
              'SBE':'SeaBird Electronics',
              'S9':'Soundnine',
              'UW':'Univeristy of Washington'}

    # depDate="%.2d/%.2d/%d" % (int(depline[1]),int(depline[2]),int(depline[0]))
    fdeplat=binf['deploymentLat']
    fdeplon=binf['deploymentLon']
    print('line 544',fdeplat,fdeplon)

    if fdeplat < 0:
        fdeplat=-fdeplat
        nors='S'
    else: nors='N'

    if fdeplon < 0:
        fdeplon=-fdeplon
        eorw='W'
    else: eorw='E'
    deplat="%.2f" % fdeplat
    deplon="%.2f" % fdeplon
    depll=deplat+nors+' '+deplon+eorw

    # opf=open('UPTEMPO/LastUpdate/'+bid+'.dat','r')
    # data=opf.read()
    # opf.close()
    # data=data.replace(';',' ')
    # data=data.split('\n')
    # data=[da for da in data if da]
    # header=data[0]
    # data=data[1:]
    # nd=len(data)

    # opf = open('UPTEMPO/Processed_Data/'+bid+'.dat','r')
    # data=opf.read()
    # opf.close()
    # data=data.replace(';',' ')
    # data=data.split('\n')
    # data=[da for da in data if da]
    # header=data[0]
    # data=data[1:]
    # nd=len(data)
    if L2p:
        df = pd.read_csv('UPTEMPO/L2p_SASSIE/'+bid+'.csv')
    else:
        df = pd.read_csv('UPTEMPO/Processed_Data/'+bid+'.csv')

    # shead=header.split(' ')

    fname='UpTempO_'+binf['name'][0]+'_'+binfn1+'_'+binf['vessel'].split(' ')[0]+'-Last.dat'

    lastUpdate = dt.datetime.now().strftime('%m/%d/%Y')
    dolt = f"{df['Month'].iloc[-1]}/{df['Day'].iloc[-1]}/{df['Year'].iloc[-1]}"
    # today=datetime.datetime.now()
    # lastUpdate="%.2d/%.2d/%d" % (today.month,today.day,today.year)
    # lastline=data[-1].split(' ')
    # dolt="%.2d/%.2d/%d" % (int(lastline[1]),int(lastline[2]),int(lastline[0]))

    # if nd>0:
    #     if order == -1:
    #         rdata=[]
    #         for r in range(nd):
    #             rdata.append(data[nd-1-r])
    #         data=rdata

    #         lastline=data[-1].split(' ')
    #         dolt="%.2d/%.2d/%d" % (int(lastline[1]),int(lastline[2]),int(lastline[0]))
    # else:
    #     dolt=lastUpdate

    webhead=['%UpTempO '+binf['name'][0]+' #'+binfn1,
          '%Iridium ID: '+bid,
          '%WMO: '+wmo,
          '%DATE DEPLOYED: '+ binf['deploymentDate'],
          '%POSITION DEPLOYED: '+depll,
          '%DATE OF LAST TRANSMISSION: '+dolt,
          '%DATE OF LAST DATA FILE UPDATE: '+lastUpdate,
          '%',
          '%DATA COLUMNS:',
          '% 0 = year',
          '% 1 = month',
          '% 2 = day',
          '% 3 = hour (GMT)',
          '% 4 = Latitude (N)',
          '% 5 = Longitude (E)']

    # remake  columns
    if bid == '300534062158460' or bid == '300534062158480':
        binf['tdepths'] = [binf['tdepths'][-1]]   # all the data in Temperature0cm col are null, col has been removed

    # tdepths=binf['tdepths'];
    # eddepths=binf['tdepths'].copy()
    tcols = binf['tdepths']
    tcolsMadeBy = []
    if 'tdepthsMadeBy' in binf: tcolsMadeBy = binf['tdepthsMadeBy']
    if 'HULLtdepths' in binf:
        tcols.extend(binf['HULLtdepths'])
        if 'HULLtdepthsMadeBy' in binf: tcolsMadeBy.extend(binf['HULLtdepthsMadeBy'])
    if 'CTDtdepths' in binf:
        tcols.extend(binf['CTDtdepths'])
        if 'CTDtdepthsMadeBy' in binf: tcolsMadeBy.extend(binf['CTDtdepthsMadeBy'])
    if len(tcolsMadeBy) == 0:
        tcols = sorted(tcols)
    else:
        tcols, tcolsMadeBy = zip(*sorted(zip(tcols,tcolsMadeBy)))
        tcols = list(tcols)
        tcolsMadeBy = list(tcolsMadeBy)
    # print('tcols',tcols)
    # print('tcolsMadeBy',tcolsMadeBy)

    pcols = []
    if 'pdepthsMadeBy' or 'CTDpdepthsMadeBy' in binf: pcolsMadeBy = []
    if 'pdepths' in binf:
        pcols.extend(binf['pdepths'])
        if 'pdepthsMadeBy' in binf: pcolsMadeBy.extend(binf['pdepthsMadeBy'])
    if 'CTDpdepths' in binf:
        pcols.extend(binf['CTDpdepths'])
        if 'CTDpdepthsMadeBy' in binf: pcolsMadeBy.extend(binf['CTDpdepthsMadeBy'])
    if len(pcolsMadeBy) == 0:
        pcols = sorted(pcols)
    else:
        pcols, pcolsMadeBy = zip(*sorted(zip(pcols,pcolsMadeBy)))
        pcols = list(pcols)
        pcolsMadeBy = list(pcolsMadeBy)

    if 'ddepths' in binf: ddepths=binf['ddepths'];

    scols = []
    if 'sdepthsMadeBy' or 'HULLsdepthsMadeBy' or 'CTDsdepthsMadeBy' in binf: scolsMadeBy = []
    if 'sdepths' in binf:
        scols.extend(binf['sdepths'])
        if 'sdepthsMadeBy' in binf: scolsMadeBy.extend(binf['sdepthsMadeBy'])
    if 'HULLsdepths' in binf:
        scols.extend(binf['HULLsdepths'])
        if 'HULLsdepthsMadeBy' in binf: scolsMadeBy.extend(binf['HULLsdepthsMadeBy'])
    if 'CTDsdepths' in binf:
        scols.extend(binf['CTDsdepths'])
        if 'CTDsdepthsMadeBy' in binf: scolsMadeBy.extend(binf['CTDsdepthsMadeBy'])
    if len(scolsMadeBy) == 0:
        scols = sorted(scols)
    else:
        scols, scolsMadeBy = zip(*sorted(zip(scols,scolsMadeBy)))
        scols = list(scols)
        scolsMadeBy = list(scolsMadeBy)
        
    # shead=header.split(' ')[6:]  # only work on the data columns
    # print(shead)
    # print()
    print(df.columns)
    col=6

    for h in df.columns: #shead:
        print(h,col)
        if h.startswith('P') or h.startswith('CTD-P'):
            cdep=pcols.pop(0)
            strdep,strcol=strDepColi(cdep,col)
            if pcolsMadeBy:
                cdepMadeBy = pcolsMadeBy.pop(0)
                lineout=f'% {strcol} = Ocean Pressure (dB) at Sensor #{h[-1]} (Nominal Depth = {strdep} m), sensor made by {sensor[cdepMadeBy]}'
            else:
                lineout=f'% {strcol} = Ocean Pressure (dB) at Sensor #{h[-1]} (Nominal Depth = {strdep} m)'
            webhead.append(lineout)
            col+=1
        # if h.startswith('CTD-P'):
        #     cdep=CTDpdepths.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout='% '+strcol+' = Ocean Pressure (dB) at Sensor #'+h[-1]+'(Nominal Depth = '+strdep+' m)'
        #     webhead.append(lineout)
        #     col+=1

        if (h.startswith('T') or h.startswith('CTD-T')) and h != 'Ta':
            cdep=tcols.pop(0)
            strdep,strcol=strDepColi(cdep,col)
            if tcolsMadeBy:
                cdepMadeBy = tcolsMadeBy.pop(0)
                lineout=f'% {strcol} = Temperature (C) at nominal depth {strdep} (m), sensor made by {sensor[cdepMadeBy]}'
            else:
                lineout=f'% {strcol} = Temperature (C) at nominal depth {strdep} (m)'

            print(lineout)
            webhead.append(lineout)
            col+=1
    ####        , sensor made by
        # if h == 'Thull':
        #     cdep=HULLtdepths.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout='% '+strcol+' = Temperature at nominal depth '+strdep+' (m)'
        #     webhead.append(lineout)
        #     col+=1
        # if h.startswith('CTD-T'):
        #     cdep=CTDtdepths.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout='% '+strcol+' = Temperature at nominal depth '+strdep+' (m)'
        #     webhead.append(lineout)
        #     col+=1

        if (h.startswith('S') or h.startswith('CTD-S')) and h != 'SUB':
            cdep=scols.pop(0)
            strdep,strcol=strDepColi(cdep,col)
            if scolsMadeBy:
                cdepMadeBy = scolsMadeBy.pop(0)
                lineout=f'% {strcol} = Salinity (psu) at nominal depth {strdep} (m), sensor made by {sensor[cdepMadeBy]}'
            else:
                lineout=f'% {strcol} = Salinity (psu) at nominal depth {strdep} (m)'

            print(lineout)
            webhead.append(lineout)
            col+=1
            
        # if h.startswith('spd'):
        #     spdcols=binf['spddepths']
        #     cdep=spdcols.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout=f'% {strcol} = Speed (m/s) at nominal depth {strdep} (m)'
        #     print(lineout)
        #     webhead.append(lineout)
        #     col+=1
        # if h.startswith('dir'):
        #     spdcols=binf['dirdepths']
        #     cdep=spdcols.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout=f'% {strcol} = Direction (from North) at nominal depth {strdep} (m)'
        #     print(lineout)
        #     webhead.append(lineout)
        #     col+=1
        # if h.startswith('CTD-S'):
        #     cdep=CTDsdepths.pop(0)
        #     strdep,strcol=strDepColi(cdep,col)
        #     lineout='% '+strcol+' = Salinity at nominal depth '+strdep+' (m)'
        #     webhead.append(lineout)
        #     col+=1

        if h == 'Ta':
            strcol="%d" % col
            lineout='% '+strcol+' = Air Temperature (C)'
            webhead.append(lineout)
            col+=1

        if h == 'BP':
            strcol="%d" % col
            lineout='% '+strcol+' = Sea Level Pressure (mBar)'
            webhead.append(lineout)
            col+=1

        if h == 'BATT':
            strcol="%d" % col
            lineout='% '+strcol+' = Battery Voltage (V)'
            webhead.append(lineout)
            col+=1

        if h == 'SUB':
            strcol="%d" % col
            lineout='% '+strcol+' = Submergence Percent'
            webhead.append(lineout)
            col+=1

        if h == 'GPSquality':
            strcol="%d" % col
            lineout='% '+strcol+' = GPS quality'
            webhead.append(lineout)
            col+=1


    #     if 'D' in h and not 'CTD' in h:
    #         try:
    #             cdep=eddepths.pop(0)
    #             strdep,strcol=strDepColi(cdep,col)
    #             lineout='% '+strcol+' = Estimated depth at nominal depth '+strdep+' (m)'
    #             col+=1
    #         except:
    #             pass


    webhead.append('%END')

    # for downloading files later (mar 2023) to get GPSQuality, need to cut off data 
    #    after we 'stopped listening'
    if bid in '300534060649670':  # 2021 01
        df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        df.drop( df[df['Dates']>dt.datetime(2022,3,1)].index, inplace=True)
        df.drop(columns=['Dates'],inplace=True)
    if bid in '300534060251600':  # 2021 02
        df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        df.drop( df[df['Dates']>dt.datetime(2021,12,24)].index, inplace=True)
        df.drop(columns=['Dates'],inplace=True)
    if bid in '300534060051570':  # 2021 03
        df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        df.drop( df[df['Dates']>dt.datetime(2021,11,1)].index, inplace=True)
        df.drop(columns=['Dates'],inplace=True)
    if bid in '300534062158480':  # 2021 04
        df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        df.drop( df[df['Dates']>dt.datetime(2021,10,24)].index, inplace=True)
        df.drop(columns=['Dates'],inplace=True)
    if bid in '300534062158460':  # 2021 05
        df['Dates']=pd.to_datetime(df[['Year','Month','Day','Hour']])
        df.drop( df[df['Dates']>dt.datetime(2021,11,24)].index, inplace=True)
        df.drop(columns=['Dates'],inplace=True)
        
    # opw=open('UPTEMPO/Processed_Data/'+bid+'.dat','w')
    # for h in have: opw.write(h+'\n')
    # opw.close()

    # if os.path.isfile('UPTEMPO/WebData/'+fname):
    #     opweb=open('UPTEMPO/WebData/'+fname,'r')
    #     have=opweb.read()
    #     opweb.close()
    #     have=have.split('\n')
    #     have=[ha for ha in have if ha]
    #     header=[ha for ha in webhead]
    #     hdata=[ha for ha in have if '%' not in ha]

    #     for d in data:
    #         if d not in hdata: hdata.append(d)

    #     opw=open('UPTEMPO/WebData/'+fname,'w')
    #     for h in header: opw.write(h+'\n')
    #     for hd in hdata: opw.write(hd+'\n')
    #     opw.close()
    # else:
    #     # depline=data[0].split(' ')

    if L2p:
        opw=open('UPTEMPO/L2p_SASSIE/'+fname,'w')
    else:
        opw=open('UPTEMPO/WebData/'+fname,'w')
        
    for w in webhead: opw.write(w+'\n')
    data = df.to_string(header=False, index=False)
    opw.write(data)
    opw.close()

    strtoday=dt.datetime.today().strftime('%Y%m%d')
    today = dt.datetime.today()
    
    if newdead: newfname=fname.replace('Last','FINAL')
    else: newfname=fname.replace('Last',strtoday)
    if L2p:
        newfname = fname.replace('Last','20230601')

    if L2p:
        os.system('cp UPTEMPO/L2p_SASSIE/'+fname+' UPTEMPO/L2p_SASSIE/'+newfname)
        return 'UPTEMPO/L2p_SASSIE/'+newfname, lastUpdate
    else:
        os.system('cp UPTEMPO/WebData/'+fname+' UPTEMPO/WebData/'+newfname)
        lastUpdate="%.2d/%.2d/%d" % (today.month,today.day,today.year)

        return 'UPTEMPO/WebData/'+newfname, lastUpdate




#===========================
def strDepColi(p,c):
    strdep="%.2f" % p
    strcol="%d" % c
    return strdep,strcol

#===========================
def MY_OP_Correction(pval,cbp):

    density=1027.0
    AP=cbp*100.0 #Pa
    cpval=( (pval*10000.0) - AP)/(density*9.8)

    return cpval
#===========================
def PG_Driver(bid):

    processPG(bid)
    datpath=WebFormat(bid)
    return datpath
