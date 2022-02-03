#!/usr/bin/python
import os
import sys
import time
import datetime
import BuoyTools_py3_toot as BT
import PlottingFuncs as PF
import numpy as np
import FUNC_PG_HeaderCodes as HC
import UpTempO_Python as upy
import requests
import urllib
import UpTempO_BuoyMaster as BM


def userCred(user):

    psswd={'WB_Ermold':'warmbuoy','pscapluw':'microstar'}
    return psswd[user]

# def getPG(bid,user,daysago=50):
def getPG(bid,user,startdate):
    #user = 'WB_Ermold' or 'pscapluw'
    psswd=userCred(user)

    today=datetime.datetime.now()
    enddate="%.2d/%.2d/%d" % (today.month,today.day,today.year)

    # xdaysago,fdoy=BT.xDaysAgo(daysago)
    # startdate="%.2d/%.2d/%d" % (xdaysago.month,xdaysago.day,xdaysago.year)
       
    strcommand='http://api.pacificgyre.com/api2/getData.aspx?userName='
    strcommand+=user+'&password='+psswd+'&startDate='+startdate
    strcommand+='&endDate='+enddate+'&commIDs='+bid+'&fileFormat=CSV'

    fid=urllib.request.urlopen(strcommand)
    data=fid.read()
    fid.close()
    data=str(data,'utf-8')

    rstartdate=startdate.replace('/','-')
    renddate=enddate.replace('/','-')
    opw=open('UPTEMPO/Raw_Data/UpTempO_'+bid+'_'+rstartdate+'-'+renddate+'.csv','w')
    opw.write(data)
    opw.close()

    os.system('cp UPTEMPO/Raw_Data/UpTempO_'+bid+'_'+rstartdate+'-'+renddate+'.csv UPTEMPO/PG_LastDownload_'+bid+'.csv')
##    os.system('cp UPTEMPO/Raw_Data/UpTempO_'+bid+'_'+rstartdate+'-'+renddate+'.csv /Users/wendye/UpTempO_HTML/Raw_Data/UpTempO_'+bid+'_'+rstartdate+'-'+renddate+'.csv')
    

def getARGOS(bid):

    today=datetime.datetime.now()
    strdate="%d%.2d%.2d" % (today.year,today.month,today.day)
    ubids={'300234061160500':'199070'}
    
    datapath='http://localhost:8888/SOAP_AORI3_DATA.php?bid='+ubids[bid]
    f = urllib.request.urlopen(datapath)
    time.sleep(20)
    data=f.read()
    f.close()
    data=data.decode('utf-8')
    opw=open('UPTEMPO/Raw_Data/ArgosData_'+strdate+'_'+bid+'.dat','w')
    opw.write(data)
    opw.close()

    os.system('cp UPTEMPO/Raw_Data/ArgosData_'+strdate+'_'+bid+'.dat UPTEMPO/ARGOS_LastDownload_'+bid+'.dat')
    

    
    


#    os.system('./FUNC_system_calls_toot.py ArgUP_UPTEMPO')
    #bid=300234061160500 = 2020_01_MIRAI, with Argos code: 199070
    #Data is in ARGOS_DATA/AORI3_UPTEMPO/300234061160500.dat
    
    
