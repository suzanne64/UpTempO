#!/usr/bin/python
import os
import sys
import time
import datetime
import BuoyTools_py3_toot as BT
import PlottingFuncs as PF
import numpy as np
import UpTempO_BuoyMaster as BM
import UpTempO_Downloads as upd
import ftplib
from ftplib import FTP


def StatsReport(lupdate):

    curbuoys,deadbuoys,orderbuoys,newdead=BM.getBuoys()

    oph=open('UPTEMPO/WebPlots/STATS-REPORT.txt','r')
    have=oph.read()
    oph.close()
    have=have.split('\n')[0:-1]
    haveinf={}
    for h in have:
        sh=h.split(',')
        haveinf[sh[11]]=h  # makes the buoy ID the key
        if sh[11] == '300034013618650':
            print(haveinf)
    
    for b in orderbuoys:
        if (b in curbuoys) or (b in newdead):
            print(b)
            if b in haveinf: statline=haveinf[b]
            else: statline=''
            
            binf=BM.BuoyMaster(b)  # buoy info
            
            try:
                abbv,byear,depdate,source=curbuoys[b]
            except:
                abbv,byear,depdate,source=newdead[b]

            opf=open('UPTEMPO/Processed_Data/'+b+'.dat','r')
            data=opf.read()
            opf.close()
            data=data.split('\n')
            head=data[0]
            data=data[1:]
            data=[d for d in data if d]

            if not statline:
                firstline=data[0]
                sfirst=firstline.split(' ')
                sfirst=[sf for sf in sfirst if sf]
                deplat=sfirst[4]
                deplon=sfirst[5]

                fdeplat=float(deplat)
                fdeplon=float(deplon)
                
                if float(deplon) < 0:
                    eorw='W'
                    fdeplon=-fdeplon
                else: eorw='E'
                sdeplon="%.2f" % fdeplon

                sdeplat="%.2f" % float(deplat)

                if float(deplat) < 0: nors='S '
                else: nors='N '

                depll=sdeplat+nors+sdeplon+eorw
                statlist=[binf['name'][1],binf['vessel'],depdate,depll,'','','',abbv,'NA','0',binf['name'][0],b,'','1']
            else:
                statlist=statline.split(',')

            if b in newdead: statlist[-5]='1'
        

           
            lastline=data[-1]
            slast=lastline.split(' ')
            slast=[sl for sl in slast if sl]
            lastyr=slast[0]
            lastmo=slast[1]
            lastda=slast[2]
            lasthr=slast[3]
            lastlat=slast[4]
            lastlon=slast[5]
            lastdate='/'.join([lastmo,lastda,lastyr])

            flastlon=float(lastlon)
            flastlat=float(lastlat)
            if flastlon < 0: slastlon="%.2f" % (-flastlon)
            else: slastlon="%.2f" % (flastlon)
            slastlat="%.2f" % flastlat
            if flastlat < 0: nors='S '
            else: nors='N '
            if flastlon < 0: eorw='W'
            else: eorw='E'

            lastll=slastlat+nors+slastlon+eorw
 
            depdate=depdate.split(' ')[0]
            amlistening=binf['listening']

            statlist[4]=lastdate
            statlist[5]=lastll
            statlist[6]=lupdate

            if statlist[12] == 'NA' or not statlist[12]:
                wmo=BT.lookupWMO(b)
                statlist[12]=wmo
            statlist[13]=amlistening
            jout=','.join(statlist)
            haveinf[b]=jout


    opw=open('UPTEMPO/WebPlots/STATS-REPORT.txt','w')
    for b in orderbuoys:
        opw.write(haveinf[b]+'\n')
    opw.close()


def UploadToPSC():

    transrecs='UPTEMPO/transferRecord.dat'
    opf=open(transrecs,'r')
    tfiles=opf.read()
    opf.close()
    tfiles=tfiles.split('\n')
    tfiles=[tf for tf in tfiles if tf]

    datarecs='UPTEMPO/DataFilesToTransfer.dat'
    opf=open(datarecs,'r')
    tdata=opf.read()
    opf.close()
    tdata=tdata.split('\n')
    tdata=[td for td in tdata if td]


    ftp=FTP('psctestsite.org')
    ftp.login('psctestsite.org','Ice+Melt3go')
    ftp.cwd('UpTempO')


    for f in tfiles:
        tup=f.split(' ')
        tofile=tup[1]
        fromfile=tup[0]
        try:
            ftp.storbinary('STOR '+tofile,open(fromfile,'rb'))
            print('TRANSFER SUCCESSFUL: '+tofile)
        except ftplib.all_errors:
            print('This data file did not go: '+tofile)
            

    print('Transfering Data Files...')
    for d in tdata:
        tup=d.split(' ')
        tofile=tup[1]
        fromfile=tup[0]
        try:
            ftp.storbinary('STOR '+tofile,open(fromfile,'rb'))
            print('DATA TRANSFER SUCCESSFUL: '+tofile)
        except ftplib.all_errors:
            print('This data file did not go: '+tofile)

    ftp.quit()
 
def DownloadFromPSC(fname):
    #fname = 'BuoyInfo.php' Individual buoy plots
    #fname = 'Data.php' main Data & Graphics page

    putpath='UPTEMPO/DownloadedFromPSC/'+fname
    
    ftp=FTP('psctestsite.org')
    ftp.login('psctestsite.org','Ice+Melt3go')
    ftp.cwd('UpTempO')
    
    with open(putpath,'wb') as fp:
        ftp.retrbinary('RETR '+fname,fp.write)

    ftp.quit()

       
    
def BatteryStats():

    curbuoys,deadbuoys,orderbuoys,newdead=BM.getBuoys()
    for o in orderbuoys:
        dinf=loadUpTempO(o)
    
        
        
        
        
        
    

    
    

