#!/usr/bin/python
import os
import sys
import time
import datetime
# import BuoyTools_py3_toot as BT
import UpTempO_BuoyMaster as BM


def PG_HeaderCodes(header):
    #Feed in header array
    #RETURN hinds={abbrev. header:ind}

    hdict={'CommId':'BuoyID',
           'DeviceDateTime':'Date',
           'BarometricPressure':'BP',
           'BatteryVoltage':'BATT',
           'Latitude':'Lat',
           'Longitude':'Lon',
           'SubmergedPercent':'SUB',
           'Temperature0cm':'Ts',
           'WindDirection':'WindDir',
           'WindSpeed':'WindSpeed',
           '37IMPressure':'CTD-P',   '37IMSalinity':'CTD-S',   '37IMSST':'CTD-T',
           '37IMPressure1':'CTD-P1', '37IMSalinity1':'CTD-S1', '37IMSST1':'CTD-T1',
           '37IMPressure2':'CTD-P2', '37IMSalinity2':'CTD-S2', '37IMSST2':'CTD-T2',
           '37IMPressure3':'CTD-P3', '37IMSalinity3':'CTD-S3', '37IMSST3':'CTD-T3',
           '37IMPressure4':'CTD-P4', '37IMSalinity4':'CTD-S4', '37IMSST4':'CTD-T4',
           '37IMPressure5':'CTD-P5', '37IMSalinity5':'CTD-S5', '37IMSST5':'CTD-T5',
           '37IMPressure6':'CTD-P6', '37IMSalinity6':'CTD-S6', '37IMSST6':'CTD-T6',
           'DepthPod1':'D1','DepthPod10':'D10','DepthPod11':'D11','DepthPod12':'D12','DepthPod13':'D13','DepthPod14':'D14',
           'DepthPod15':'D15','DepthPod16':'D16','DepthPod17':'D17','DepthPod18':'D18','DepthPod19':'D19','DepthPod20':'D20',
           'DepthPod21':'D21','DepthPod22':'D22','DepthPod23':'D23','DepthPod24':'D24','DepthPod25':'D25','DepthPod2':'D2',
           'DepthPod3':'D3','DepthPod4':'D4','DepthPod5':'D5','DepthPod6':'D6','DepthPod7':'D7','DepthPod8':'D8','DepthPod9':'D9',
           'PressurePod1':'P1',
           'PressurePod2':'P2',
           'PressurePod3':'P3',
           'PressurePod4':'P4',
           'PressurePod5':'P5',
           'PressurePod6':'P6',
           'TemperaturePod1':'T1','TemperaturePod10':'T10','TemperaturePod11':'T11','TemperaturePod12':'T12',
           'TemperaturePod13':'T13','TemperaturePod14':'T14','TemperaturePod15':'T15','TemperaturePod16':'T16',
           'TemperaturePod17':'T17','TemperaturePod18':'T18','TemperaturePod19':'T19','TemperaturePod20':'T20',
           'TemperaturePod21':'T21','TemperaturePod22':'T22','TemperaturePod23':'T23','TemperaturePod24':'T24',
           'TemperaturePod25':'T25','TemperaturePod2':'T2','TemperaturePod3':'T3','TemperaturePod4':'T4',
           'TemperaturePod5':'T5','TemperaturePod6':'T6','TemperaturePod7':'T7','TemperaturePod8':'T8','TemperaturePod9':'T9',
           'DataDateTime':'Date',
           'GPSLatitude':'Lat',
           'GPSLongitude':'Lon',
           'SST':'Ts',
           'SurfaceSalinity':'SSSalt',
           'CTSalinityHull': 'Shull',
           'CTTemperatureHull': 'Thull',
           'BPress':'BP',
           'IridiumLatitude':'IrLat',
           'IridiumLongitude':'IrLon',
           'WindDir':'WindDir','WindSpeed':'WindSpeed',
           'TempPod1':'T1','TempPod2':'T2','TempPod3':'T3','TempPod4':'T4','TempPod5':'T5','TempPod6':'T6','TempPod7':'T7',
           'TempPod8':'T8','TempPod9':'T9','TempPod10':'T10','TempPod11':'T11','TempPod12':'T12','TempPod13':'T13',
           'TempPod14':'T14','TempPod15':'T15','TempPod16':'T16','TempPod17':'T17','TempPod18':'T18','TempPod19':'T19',
           'TempPod20':'T20','TempPod21':'T21','TempPod22':'T22','TempPod23':'T23','TempPod24':'T24','TempPod25':'T25',
           'PressPod1':'P1',
           'PressPod2':'P2',
           'PressPod3':'P3',
           'Salinity22cm':'S1',
           'Temperature22cm':'T1',

           'SalinityTemp1':'CTD-T1','SalinityDepth1':'CTD-P1','Salinity1':'CTD-S1',
           'TiltPod1':'Tilt1','TiltPod2':'Tilt2','TiltPod3':'Tilt3','TiltPod4':'Tilt4','TiltPod5':'Tilt5','TiltPod6':'Tilt6',
           'TiltPod7':'Tilt7','TiltPod8':'Tilt8','TiltPod9':'Tilt9','TiltPod10':'Tilt10','TiltPod11':'Tilt11','TiltPod12':'Tilt12',
           'AirTemp':'Ta',
           'AccelerometerVariance':'Accelerometer'}


    hinds={}
    for h in header:
        if h in hdict:
            hinds[hdict[h]]=header.index(h)

    return hinds


def ARGOS_HeaderCodes(header):
    hdict={'programNumber':'prog',
           'platformId': 'ARGOSbid',
           'wmo':'wmo',
           'platformType': 'btype',
           'platformModel': 'bmodel',
           'platformName': 'bname',
           'satellite': 'satellite',
           'bestMsgDate': 'Date',
           'observationDate': 'Date',
           'duration': 'duration',
           'nbMessage': 'nbMessage',
           'message120': 'message120',
           'bestLevel': 'bestLevel',
           'frequency': 'frequency',
           'locationDate': 'POSdate',
           'latitude': 'Lat',
           'longitude':'Lon',
           'altitude': 'alt',
           'locationClass': 'locClass',
           'gpsSpeed': 'gpsSpeed',
           'gpsHeading': 'gpsHeading',
           'AIRTEMP': 'Ta',
           'AIR TEMPERATURE': 'Ta',
           'AIR TEMP': 'Ta',
           'AIRTEMP_SY': 'Ta_SY',
           'AIRTMP_MAXI24': 'Ta_max',
           'AIRTMP_MINI24': 'Ta_min',
           'ATMPRES': 'BP',
           'BAROMETRIC PRESSURE': 'BP',
           'AIR PRESSURE': 'BP',
           'AIR PRESS': 'BP',
           'ATMPRES_SY': 'bp_SY',
           'BATTERY': 'BATT',
           'BAT VOLT': 'BATT',
           'GROUND TEMP': 'Ts',
           'SST': 'Ts',
           'SEATEMP': 'Ts',
           'SST2': 'Ts2',
           'PRETEND': 'pretend',
           'PRETEND_SY': 'pretend_SY',
           'TENDCAR_SY': 'tendcar_SY',
           'SUBMERGENCE': 'SUB',
           'SUBMER': 'SUB',
           'SUBM': 'SUB',
           'SALINITY': 'CTD-S1',
           'SALINITY2': 'CTD-S2',
           'TEMPERATURE': 'CTD-T1',
           'TEMPERATURE2': 'CTD-T2',
           'TEMP T01': 'T1',
           'TEMP T02': 'T2',
           'TEMP T03': 'T3',
           'TEMP T04': 'T4',
           'TEMP T05': 'T5',
           'TEMP T06': 'T6',
           'TEMP T07': 'T7',
           'TEMP T08': 'T8',
           'TEMP T09': 'T9',
           'TEMP T10': 'T10',
           'TEMP T11': 'T11',
           'TEMP T12': 'T12',
           'TEMP T13': 'T13',
           'TEMP T14': 'T14',
           'TEMP T15': 'T15',
           'TEMP T16': 'T16',
           'TEMP T17': 'T17',
           'TEMP T18': 'T18',
           'TEMP T19': 'T19',
           'PRESS P01': 'P1',
           'PRESS P02': 'P2',
           'PRESS P03': 'P3',
           'DEPTH T01': 'D1',
           'DEPTH T02': 'D2',
           'DEPTH T03': 'D3',
           'DEPTH T04': 'D4',
           'DEPTH T05': 'D5',
           'DEPTH T06': 'D6',
           'DEPTH T07': 'D7',
           'DEPTH T08': 'D8',
           'DEPTH T09': 'D9',
           'DEPTH T10': 'D10',
           'DEPTH T11': 'D11',
           'DEPTH T12': 'D12',
           'DEPTH T13': 'D13',
           'DEPTH T14': 'D14',
           'DEPTH T15': 'D15',
           'DEPTH T16': 'D16',
           'DEPTH T17': 'D17',
           'DEPTH T18': 'D18',
           'DEPTH T19': 'D19'}



    hinf={}
    for h in header:
        if h in hdict:
            hinf[hdict[h]]=header.index(h)

    return hinf
