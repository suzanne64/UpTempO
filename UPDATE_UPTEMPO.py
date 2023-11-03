#!/usr/bin/python
import os, glob, shutil
import sys
import time
import datetime as dt
import BuoyTools_py3_toot as BT
import UpTempO_BuoyMaster as BM
import UpTempO_HeaderCodes as HC
import UpTempO_Python as upy
import UpTempO_Downloads as upd
import UpTempO_ProcessRaw as upp
import UpTempO_Plots as uplots
import ArcticPlots as aplots
from waterIce import getL1
import UpTempO_PlotsLevel2 as uplotsL2

def upupData():

    opdat=open('UPTEMPO/DataFilesToTransfer.dat','w')

    reporting,dead,order,newdead=BM.getBuoys()
    for r in reporting:
        print(r)
    # exit()
    if len(newdead)>0:
        print(newdead)
        # exit(-1)
    
    # empty swift_telemetry dirs
    swiftContents = glob.glob('swift_telemetry/*')
    for item in swiftContents:
        if os.path.isfile(item):
            os.remove(item)
        if os.path.isdir(item):
            shutil.rmtree(item)

    #---- Update Data ----
    for r in reporting:  # reporting is a dict, keys are buoy ID'
        # r = '300534062897690'
        source,user=reporting[r][3].split(':')
        print(source,user,r)
        print(reporting[r][2])
        if source == 'PG':
            print('getting '+r+' from PG:'+user)
            upd.getPG(r,user,reporting[r][2])
            upp.processPG(r)
            datpath, latestupdate = upp.WebFormat(r)
            print('line 47',datpath,latestupdate)
        if source == 'ARGOS':
            print('getting '+r+' from ARGOS:'+user)
            upd.getARGOS(r)
            upp.processARGOS(r)
            datpath, latestupdate = upp.WebFormat(r,order=1,fts=0)
        if source =='UW':
            print('getting '+r+' from UW') 
            binf = BM.BuoyMaster(r)
            ID = binf['pgname'].split('-')[1]
            upp.processMicroSWIFT(ID,r)
            datpath, latestupdate = upp.WebFormat(r)
        
        fname=datpath.split('/')[-1]
        print('fname',fname)
        opdat.write(datpath+' WebDATA/'+fname+'\n')
        # exit()
    if newdead:
        for nd in newdead:
            source=newdead[nd][-1].split(':')[0]
            if source == 'ARGOS': datpath=upp.WebFormat(nd,order=1,fts=0,newdead=1)
            else: datpath=upp.WebFormat(nd,newdead=1)

    opdat.close()
    # exit()

    upy.StatsReport(latestupdate)

# 
def upupPlots():
    figspath = 'UPTEMPO/WebPlots'
    
    curbuoys,deadbuoys,orderbuoys,newdead=BM.getBuoys()
    
    today = dt.datetime.now()
    tomorrow = today + dt.timedelta(days=2)

    # use this dict for website plots
    timed = {'300534062898720': [dt.datetime(2022,9,8), dt.datetime(2022,10,25)],   # 2022 01  SASSIE
              '300534062897730': [dt.datetime(2022,9,8), tomorrow],                 # 2022 02  SASSIE
              '300534063704980': [dt.datetime(2022,9,8), dt.datetime(2022,10,27)],  # 2022 03  SASSIE
              '300534063807110': [dt.datetime(2022,9,10), tomorrow],                # 2022 04  SASSIE
              '300534063803100': [dt.datetime(2022,9,13), dt.datetime(2022,9,28)],  # 2022 05  SASSIE  long
              '300534062892700': [dt.datetime(2022,9,13), dt.datetime(2022,10,9)],  # 2022 06  SASSIE  no pressures
              '300534062894700': [dt.datetime(2022,9,15), tomorrow],                # 2022 07  SASSIE  no pressures
              '300534062894740': [dt.datetime(2022,9,18), tomorrow],                # 2022 08  SASSIE
              '300534062896730': [dt.datetime(2022,9,18), tomorrow],                # 2022 09  SASSIE  long
              '300534062894730': [dt.datetime(2022,9,18), dt.datetime(2022,11,2)],  # 2022 10  SASSIE
              '300534062893700': [dt.datetime(2022,9,18), dt.datetime(2022,10,9)],  # 2022 11  SASSIE
              '300534062895730': [dt.datetime(2022,10,10), tomorrow],               # 2022 12  SIZRS 3 press
              '300434064041440': [dt.datetime(2023,6,13), dt.datetime(2023,7,21)],  # 2023 01  NOAA
              '300434064042420': [dt.datetime(2023,6,13), dt.datetime(2023,7,6)],   # 2023 02  NOAA
              '300434064046720': [dt.datetime(2023,6,13), dt.datetime(2023,7,4)],   # 2023 03  NOAA
              '300434064042710': [dt.datetime(2023,6,13), dt.datetime(2023,7,21)],  # 2023 04  NOAA     
              '300534062891690': [dt.datetime(2023,7,28), tomorrow],                # 2023 05 Healy                  
              '300534062893740': [dt.datetime(2023,7,28), dt.datetime(2023,8,7)],   # 2023 06 Healy                  
              '300534062895700': [dt.datetime(2023,7,28), tomorrow],                # 2023 07 Healy                  
              '300534063449630': [dt.datetime(2023,9,14), tomorrow],                # 2023 08 Mirai  
              '300434064040440': [dt.datetime(2023,9,19), dt.datetime(2023,9,27)],  # 2023 09 NOAA
              '300434064048220': [dt.datetime(2023,9,19), tomorrow],                # 2023 10 NOAA
              '300434064044730': [dt.datetime(2023,9,19), tomorrow],                # 2023 11 NOAA
              '300434064045210': [dt.datetime(2023,9,19), tomorrow],                # 2023 12 NOAA
              '300534062897690': [dt.datetime(2023,10,19), tomorrow],               # 2023 13 SIZRS 3 pres, 60m (not yet deployed)        
            }

    for ii,c in enumerate(curbuoys):
        # if '300534062897690' in c:
        # if ii>5:
            binf = BM.BuoyMaster(c)
        # if binf['name'][0] == '2023':
            fileL1 = f"UPTEMPO/WebData/UpTempO_{binf['name'][0]}_{int(binf['name'][1]):02d}_{binf['vessel'].split(' ')[0]}-Last.dat"
            # getL1 asks if we want to check ranges. the answer here is NO.
            # if binf['vessel'].startswith('NOAA'):
            df1,pdepths,tdepths,sdepths,ddepths,tiltdepths,_ = getL1(fileL1,c)
            print(fileL1,df1.columns)
            print('tdepths',tdepths)
            print('pdepths',pdepths)
            print('sdepths',sdepths)
            # make Level 1b plots for website with somewhat QC'd data
            uplotsL2.TimeSeriesPlots(c,figspath,df=df1,tdepths=tdepths,
                                      dt1=timed[c][0],dt2=timed[c][1])
            
            if sdepths:
                uplotsL2.TimeSeriesPlots(c,figspath,df=df1,quan='Salinity',sdepths=sdepths,
                                          dt1=timed[c][0],dt2=timed[c][1])
            if pdepths:
                uplotsL2.TimeSeriesPlots(c,figspath,df=df1,quan='Pressure',pdepths=pdepths,
                                          dt1=timed[c][0],dt2=timed[c][1])
            if tiltdepths:
                uplotsL2.TimeSeriesPlots(c,figspath,df=df1,quan='Tilt',
                                          dt1=timed[c][0],dt2=timed[c][1])
            if any(item in df1.columns for item in ['SUB','BATT']):  # sheesh
                # if not binf['vessel'].startswith('NOAA'):
                    uplotsL2.Batt_Sub(c,figspath,df=df1,dt1=timed[c][0],dt2=timed[c][1])
            uplotsL2.VelocitySeries(c,figspath,df=df1,dt1=timed[c][0],dt2=timed[c][1])
            
            if '300534062897730' in c:  # 2022 02
                uplotsL2.TrackMaps2Atlantic(c,figspath,df=df1)
            else:
                uplotsL2.TrackMaps(c,figspath,df=df1)

        
        # plots for Level 1
        # Temperature plots are default
        # c = '300534063704980'  # for testing out one buoy
        # uplots.TimeSeriesPlots(bid=c)
    #     if c not in nopresbids:
    #         uplots.TimeSeriesPlots(bid=c,quan='Pressure')
    #     if c not in nosalibids:
    #         uplots.TimeSeriesPlots(bid=c,quan='Salinity')
    #     # uplots.VelocitySeries(c)
    #     # uplots.Batt_Sub(c)
    #     uplots.TrackMaps(c)
    #     # exit(-1)
    
    uplots.PrevOverviewMap()  # '20230910'
    
    
    # # uplots.PrevOverviewMapSouth(defaultPlot=True)

    # filename = UpTempO_2022_01_SASSIE-Last.dat
    # df1,pdepths,tdepths,sdepths,ddepths,tiltdepths = getL1(fileL1, c, figspath)
    # For doing one
    # strdate='20230220'
    # uplots.PrevOverviewMap(strdate)

    # strdate='20220620'
    # objdate = dt.datetime.strptime(strdate,'%Y%m%d')

    # For doing many
    # strenddate = '20220220'
    # objenddate = dt.datetime.strptime(strenddate,'%Y%m%d')
    # while objdate <= objenddate:
    #     uplots.PrevOverviewMap(strdate)
    #     objdate = objdate + dt.timedelta(days=7)
    #     strdate = "%d%.2d%.2d" % (objdate.year,objdate.month,objdate.day)
    # uplots.PrevOverviewMap('20220220')

def upupGo():

    upy.UploadToPSC()

if __name__=='__main__':
    # GIT PULL SWIFT CODES:   cd ~/git_repos/SWIFT-codes; git stash; git pull; see notes_swift.docx
    # upupData()
    # upupPlots()
    upupGo()
