#!/usr/bin/python
import os
import sys
import time
import datetime
import BuoyTools_py3_toot as BT
import UpTempO_BuoyMaster as BM
import UpTempO_HeaderCodes as HC
import UpTempO_Python as upy


def processDATA(bid,header,data,hinf,fts=1,pmod='PG'):


    binf=BM.BuoyMaster(bid)
    #find variables to look for
    fvars=['Dates','Lat','Lon']
    if 'pdepths' in binf:
        nd=len(binf['pdepths'])
        for i in range(nd):
            si="%d" % (i+1)
            fvars.append('P'+si)

            
    if 'ddepths' in binf:
        tdeps=binf['tdepths']
        ddep=binf['ddepths']

        nd=len(binf['ddepths'])
        for i in range(nd):
            cindex=tdeps.index(ddep[i])
            si="%d" % (cindex)
            fvars.append('D'+si)


    if 'ED1_ind' in binf:
        nd=len(binf['tdepths'])
        for i in range(nd):
            si="%d" % (i+1)
            fvars.append('D'+si)

    countt=0
    if fts:
        if 'Ts' in hinf:
            countt+=1
            fvars.append('Ts')
    
    if 'tdepths' in binf:
        nd=len(binf['tdepths'])
        for i in range(nd-countt):
            si="%d" % (i+1)
            fvars.append('T'+si)


    if 'sdepths' in binf:
        nd=len(binf['sdepths'])
        for i in range(nd):
            si="%d" % (i+1)
            fvars.append('S'+si)

    if 'CTDPs' in binf:
        nd=len(binf['CTDPs'])
        for i in range(nd):
            si="%d" % (nd[i])
            fvars.append('CTD-P'+si)

    if 'CTDTs' in binf:
        nd=len(binf['CTDTs'])
        for i in range(nd):
            si="%d" % (i+1)
            fvars.append('CTD-T'+si)

    if 'CTDSs' in binf:
        tdeps=binf['tdepths']
        ctdss=binf['CTDSs']
        
        nd=len(binf['CTDSs'])
        for i in range(nd):
            cindex=tdeps.index(ctdss[i])
            si="%d" % (cindex)
            fvars.append('CTD-S'+si)

    

    if 'bp_ind' in binf: fvars.append('BP')
    if 'ta_ind' in binf: fvars.append('Ta')
    if 'vbatt_ind' in binf: fvars.append('BATT')
    if 'sub_ind' in binf: fvars.append('SUB')



    #year,month,day,hour,lat,lon, OCEAN PRESSURES, ESTIMATED DEPTHS, TEMP DEPTHS, CTD-Ps, CTD-Ts, CTD-Ss, bp, ta, batt, sub
    sto=[]
    rown=0
    for d in data:
        if ',' in d: sd=d.split(',')
        else: sd=d.split(';')

        try:
            cdate=sd[hinf['Date']]
        except:
            print('failed sd[hinf[Date]]')
            print('d: '+d)
            print(rown)
            return 0
        rown+=1
        if '/' in cdate: spl='/'
        else: spl='-'
        cyear,cmonth,cday,chour,cmin,csec,cdoy,q=BT.processDate(cdate,spliton=spl)
        clat=sd[hinf['Lat']]
        clon=sd[hinf['Lon']]

        if 'Ts' in hinf: its=hinf['Ts']
        else: its = -1

        outline=[cyear,cmonth,cday,chour,clat,clon]
        for f in fvars[3:]:
            if sd[hinf[f]]:
                if ('P' in f) and (f != 'BP'):
                    fp=float(sd[hinf[f]])
                    if pmod == 'PG': fp=fp*.1
                    if pmod == 'MY':
                        cbp=float(sd[hinf['BP']])
                        fp=MY_OP_Correction(fp,cbp)
                    pout="%.3f" % fp
                    outline.append(pout)
                else: outline.append(sd[hinf[f]])
            else: outline.append('-999')

        jout=';'.join(outline)
        sto.append(jout)

    outhead='Year;Month;Day;Hour;Lat;Lon;'
    jvars=';'.join(fvars[3:])
    outhead+=jvars
    
    opw=open('UPTEMPO/LastUpdate/'+bid+'.dat','w')
    opw.write(outhead+'\n')
    for s in sto: opw.write(s+'\n')
    opw.close()
    

def processARGOS(bid):

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

    
def processPG(bid):

    rawpath='UPTEMPO/PG_LastDownload_'+bid+'.csv'
    opr=open(rawpath,'r')
    data=opr.read()
    opr.close()
    data=data.replace('"','')
    data=data.split('\n') #[0:-1]
    header=data[0].split(',')
    data=data[1:]
    data=[da for da in data if da]

    hinf=HC.PG_HeaderCodes(header)
    binf=BM.BuoyMaster(bid)
    
    processDATA(bid,header,data,hinf)  #fts=1 by default (Ts column is different from T1)
                                       #fts=0 Ts coloum is same as T1     
                                       #pmod='PG' by default (multiply Ocean Pressure by 0.1)
    appendProcessed(bid,order=-1)
    #WebFormat(bid)
    

        
def appendProcessed(bid,order=-1,fts=1):
    #fts = look for Ts data (1) or not (0)
    #order = new data is in order(1) or new data is in reverse order(-1)
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

    opw=open('UPTEMPO/Processed_Data/'+bid+'.dat','w')
    for h in have: opw.write(h+'\n')
    opw.close()
    
        
#======================================================================   
def WebFormat(bid,fts=1,order=-1,newdead=0):

    opf=open('UPTEMPO/LastUpdate/'+bid+'.dat','r')
    data=opf.read()
    opf.close()
    data=data.replace(';',' ')
    data=data.split('\n')
    data=[da for da in data if da]
    header=data[0]
    data=data[1:]
    nd=len(data)

    if order == -1:
        rdata=[]
        for r in range(nd):
            rdata.append(data[nd-1-r])
        data=rdata

    shead=header.split(' ')

    binf=BM.BuoyMaster(bid)
    binfn1="%.2d" % int(binf['name'][1])

    fname='UpTempO_'+binf['name'][0]+'_'+binfn1+'_'+binf['vessel']+'-Last.dat'

    today=datetime.datetime.now()
    lastUpdate="%.2d/%.2d/%d" % (today.month,today.day,today.year)


    lastline=data[-1].split(' ')
    dolt="%.2d/%.2d/%d" % (int(lastline[1]),int(lastline[2]),int(lastline[0]))
    
    
    if os.path.isfile('UPTEMPO/WebData/'+fname):
        opweb=open('UPTEMPO/WebData/'+fname,'r')
        have=opweb.read()
        opweb.close()
        have=have.split('\n')
        have=[ha for ha in have if ha]
        header=[ha for ha in have if '%' in ha]
        hdata=[ha for ha in have if '%' not in ha]

        header[5]='%DATE OF LAST TRANSMISSION: '+dolt
        header[6]='%DATE OF LAST DATA FILE UPDATE: '+lastUpdate

        for d in data:
            if d not in hdata: hdata.append(d)

        opw=open('UPTEMPO/WebData/'+fname,'w')
        for h in header: opw.write(h+'\n')
        for hd in hdata: opw.write(hd+'\n')
        opw.close()
    else:
        depline=data[0].split(' ')
        wmo=BT.lookupWMO(bid)
        depDate="%.2d/%.2d/%d" % (int(depline[1]),int(depline[2]),int(depline[0]))
        fdeplat=float(depline[4])
        fdeplon=float(depline[5])
        
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
        
        webhead=['%UpTempO '+binf['name'][0]+' #'+binfn1,
             '%Iridium ID: '+bid,
             '%WMO: '+wmo,
             '%DATE DEPLOYED: '+depDate,
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

        tdepths=binf['tdepths']
        eddepths=binf['tdepths'].copy()
        
        if 'pdepths' in binf: pdepths=binf['pdepths']
        if 'ddepths' in binf: ddepths=binf['ddepths']
        if 'CTDSs' in binf: CTDSs_depths=binf['CTDSs']
        if 'sdepths' in binf: sdepths=binf['sdepths']
##        print(sdepths)
        
        

##        print(tdepths)
        shead=header.split(' ')[6:]
        col=6

        for h in shead:
            if 'T' in h:
                if 'CTD' not in h:
                    if h == 'BATT':
                        strcol="%d" % col
                        lineout='% '+strcol+' = Battery Voltage (V)'
                    else:
                        if h == 'Ta':
                            strcol="%d" % col
                            lineout='% '+strcol+' = Air Temperature (C)'
                            col+=1
                        else:
                            cdep=tdepths.pop(0)
                            strdep,strcol=strDepColi(cdep,col)
                            lineout='% '+strcol+' = Temperature at nominal depth '+strdep+' (m)'
                    col+=1

            if 'S' in h:
                if (h != 'SUB') & ('CTD' not in h):
                    cdep=sdepths.pop(0)
                    strdep,strcol=strDepColi(cdep,col)
                    lineout='% '+strcol+' = Salinity at nominal depth '+strdep+' (m)'
                    col+=1
                
            if 'D' in h:
                cdep=eddepths.pop(0)
                strdep,strcol=strDepColi(cdep,col)
                lineout='% '+strcol+' = Estimated depth at nominal depth '+strdep+' (m)'
                col+=1
                

            if 'P' in h:
                if h == 'BP':
                    strcol="%d" % col
                    lineout='% '+strcol+' = Sea Level Pressure (mBar)'
                else:
                    cdep=pdepths.pop(0)
                    strdep,strcol=strDepColi(cdep,col)
                    lineout='% '+strcol+' = Ocean Pressure (dB) at Sensor #'+h[1]+'(Nominal Depth = '+strdep+' m)'
                col+=1

            if 'CTD-S' in h:
                cdep=CTDSs_depths.pop(0)
                strdep,strcol=strDepColi(cdep,col)
                lineout='% '+strcol+' = Salinity at Sensor #'+h[-1]+'(Nominal Depth = '+strdep+' m)'
                col+=1

            if h == 'SUB':
                strcol="%d" % col
                lineout='% '+strcol+' = Submergence Percent'
                col+=1
                

            webhead.append(lineout)

        webhead.append('%END')

        opw=open('UPTEMPO/WebData/'+fname,'w')
        for w in webhead: opw.write(w+'\n')
        for d in data: opw.write(d+'\n')
        opw.close()

    strtoday="%d%.2d%.2d" % (today.year,today.month,today.day)
    if newdead: newfname=fname.replace('Last','FINAL')
    else: newfname=fname.replace('Last',strtoday)
    os.system('cp UPTEMPO/WebData/'+fname+' UPTEMPO/WebData/'+newfname)


    return 'UPTEMPO/WebData/'+newfname    
    
    
                    
#===========================
def strDepColi(p,c):
    strdep="%.1f" % p
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
    
    
    
        
    
    
