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

def upupData():
    
    opdat=open('UPTEMPO/DataFilesToTransfer.dat','w')

    reporting,dead,order,newdead=BM.getBuoys()  

    #---- Update Data ----
    for r in reporting:  # reporting is a dict, keys are buoy ID
        source,user=reporting[r][3].split(':')
        if source == 'PG':
            print('getting '+r+' from PG:'+user)
            upd.getPG(r,user)
            upp.processPG(r)
            datpath=upp.WebFormat(r)
        if source == 'ARGOS':
            print('getting '+r+' from ARGOS:'+user)
            upd.getARGOS(r)
            upp.processARGOS(r)
            datpath=upp.WebFormat(r,order=1,fts=0)
            
        fname=datpath.split('/')[-1]
        opdat.write(datpath+' WebDATA/'+fname+'\n')

    if newdead:
        for nd in newdead:
            source=newdead[nd][-1].split(':')[0]
            if source == 'ARGOS': datpath=upp.WebFormat(nd,order=1,fts=0,newdead=1)
            else: datpath=upp.WebFormat(nd,newdead=1)
            

    opdat.close()
    
    upy.StatsReport()
            
            
def upupPlots():
    nopresbids=['300534062158460','300534062158480']
    curbuoys,deadbuoys,orderbuoys,newdead=BM.getBuoys()
    for c in curbuoys:
        uplots.TimeSeriesPlots(bid=c)
        if c not in nopresbids:
            uplots.TimeSeriesPlots(bid=c,quan='Pressure')
        uplots.VelocitySeries(c)
##        uplots.TrackMaps(c)

##    uplots.OverviewMap()
        

def upupGo():

    upy.UploadToPSC()
        
if __name__=='__main__':
    upupData()
    #upupPlots()



