import os
import time
import datetime
import sys
import urllib


def PGheaderCodes(header):
    #Feed in header array
    #RETURN hinds={abbrev. header:ind}

    hdict={'CommId':'BuoyID','DeviceDateTime':'Date','BarometricPressure':'BP','BatteryVoltage':'BATT','Latitude':'Lat','Longitude':'Lon',
           'SubmergedPercent':'SUB','Temperature0cm':'Ts','WindDirection':'WindDir','WindSpeed':'WindSpeed',
           '37IMPressure':'CTD-P','37IMSalinity':'CTD-S','37IMSST':'CTD-T','37IMPressure1':'CTD-P1',
           '37IMSalinity1':'CTD-S1','37IMSST1':'CTD-T1','37IMPressure2':'CTD-P2','37IMSalinity2':'CTD-S2',
           '37IMSST2':'CTD-T2','37IMPressure3':'CTD-P3','37IMSalinity3':'CTD-S3','37IMSST3':'CTD-T3',
           '37IMPressure4':'CTD-P4','37IMSalinity4':'CTD-S4','37IMSST4':'CTD-T4',
           '37IMPressure5':'CTD-P5','37IMSalinity5':'CTD-S5','37IMSST5':'CTD-T5',
           '37IMPressure6':'CTD-P6','37IMSalinity6':'CTD-S6','37IMSST6':'CTD-T6',
           'DepthPod1':'D1','DepthPod10':'D10','DepthPod11':'D11','DepthPod12':'D12','DepthPod13':'D13','DepthPod14':'D14',
           'DepthPod15':'D15','DepthPod16':'D16','DepthPod17':'D17','DepthPod18':'D18','DepthPod19':'D19','DepthPod20':'D20',
           'DepthPod21':'D21','DepthPod22':'D22','DepthPod23':'D23','DepthPod24':'D24','DepthPod25':'D25','DepthPod2':'D2',
           'DepthPod3':'D3','DepthPod4':'D4','DepthPod5':'D5','DepthPod6':'D6','DepthPod7':'D7','DepthPod8':'D8','DepthPod9':'D9',
           'PressurePod1':'P1','PressurePod2':'P2','PressurePod3':'P3','PressurePod4':'P4','PressurePod5':'P5','PressurePod6':'P6',
           'TemperaturePod1':'T1','TemperaturePod10':'T10','TemperaturePod11':'T11','TemperaturePod12':'T12',
           'TemperaturePod13':'T13','TemperaturePod14':'T14','TemperaturePod15':'T15','TemperaturePod16':'T16',
           'TemperaturePod17':'T17','TemperaturePod17':'T18','TemperaturePod17':'T19','TemperaturePod17':'T20',
           'TemperaturePod17':'T21','TemperaturePod17':'T22','TemperaturePod17':'T23','TemperaturePod17':'T24',
           'TemperaturePod17':'T25','TemperaturePod2':'T2','TemperaturePod3':'T3','TemperaturePod4':'T4',
           'TemperaturePod5':'T5','TemperaturePod6':'T6','TemperaturePod7':'T7','TemperaturePod8':'T8','TemperaturePod9':'T9',
           'DataDateTime':'Date','GPSLatitude':'Lat','GPSLongitude':'Lon','SST':'SST','SurfaceSalinity':'SSSalt','BPress':'BP',
           'IridiumLatitude':'IrLat','IridiumLongitude':'IrLon','WindDir':'WindDir','WindSpeed':'WindSpeed',
           'TempPod1':'T1','TempPod2':'T2','TempPod3':'T3','TempPod4':'T4','TempPod5':'T5','TempPod6':'T6','TempPod7':'T7',
           'TempPod8':'T8','TempPod9':'T9','TempPod10':'T10','TempPod11':'T11','TempPod12':'T12','TempPod13':'T13',
           'TempPod14':'T14','TempPod15':'T15','TempPod16':'T16','TempPod17':'T17','TempPod18':'T18','TempPod19':'T19',
           'TempPod20':'T20','TempPod21':'T21','TempPod22':'T22','TempPod23':'T23','TempPod24':'T24','TempPod25':'T25',
           'PressPod1':'P1','PressPod2':'P2','PressPod3':'P3','SalinityTemp1':'CTD-S1','SalinityDepth1':'CTD-P1','Salinity1':'CTD-S1',
           'TiltPod1':'Tilt1','TiltPod2':'Tilt2','TiltPod3':'Tilt3','TiltPod4':'Tilt4','TiltPod5':'Tilt5','TiltPod6':'Tilt6',
           'TiltPod7':'Tilt7','TiltPod8':'Tilt8','TiltPod9':'Tilt9','TiltPod10':'Tilt10','TiltPod11':'Tilt11','TiltPod12':'Tilt12','AirTemp':'Ta',
           'AccelerometerVariance':'Accelerometer'}


    hinds={}
    track=[]
    c=0
    dups=0
    for h in header:
        if h in hdict.keys():
            hinds[hdict[h]]=c
            if hdict[h] in track:
                print('GOT DUPLICATE HEADER ENTRY!!')
                dups+=1
            track.append(hdict[h])
        c+=1
    hinds['N_DUPS']=dups
    return hinds

#===================================
def getOutHead(diver,hind):
    out='Year'+diver+'Month'+diver+'Day'+diver+'Hour'+diver+'Lat'+diver+'Lon'
    
    if 'P1' in hind:
        out += diver+'P1'

    if 'P2' in  hind:
       out += diver+ 'P2'

    if 'P3' in  hind:
        out += diver+ 'P3'

    if 'P4' in  hind:
        out += diver+'P4'

    for i in range(25):
        si="%d" % i
        if 'D'+si in  hind:
            out += diver+'D'+si

    if 'SST' in  hind:
        out += diver+'Ts'

    if 'Ts' in  hind:
        out += diver+'Ts'
        
    for i in range(25):
        si="%d" % i
        if 'T'+si in hind:
            out += diver+'T'+si

    if 'BP' in  hind:
        out +=diver+ 'SLP'

    if 'BATT' in  hind.keys():
        out += diver+'BATT'

    if 'SUB' in  hind:
        out += diver+'SUB'

    if 'CTD-P' in  hind:
        out += diver+'CTD-P'

    for i in range(25):
        si="%d" % i
        if 'CTD-P'+si in  hind:
            out += diver+'CTD-P'+si


    if 'CTD-S' in  hind:
        out += diver + 'CTD-S'
        
    for i in range(25):
        si="%d" % i
        if 'CTD-S'+si in  hind:
            out += diver+'CTD-S'+si

    if 'CTD-T' in  hind:
        out += diver + 'CTD-T'
        
    for i in range(25):
        si="%d" % i
        if 'CTD-T'+si in  hind:
            out += diver+'CTD-T'+si

    if 'WindDir' in  hind:
        out += diver + 'WindDir'

    if 'WindSpeed' in  hind:
        out += diver+'WindSpeed'


    for i in range(25):
        si="%d" % i
        if 'Tilt'+si in  hind:
            out += diver+'Tilt'+si

    return out
    
