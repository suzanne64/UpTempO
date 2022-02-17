#!/usr/bin/python
import os
import sys
import time
import datetime
import ftplib
from ftplib import FTP
import numpy as np
#import timedelta
import PlottingFuncs as pfuncs

#import urllib3 as urllib


HEADOUT='BuoyID;Year;Hour;Min;DOY;POS_DOY;Lat;Lon;BP;Ts;Ta'

def processDate(adate,spliton='/',mdy=0):
    #adate has the format yyyy/mm/dd hh:mm:ss
    # spliton is the date separater.
    #RETURN: list [year, month, day, hour, min, sec, doy in decimal to the minute]
    try:
        divydatetime=adate.split(' ')
        divydate=divydatetime[0].split(spliton)
        divytime=divydatetime[1].split(':')
        if float(divytime[0]) != int(float(divytime[0])):
            extraminutes=float(divytime[0])-int(float(divytime[0]))
            emm=extraminutes*60
            totalminutes=float(divytime[1])+emm
            divytime[1]="%2.2d" % totalminutes
            divytime[0]="%2.2d" % int(float(divytime[0]))
        if mdy:
            dtobj=datetime.datetime(int(divydate[2]),int(divydate[0]),int(divydate[1]))
        else:
            dtobj=datetime.datetime(int(divydate[0]),int(divydate[1]),int(divydate[2]))
        daynum=float(dtobj.timetuple().tm_yday)+float(divytime[0])/24.+float(divytime[1])/1440.
        fdaynum="%.4f" % daynum
        dechour=float(divytime[0])+float(divytime[1])/60.
        sdechour="%5.2f" % dechour
        datetimelist=[divydate[0],divydate[1],divydate[2],divytime[0],divytime[1],divytime[2],fdaynum,sdechour]
        return(datetimelist)
    except:
        return(['-999','-999','-999','-999','-999','-999','-999','-999'])
#=============================
##def Date2Doy(adate,spliton='-'):
##    #yyyy-mm-dd hh:mm:ss
##
##    cdate,ctime=adate.split(' ')
##    cyear,cmonth,cday=cdate.split(spliton)
##    chh,cmm,css=ctime.split(':')
##
##    dtobj=datetime.datetime(int(cyear),int(cmonth),int(cday))
##    daynum=float(dtobj.timetuple().tm_yday)+float(chh)/24.+float(cmm)/1440.
##    fdaynum="%.4f" % daynum
##
##    return fdaynum
###===============================
def fileExists(afile):

    if os.path.isfile(afile): return(1)
    else: return(0)

#===============================
def appendProcessed(fromfile,tofile,recsplit=';',nheadlines=0,sortind=[4,1]):            
    
    today=datetime.datetime.now()
    strdate="%.4d-%.2d-%.2d" % (today.year,today.month,today.day)
    header='BuoyID;Year;Hour;Min;DOY;POS_DOY;Lat;Lon;BP;Ts;Ta\n'
    
    dataf=open(fromfile,'r')
    if nheadlines == 1:
        datatop=dataf.readline()
        
    data=dataf.read()
    dataf.close()

    data=data.replace(' ','')
   
    if os.path.isfile(tofile):
        tof=open(tofile,'r')
        toftop=tof.readline()
        tof.close()
        tof=open(tofile,'a')
    else:
        tof=open(tofile,'w')
        tof.write(header)



    tof.write(data)
    tof.close()
    sortby(tofile,sind=sortind[0],yind=sortind[1])
    os.rename(tofile+'.sorted.dat',tofile)
        
    deDup(tofile)
    os.rename(tofile+'.dedup.dat',tofile)
    #filterBad(tofile)

def FileList(cpath,spliton='.',cind=1,fcontains='dat'):
    #RETURNS list of files in directory "cpath" that when split with "spliton"
    #                   the "cind" element = "fcontains"
    filesout=[]
    ofiles=[f for f in os.listdir(cpath) if os.path.isfile(cpath+f)]
    for of in ofiles:
        try:
            divyof=of.split(spliton)
            if divyof[cind] == fcontains: filesout.append(of)
        except:
            pass

    return(filesout)

def sortby(afile,spliton=';',sind=4,yind=-1,nhead=1):
    #sort a file based on the column of data indicated by "sind"
    # "nhead" = the number of header lines. If multiple years
    # exist in the file, set yind to the year index.

    if not os.path.isfile(afile):
        print('No file found to sortby: '+afile)
    else:
        op=open(afile,'r')
        header=[]
        
        for h in range(nhead):
            top=op.readline()
            header.append(top)
                

        alist=[]
        calibline=''
        for line in op:
            if '46514calib' not in line:
                line=line.split('\n')[0]
                if spliton != ' ':
                    sline=line.split(' ')
                    line=[sl for sl in sline if sl]
                    line=''.join(il for il in line)
                divy=line.split(spliton)
                divy=[dv for dv in divy if dv]
                apdiv=[]
                for di in divy:
                    if di: apdiv.append(di)
                    else: apdiv.append('-999')
                divy=apdiv
                atup=tuple(divy)
                alist.append(atup)
                if len(atup) != 11:
                    print(atup)
            else:
                calibline=line
        op.close()

        
        ss=sorted(alist, key=lambda tup:float(tup[sind]))

        if yind != -1:
            pss=sorted(ss,key=lambda tup:float(tup[yind]))
            ss=pss


        
        out=open(afile+'.sorted.dat','w')
        #if calibline: out.write(calibline)
        for h in header: out.write(h)
        for sline in ss:
            lineout=''.join([sl.split('\n')[0]+spliton for sl in sline if sl !=' '])
            lineout=lineout.strip(';')+'\n'
            out.write(lineout)
        out.close()

def sortitGF(data,spliton=';',sind=4,yind=1,form="%d;%d;%.2d;%.2d;%.4f;%.4f;%.5f;%.5f;%.2f;%.2f;%.2f\n"):
    #data is a numpy array
    
    if len(np.shape(data)) == 1:        
        dataout=npToGeneralFormat(data,form=form)
        return dataout

    sortby=data[:,sind]
    inds1=np.lexsort([sortby])
    data=data[inds1,:]

    if yind != -1:
        sortby2=data[:,yind]
        inds2=np.lexsort([sortby2])
        data=data[inds2,:]

   
    dataout=[]
    for d in data:
        if len(d) > 1:
            t=tuple(d)
            try:
                out=form % t
                out=out.replace(' ','')
                out=out.replace('-999.00000','-999')
                out=out.replace('-999.0000','-999')
                out=out.replace('-999.00','-999')
                dataout.append(out)
            except:
                print('sort error: ')
                print(t)
            
    return dataout

##    opw=open(afile,'w')
##    opw.write(header)
##    for dat in dataout:
##        opw.write(dat)
##    opw.close()

def sortbydate(apath,dind=0,spliton='/',nhead=1):

    opf=open(apath,'r')
    if nhead: head=opf.readline()
    data=opf.read()
    data=data.replace('"','')
    data=data.replace('NAN','-999')
    data=data.split('\n')
    opf.close()

    out=[]
    have=[]
    for d in data:
        sd=d.split(',')
        if sd[0] not in have:
            have.append(sd[0])
            try:
                date,time=sd[0].split(' ')
                yy,mo,da=date.split(spliton)
                hh,mm,ss=time.split(':')
                datear=processDate(sd[0],spliton='-')
                aout=[datear[0],datear[6],yy,mo,da,hh,mm,ss]
                for s in range(len(sd)):
                    if s != 0: aout.append(sd[s])
                jout=';'.join(aout)
                out.append(jout)
            except:
                print('error with '+d)

    opw=open('tmp.dat','w')
    jout='\n'.join(out)
    opw.write(jout+'\n')
    opw.close()

    sortby('tmp.dat',sind=1,yind=0)
 #   os.remove('tmp.dat')

    opf=open('tmp.dat.sorted.dat','r')
    data=opf.read()
    opf.close()
    data=data.split('\n')[0:-1]
    
    opw=open(apath+'.sorted.dat','w')
    if nhead: opw.write(head)
    for d in data:
        sd=d.split(';')
        print(sd)
        rdate="%d/%.2d/%.2d %.2d:%.2d:%.2d" % (int(sd[2]),int(sd[3]),int(sd[4]),int(sd[5]),int(sd[6]),int(sd[7]))
        out=[rdate]
        for s in range(len(sd)):
            if s > 7: out.append(sd[s])

        jout=','.join(out)
        opw.write(jout+'\n')
    opw.close()

     

def findunique(alist):
    ulist=[]
    for a in alist:
        try:
            i=ulist.index(a)
        except:
            ulist.append(a)

    return(ulist)

                   
def deDup(afile,bycols=0,spliton=';'):
    #Deletes repeated lines in a file
    #bycols is a list of col indexs that should be check for uniqueness together
    #    bycols=[1,2,3], for example

    if not os.path.isfile(afile):
        print('No file found to deDup: '+afile)
    else:
        op=open(afile)
        alist=[]
        for line in op:
            if bycols == 0:
                alist.append(line)
            else:
                line=line.split('\n')[0]
                dline=line.split(spliton)
                outcomp=''
                for i in bycols:
                    outcomp += dline[i]
                    alist.append(outcomp)
                    
                    
                
        op.close()
        
        ulines=findunique(alist)
        out=open(afile+'.dedup.dat','w')

        if bycols == 0:
            for ul in ulines:
                out.write(ul)
        else:
            opf=open(afile,'r')
            for line in opf:
                sline=line.split('\n')[0]
                dline=sline.split(spliton)
                ci=''
                for i in bycols:
                    ci += dline[i]
                if ci in ulines:
                    out.write(line)
                    ulines.remove(ci)
                
        out.close()

def sortWMO():

    opr=open('WMO_NumbersEdit.txt','r')
    data=opr.read()
    opr.close()
    data=data.split('\n')

    newdata=[]
    for d in data:
        sd=d.split(';')
        print(sd)
        out=sd[0]+';'+sd[1]
        newdata.append(out)

    opw=open('WMO_NumbersEdit2.txt','w')
    jout='\n'.join(newdata)
    opw.write(jout)
    opw.close()


def getDOY():
    #returns the current year and day of year
    ctoday=datetime.datetime.now()
    cobj=datetime.datetime(ctoday.year,ctoday.month,ctoday.day)
    doy=[ctoday.year,float(cobj.timetuple().tm_yday)]
    return doy


def dateToDOY(year='2014',month='04',day='01',hour='00',mm='00'):
        
        dtobj=datetime.datetime(int(float(year)),int(float(month)),int(float(day)))
        daynum=float(dtobj.timetuple().tm_yday)+float(hour)/24.+float(mm)/1440.
        fdaynum="%.4f" % daynum
        return fdaynum

def isLeap(year):

    leaps=['1900','1904','1908','1912','1916','1920','1924','1928',
           '1932','1936','1940','1944','1948','1952','1956','1960',
           '1964','1968','1972','1976','1980','1984','1988','1992',
           '1996','2000','2004','2008','2012','2016','2020','2024',
           '2028','2032','2036','2040','2044','2048','2052','2056']

    if year in leaps: return True
    else: return False

def moInf(Mmm=1,mmm=0,MMM=0):

    if Mmm:
        out={'Jan':'01','Feb':'02','Mar':'03','Apr':'04',
             'May':'05','Jun':'06','Jul':'07','Aug':'08',
             'Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    if mmm:
        out={'jan':'01','feb':'02','mar':'03','apr':'04',
             'may':'05','jun':'06','jul':'07','aug':'08',
             'sep':'09','oct':'10','nov':'11','dec':'12'}
    if MMM:
        out={'JAN':'01','FEB':'02','MAR':'03','APR':'04',
             'MAY':'05','JUN':'06','JUL':'07','AUG':'08',
             'SEP':'09','OCT':'10','NOV':'11','DEC':'12'}

    return out

def DaysPerMonth(year):
    
    dpm=[31,28,31,30,31,30,31,31,30,31,30,31]
    if isLeap(year): dpm[1]=29

    cpm=[np.sum(dpm[0:i]) for i in range(len(dpm))]

    return cpm

def MonthFromDoy():

    mo=[1,2,3,4,5,6,7,8,9,10,11,12]
    cpm=DaysPerMonth('2021')
    cpm=np.asarray(cpm)
    cinf={}
    for i in range(366):
        w = cpm < i+1
        nw=np.sum(w)
        cinf[i+1]=mo[nw-1]

    return cinf

##def daysSince(cyear,cmonth,cday):
##
##    today=datetime.datetime.now()
##    startday=datetime.datetime(cyear,cmonth,cday)
##    dt=timedelta.Timedelta(today-startday)
##
##    return dt.days

    
#=======================================#
def allNum(c):

    if not c: return False

    nums=['0','1','2','3','4','5','6','7','8','9','.','-']
    for i in c:
        if i not in nums: return False

        
    return True

#=======================================#
def daydiff(today,compday):
    # today=[year, doy], compday=[year, doy]
    if today[0] == compday[0]:
        ddiff=float(today[1])-float(compday[1])
    else:
        yeardiff=float(today[0])-float(compday[0])
        todaydoy=float(today[1])+yeardiff*365.
        ddiff=float(todaydoy)-float(compday[1])
    return ddiff
        
#=======================================#
def xDaysAgo2(x,writeit=0):
    #returns year,doy from x days ago
    ctoday=datetime.datetime.now()
    lastweek=ctoday-datetime.timedelta(days=x)
    doy=dateToDOY(year=lastweek.year,month=lastweek.month,day=lastweek.day,hour=lastweek.hour,mm='00',ss='00')

    if writeit:
        opf=open('tmp.txt','w')
        opf.write(str(lastweek.year)+' '+doy)
        opf.close()
        
    return lastweek.year,float(doy)

#=====================================#
def DataInfo2(region='ARCTIC/'):

    if region == 'ARCTIC/':
        datapaths=['PACIFIC_GYRE_DATA/PROCESSED_DATA/','ARGOS_DATA/PROCESSED_NEW/','JOUBEH_DATA/PROCESSED_DATA/',
                   'EUMETNET_DATA/PROCESSED_DATA/','BAS_DATA/PROCESSED_DATA/','BAS_DATA/PROCESSED_DATA_NEW/','PacGyre_AWI/PROCESSED_DATA/',
                   'PacGyre_ASL/PROCESSED_DATA/','Icedrifter_DATA/PROCESSED_DATA/',
                   'CRELL_DATA/PROCESSED_DATA/','ITP_DATA/PROCESSED_DATA/','COLD_FACTS_DATA/PROCESSED_DATA/',
                   'SAMS_DATA/PROCESSED_DATA/','AOFB_DATA/PROCESSED_DATA/',
                   'AOML_DoD_DATA/PROCESSED_DATA/','SBD_DATA/PROCESSED_DATA/'+region,'GPS_TRACKER_DATA/PROCESSED_DATA/',
                   'GERMAN_DATA/PROCESSED_DATA/','SPOT_DATA/PROCESSED_DATA/',
                   'SAILDRONE_DATA/PROCESSED_DATA/','Cy_DATA/PROCESSED_DATA/','PacGyre_OSU/PROCESSED_DATA/',
                   'SIMBA_DATA/FMI_DATA/PROCESSED_DATA/','SIMBA_DATA/PRIC_DATA/PROCESSED_DATA/','TUT_DATA/PROCESSED_DATA/',
                   'SIMB3_DATA/PROCESSED_DATA/','PacGyre_AWI_Haas/PROCESSED_DATA/','SBD_DATA/PolonaSBD/PROCESSED_DATA/',
                   'SBD_DATA/RockBLOCK_DATA/PROCESSED_DATA/','SouthTek_DATA/PROCESSED_DATA/','IoTAS_GSheet_DATA/PROCESSED_DATA/']

    if region == 'ANTARCTIC/':
        datapaths=['ARGOS_DATA/PROCESSED_NEW/','AOML_DoD_DATA/PROCESSED_DATA/ANTARCTIC/',
                   'GERMAN_DATA/PROCESSED_DATA/ANTARCTIC/','SBD_DATA/PROCESSED_DATA/ANTARCTIC/',
                   'BAS_DATA/PROCESSED_DATA/ANTARCTIC/','PacGyre_AWI_Haas/PROCESSED_DATA/ANTARCTIC/']

    
    return datapaths

#========================================#
def whereis(bid):

    region='ARCTIC/'
    paths=['PACIFIC_GYRE_DATA/PROCESSED_DATA/','ARGOS_DATA/PROCESSED_NEW/','JOUBEH_DATA/PROCESSED_DATA/','JOUBEH_DATA/PROCESSED_NEW/ARCTIC/',
               'EUMETNET_DATA/PROCESSED_DATA/','BAS_DATA/PROCESSED_DATA/','BAS_DATA/PROCESSED_DATA_NEW/','PacGyre_AWI/PROCESSED_DATA/',
               'PacGyre_ASL/PROCESSED_DATA/','Icedrifter_DATA/PROCESSED_DATA/',
               'CRELL_DATA/PROCESSED_DATA/','ITP_DATA/PROCESSED_DATA/','COLD_FACTS_DATA/PROCESSED_DATA/',
               'SAMS_DATA/PROCESSED_DATA/','AOFB_DATA/PROCESSED_DATA/',
               'AOML_DoD_DATA/PROCESSED_DATA/','SBD_DATA/PROCESSED_DATA/ARCTIC/','GPS_TRACKER_DATA/PROCESSED_DATA/',
               'GERMAN_DATA/PROCESSED_DATA/','SPOT_DATA/PROCESSED_DATA/',
               'SAILDRONE_DATA/PROCESSED_DATA/','Cy_DATA/PROCESSED_DATA/','PacGyre_OSU/PROCESSED_DATA/',
               'SIMBA_DATA/FMI_DATA/PROCESSED_DATA/','SIMBA_DATA/PRIC_DATA/PROCESSED_DATA/','TUT_DATA/PROCESSED_DATA/',
               'SIMB3_DATA/PROCESSED_DATA/','PacGyre_AWI_Haas/PROCESSED_DATA/','SBD_DATA/PolonaSBD/PROCESSED_DATA/',
               'SBD_DATA/RockBLOCK_DATA/PROCESSED_DATA/','SouthTek_DATA/PROCESSED_DATA/','IoTAS_GSheet_DATA/PROCESSED_DATA/']

    foundit=0
    for p in paths:
        files=FileList(p)
        
        if bid+'.dat' in files:
            if not foundit: rans=p+bid+'.dat'
            print(p+bid+'.dat')
            foundit=1
        
    else:
        region='Antarctic/'
        paths=['ARGOS_DATA/PROCESSED_NEW/ANTARCTIC/','JOUBEH_DATA/PROCESSED_NEW/ANTARCTIC/','AOML_DoD_DATA/PROCESSED_DATA/ANTARCTIC/',
               'GERMAN_DATA/PROCESSED_DATA/ANTARCTIC/','SBD_DATA/PROCESSED_DATA/ANTARCTIC/','ARGOS_DATA/AARI_PROCESSED_DATA/ANTARCTIC/']
        for p in paths:
            files=FileList(p)
            if bid+'.dat' in files:
                if not foundit: rans=p+bid+'.dat'
                print(p+bid+'.dat')
                foundit=1

    if foundit: return(rans)
    else: return('none')
    
#==========================================#
def dateStamp():

    today=datetime.datetime.now()
    sdate="%d%.2d%.2d" % (today.year,today.month,today.day)

    return(sdate)

#===========================================#
def getStamp():
    today=datetime.datetime.now()

    strdate="%d/%.2d/%.2d %.2d:%.2d:%.2d" % (today.year,today.month,today.day,today.hour,today.minute,today.second)
    
    return strdate

#=============================
def Date2Doy(adate,spliton='-'):
    #yyyy-mm-dd hh:mm:ss

    cdate,ctime=adate.split(' ')
    cyear,cmonth,cday=cdate.split(spliton)
    chh,cmm,css=ctime.split(':')

    dtobj=datetime.datetime(int(cyear),int(cmonth),int(cday))
    daynum=float(dtobj.timetuple().tm_yday)+float(chh)/24.+float(cmm)/1440.+float(css)/86400.0
    fdaynum="%.4f" % daynum

    return fdaynum

#=============================
def xDaysAgo(x):
    #returns datetime object for date from x days ago, and doy from x days ago
    ctoday=datetime.datetime.now()
    daysago=ctoday-datetime.timedelta(days=x)
    strdate="%d/%.2d/%.2d %.2d:%.2d:%.2d" % (daysago.year,daysago.month,daysago.day,daysago.hour,daysago.minute,daysago.second)    
    doy=Date2Doy(strdate,spliton='/')

    return daysago,float(doy)

#=============================
def curDoyYr():
    
    currentDateObj=datetime.datetime.now()
    cdatestamp="%d-%.2d-%.2d" % (currentDateObj.year,currentDateObj.month,currentDateObj.day)
    currentDOY=float(Date2Doy(cdatestamp+' 00:00:00',spliton='-'))
    currentYr=currentDateObj.year

    return currentDOY,currentYr

#==============================
def dateList(yrdoys):

    datestoget=[]
    for d in yrdoys:
        ans=DOY2Date(d[0],d[1])
        strans="%d%.2d%.2d" % (ans[2],ans[0],ans[1])
        datestoget.append(strans)
    return datestoget

#=============================
def LastnDays(n):

    curDoy,curYr=curDoyYr()
    daten,doyn=xDaysAgo(n)
    yrn=daten.year

    idoyn=int(doyn)
    out=[]
    if yrn == curYr:
        rdoys=[idoyn+r+1 for r in range(n)]
        for r in rdoys:
            out.append([curYr,r])

    return out
        
#================================
def DOY2Date(yr,doy):
    
    fdoy=float(doy)
    invar=int(fdoy)

    decday=fdoy-invar
    dechour=decday*24.0
    inhour=int(dechour)
    decmin=(dechour-inhour)*60.0
    inmin=int(decmin)
    decsec=(decmin-inmin)*60.0
    insec=int(decsec)

    year="%d" % int(yr)
    ndays=[31,28,31,30,31,30,31,31,30,31,30,31]
    months=[1,2,3,4,5,6,7,8,9,10,11,12]
    if isLeap(year): ndays[1]=29
    cumdays=[]
    for n in range(len(ndays)+1): cumdays.append(np.sum(ndays[0:n]))
    
    for cd in range(len(months)):
        if (fdoy >= cumdays[cd]) and (fdoy < cumdays[cd+1]+1):
            ansmonth=months[cd]
            ansday=int(fdoy-float(cumdays[cd]))
            out=[ansmonth,ansday,yr,inhour,inmin,insec]
            return out

#===============================
def ArcOrAnt(afile):
    #afile is a general format file
    #BuoyID;Year;Hour;Min;DOY;POS_DOY;Lat;Lon;BP;Ts;Ta
    
    data=np.loadtxt(afile,skiprows=1,delimiter=';')

    try:
        lats=data[:,6]
        n=len(lats)
        nlats=np.sum(lats > 50.)
        slats=np.sum(lats <= -50.)
        mlats=np.sum((lats < 50.) & (lats > -50.))

        pn=float(nlats)/float(n)
        ps=float(slats)/float(n)
        pm=float(mlats)/float(n)

        if pn >= .6: return 'Arctic'
        if ps >= .6: return 'Antarctic'
        if pm >= .6: return 'Outside Domain'

        regs=['Arctic','Antarctic','Outside Domain']
        par=[pn,ps,pm]
        maxp=np.max(par)
        i=par.index(maxp)
        print('Inconclusive')
        print(regs)
        print(par)
        print
        print('Most probable region: '+reg[i])
        return 'Inconclusive: '+reg[i]+'('+str(par[i])

    except:
        print('failed check: '+afile)
        return 'failed'
    
#=================================
def RegionList():

    files=FileList('ALL_BUOYS/GeneralFormat/')
    opw=open('RegionList.txt','w')
    for f in files:
        reg=ArcOrAnt('ALL_BUOYS/GeneralFormat/'+f)
        bid=f.split('.')[0]
        opw.write(bid+':'+reg+'\n')
        
    opw.close()

#=======================================================================================
def npToGeneralFormat(data,form="%d;%d;%.2d;%.2d;%.4f;%.4f;%.5f;%.5f;%.2f;%.2f;%.2f"):

    special=0
    if len(form.split(';')) == 12: special=1
    if len(form.split(';')) == 10: special=2
    out=[]

    if len(np.shape(data)) == 1:
        if special == 1:
            a,b,c,d,e,f,g,h,i,j,k,l=data
            sd=form % (a,b,c,d,e,f,g,h,i,j,k,l)
        else:
            if special == 2:
                a,b,c,d,e,f,g,h,i,j=data
                sd=form % (a,b,c,d,e,f,g,h,i,j)

            else:
                a,b,c,d,e,f,g,h,i,j,k=data
                sd=form % (a,b,c,d,e,f,g,h,i,j,k)
        sd=sd.replace('-999.00000','-999')
        sd=sd.replace('-999.0000','-999')
        sd=sd.replace('-999.00','-999')
            
        out=[sd]
            
    else:
        for r in range(len(data[:,0])):
            row=data[r,:]
            if special == 1:
                a,b,c,d,e,f,g,h,i,j,k,l=data[r,:]
                sd=form % (a,b,c,d,e,f,g,h,i,j,k,l)
            else:
                if special == 2:
                    a,b,c,d,e,f,g,h,i,j=data[r,:]
                    sd=form % (a,b,c,d,e,f,g,h,i,j)
                else:
                    a,b,c,d,e,f,g,h,i,j,k=data[r,:]
                    sd=form % (a,b,c,d,e,f,g,h,i,j,k)
            sd=sd.replace('-999.00000','-999')
            sd=sd.replace('-999.0000','-999')
            sd=sd.replace('-999.00','-999')
            out.append(sd)

    return out
                      
#====================================#
def assignRegion(bids,region,source):
    #bids=[]
    #region = 'Arctic' or 'Antarctic'

    if os.path.isfile('Arctic.txt'):
        opf=open('MasterLists/Arctic.txt','r')
        parcs=opf.read()
        opf.close()
        parcs=parcs.split('\n')[0:-1]
        arcs={}
        for p in parcs:
            sp=p.split(';')
            arcs[sp[0]]=sp[1]
            
    else: arcs={}
    
    if os.path.isfile('Antarctic.txt'):
        opf=open('Antarctic.txt','r')
        pants=opf.read()
        opf.close()
        pants=pants.split('\n')[0:-1]
        ants={}
        for p in pants:
            sp=p.split(';')
            ants[sp[0]]=sp[1]
    else: ants={}


    if os.path.isfile('MasterLists/Ambiguous.txt'):
        opf=open('MasterLists/Ambiguous.txt','r')
        amb=opf.read()
        opf.close()
        amb=amb.split('\n')[0:-1]
        ambinf={}
        for a in amb:
            sa,reg=a.split(';')
            ambinf[sa]=reg
    else: ambinf={}
    

    for b in bids:
        if region == 'Arctic':
            if b not in arcs:
                if b in ants:
                    print(b+' has been assigned Arctic, but is also in Antarctic.')
                    if b in ambinf:
                        reg=ambinf[b]
                        if reg == 'N':
                            arcs[b]=source
                            del ants[b]
                            print('--removing '+b+' from Antarctic, assigning to Arctic.')
                            
                        if reg == '?':
                            arcs[b]=source
                            print('--adding '+b+' to Arctic as well.')
                            
                    else:
                        arcs[b]=source
                        print('--adding '+b+' to Arctic as well, and to Ambiguous.')
                        ambinf[b]='?'
                else: arcs[b]=source
            else:
                if arcs[b] == 'TBD': arcs[b]=source
        if region=='Antarctic':
            if b not in ants:
                if b in arcs:
                    print(b+' has been assigned Antarctic, but is also in Arctic.')
                    if b in ambinf:
                        reg=ambinf[b]
                        if reg == 'S':
                            ants[b]=source
                            del arcs[b]
                            print('--removing '+b+' from Arctic, assigning to Antarctic.')
                        if reg == '?':
                            ants[b]=source
                            print('--adding '+b+' to Antarctic as well.')
                    else:
                        ants[b]=source
                        print('--adding '+b+' to Antarctic as well, and to Ambiguous.')
                        ambinf[b]='?'
                else: ants[b]=source
            else:
                if ants[b] == 'TBD': ants[b]=source

    opw=open('MasterLists/Arctic.txt','w')
    for a in arcs:
        out=a+';'+arcs[a]
        opw.write(out+'\n')
    opw.close()

    opw=open('MasterLists/Antarctic.txt','w')
    for a in ants:
        out=a+';'+ants[a]
        opw.write(out+'\n')
    opw.close()

    opw=open('MasterLists/Ambiguous.txt','w')
    for a in ambinf:
        out=a+';'+ambinf[a]+'\n'
        opw.write(out)
    opw.close()
                        
def isUpdating(doy,yr,lastx=7):
    #lastx is how many days ago a file must have data to be considered updating
    

    
        yr=float(yr)
        doy=float(doy)

        
        curdoy,curyr=curDoyYr()
        if curyr == yr:
            if doy >= curdoy-lastx: return 1
            else: return 0
        else:
            if curdoy > lastx: return 0
            else:
                x=365.0-doy+curdoy
                if x < lastx: return 1
                else: return 0
 
def updatedtoday(doy,yr):

    yr=float(yr)
    doy=float(doy)
    curdoy,curyr=curDoyYr()

    if (yr == curDoyYr) and (int(doy) == int(curdoy)): return 1
    else: return 0

    
   
def getDates():
    #returns a list of dates: yesterday, today, tomorrow
    #in the format yyyy-mm-dd
    ctoday=datetime.datetime.now()
    yest=ctoday-datetime.timedelta(days=1)
    tomor=ctoday+datetime.timedelta(days=1)
    syest="%04d-%02d-%02d" % (yest.year,yest.month,yest.day)
    stoda="%04d-%02d-%02d" % (ctoday.year,ctoday.month,ctoday.day)
    stomor="%04d-%02d-%02d" % (tomor.year,tomor.month,tomor.day)
    cdates=[syest,stoda,stomor]
    return cdates

 
def lookupWMO(bid):

    opr=open('WMO_Numbers.dat')
    wmos=opr.read()
    wmos=wmos.split('\n')[0:-1]

    
    for w in wmos:
        if ';' in w:
            if w.split(';')[0] == bid: return w.split(';')[1]

    return 'NA'
        
def findYest(strdate):
    #strdate='yyyymmdd'

    year=int(strdate[0:4])
    month=int(strdate[4:6])
    day=int(strdate[6:])

    dateobj=datetime.datetime(year,month,day)
    yest=dateobj-datetime.timedelta(days=1)
    strdate="%d%.2d%.2d" % (yest.year,yest.month,yest.day)
    return strdate

def cumDOY(doys,yrs):
    
    uyrs=np.unique(yrs)
    addit=[0]
    for u in uyrs:
        if isLeap(u): addit.append(366.)
        else: addit.append(365.)

    for u in range(len(uyrs)):
        wu=yrs == uyrs[u]
        doys[wu]=doys[wu]+np.sum(addit[0:u+1])

    return doys

def sortindsByDates(datelist):
    #datelist = ['yyyy-mm-dd hh:mm:ss',...]
    #returns list sorted indexes
    
    doys=[]
    yrs=[]
    uyrs=[]
    for r in datelist:
        cyr=r.split('-')[0]
        try:
            doy=Date2Doy(r)
        except:
            print('error, got date: '+r)
            return r
        if cyr not in uyrs: uyrs.append(cyr)
        doys.append(float(doy))
        yrs.append(int(cyr))

    doys=np.asarray(doys)
    yrs=np.asarray(yrs)

    if len(uyrs) > 1:
        uyrs=np.asarray(uyrs)
        syr=np.argsort(uyrs)
        sortyrs=uyrs[syr]
        addit=[]
        daddit={}
        daddit[sortyrs[0]]=0
        for sy in sortyrs:
            if isLeap(sy): addit.append(366.0)
            else: addit.append(365.0)
            if sy not in daddit:
                daddit[sy]=np.sum(addit[0:-1])

        for da in daddit:
            wy=yrs == int(da)
            doys[wy]=doys[wy]+daddit[da]

    sdoys=np.argsort(doys)
    
    return sdoys
    
    
def calcVelocity(cumdoy,lat,lon):


    deldists=[]
    for r in range(len(lat)-1):
        cdist=pfuncs.dist_ll([lat[r+1]],[lon[r+1]],[lat[r]],[lon[r]])
        deldists.append(cdist)

    deldists=np.asarray(deldists)


    delhours=[]
    for r in range(len(cumdoy)-1):
        delday=cumdoy[r+1]-cumdoy[r]
        delhours.append(delday*24.0)

    velocity=np.zeros([len(cumdoy),4]) #cumdoy, lat, lon, vel
    velocity[:,0]=cumdoy
    velocity[:,1]=lat
    velocity[:,2]=lon

    for r in range(len(deldists)):
        if delhours[r] <= 0.0001: velocity[r+1,3]=0.0
        else: velocity[r+1,3]=deldists[r]/delhours[r]

    return velocity #km/hr

#======================
    
