#!/usr/bin/python
import os
import sys
import time
import datetime
import BuoyTools_py3_toot as BT
import UpTempO_BuoyMaster as BM
import UpTempO_HeaderCodes as HC
import UpTempO_Python as upy
import UpTempO_Downloads as upd
import UpTempO_ProcessRaw as upp
import UpTempO_Plots as uplots
import ArcticPlots as aplots

def upupData():
    
    opdat=open('UPTEMPO/DataFilesToTransfer.dat','w')

    reporting,dead,order,newdead=BM.getBuoys() 

    #---- Update Data ----
    for r in reporting:  # reporting is a dict, keys are buoy ID
        # if '300534060251600' in r:

        source,user=reporting[r][3].split(':')
        if source == 'PG':
            print('getting '+r+' from PG:'+user)
            # upd.getPG(r,user)
            upd.getPG(r,user,reporting[r][2])
            upp.processPG(r)
            datpath, latestupdate = upp.WebFormat(r)
        if source == 'ARGOS':
            print('getting '+r+' from ARGOS:'+user)
            upd.getARGOS(r)
            upp.processARGOS(r)
            datpath, latestupdate = upp.WebFormat(r,order=1,fts=0)
            
        fname=datpath.split('/')[-1]
        opdat.write(datpath+' WebDATA/'+fname+'\n')
    
        if newdead:
            for nd in newdead:
                source=newdead[nd][-1].split(':')[0]
                if source == 'ARGOS': datpath=upp.WebFormat(nd,order=1,fts=0,newdead=1)
                else: datpath=upp.WebFormat(nd,newdead=1)
            

    opdat.close()
    
    upy.StatsReport(latestupdate)
            
            
def upupPlots():
    nopresbids=['300534062158460','300534062158480']
    nosalibids=['300534060051570','300534060251600','300234068519450']
    curbuoys,deadbuoys,orderbuoys,newdead=BM.getBuoys()
    for c in curbuoys:
        # if c =='300534062158480':
        uplots.TimeSeriesPlots(bid=c)  # Temperature plots are default
        if c not in nopresbids:
            uplots.TimeSeriesPlots(bid=c,quan='Pressure')
        if c not in nosalibids:
            uplots.TimeSeriesPlots(bid=c,quan='Salinity')
        uplots.VelocitySeries(c)
        uplots.Batt_Sub(c)
        uplots.TrackMaps(c)
    uplots.OverviewMap()
        

def upupGo():

    upy.UploadToPSC()
        
if __name__=='__main__':
    # upupData()
    upupPlots()
    # upupGo()


