#!/usr/bin/python
import os
import sys
import time


def getBuoys():

    # opf=open('UPTEMPO/UpTempO_Catalog_new2024.txt','r')
    opf=open('UPTEMPO/UpTempO_Catalog.txt','r')
    data=opf.read()
    opf.close()
    data=data.split('\n')  #[0:-1]
    data=[d for d in data if d]

    reporting={}
    dead={}
    newdead={}
    buoyorder=[]
    for d in data:
        sd=d.split(',')
        buoyorder.append(sd[0])
        if len(sd) == 5:  # still reporting
            if sd[4].split(':')[1] == 'NEWDEAD': newdead[sd[0]]=sd[1:]
            else: reporting[sd[0]]=sd[1:]
        else:
            dead[sd[0]]=sd[1:]

    return reporting,dead,buoyorder,newdead

#==========================================

def BMvarDefs():

    vardefs={'pdepths':'Ocean Pressure Sensor Depths',
             'tdepths':'Temperature Sensor Depths',
             'sdepths':'Salinity Sensor Depths',
             'P1_ind':'Index of first Ocean Pressure value',
             'T1_ind':'Index of first Temperature value',
             'ED1_ind':'Index of first Estimated Depth Value (Marlin-Yug)',
             'bp_ind':'Index of Barometric Pressure',
             'vbatt_ind':'Index of battery voltage',
             'ta_ind':'Index of Atmospheric Temperature',
             'sub_ind':'Index of submergence',
             'cpdepths':'CTD Sensor Depths',
             'ctdepths':'CTD Temperature Depths',
             'csdepths':'CTD Salinity Depths',
             'CTDP1_ind':'Index of first CTD Pressure',
             'CTDT1_ind':'Index of first CTD Temperature',
             'CTDS1_ind':'Index of first CTD Salinity'}

def BuoyMaster(bid):


    bids={
          '123451234512345':{'notes':'UpTempO 2022 #0', # test configuration
                             'name':['2022','0'],
                             'imeiabbv':'123451',
                             'wmo':'987654',
                             'deploymentDate':'',
                             'deploymentLon':'',
                             'deploymentLat':'',
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-SVPS-0001',
                             'tdepths':[0.0,2.5,5.0,7.5,10,15,20],
                             'pdepths':[10,20,30],
                             'CTDtdepths':[10,20,30],
                             'CTDsdepths':[10,20],
                             'CTDpdepths':[10,20,30],
                             'HULLtdepths':[0.44],
                             'HULLsdepths':[0.44],
                             'vbatt_ind':1,
                             'sub_ind':1},

#  --------------------------2024 buoys-------------------------------------

        '300434064047460':{'notes':'UpTempO 2024 #1', 
                           'name':['2024','1'],          
                           'imeiabbv':'047460',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-040',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},

        '300434064049430':{'notes':'UpTempO 2024 #2',  
                           'name':['2024','2'],            
                           'imeiabbv':'049430',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-041',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},

        '300434064968900':{'notes':'UpTempO 2024 #3', 
                           'name':['2024','3'],         
                           'imeiabbv':'968900',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-065',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},

        '300434064962870':{'notes':'UpTempO 2024 #4', 
                           'name':['2024','4'],           
                           'imeiabbv':'962870',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-077',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},

        '300434065034120':{'notes':'UpTempO 2024 #5', 
                           'name':['2024','5'],          
                           'imeiabbv':'034120',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-080',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},

        '300434064969860':{'notes':'UpTempO 2024 #6', 
                           'name':['2024','6'],             
                           'imeiabbv':'969860',
                           'wmo':'NA',
                           'deploymentDate':'05/16/2024',
                           'deploymentLon':-178, 
                           'deploymentLat':60,  
                           'vessel':'NOAA Twin Otter',
                           'brand':'University of Washington',
                           'pgname':'microSWIFT-082',
                           'tdepths':[0.5],         
                           'sdepths':[0.5],
                           'vbatt_ind':23},


        # '300234063219570':{'notes':'UpTempO 2024 #7', 
        #                    'name':['2024','7'],             
        #                    'imeiabbv':'219570',
        #                    'wmo':'NA',
        #                    'deploymentDate':'10/01/2024',
        #                    'deploymentLon':-156, 
        #                    'deploymentLat':71,  
        #                    'vessel':'Healy',
        #                    'brand':'',
        #                    'pgname':'PNNL_SPB_0001',
        #                    'tdepths':[0.2],         
        #                    'vbatt_ind':23},




#  --------------------------2023 buoys-------------------------------------


        '300434064041440':{'notes':'UpTempO 2023 #1', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','1'],           #  
                        'imeiabbv':'041440',
                        'wmo':'NA',
                        'deploymentDate':'06/15/2023',
                        'deploymentLon':-168.240540, 
                        'deploymentLat':67.898064,  
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-007',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},

        '300434064042420':{'notes':'UpTempO 2023 #2', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','2'],           #  
                        'imeiabbv':'042420',
                        'wmo':'NA',
                        'deploymentDate':'06/15/2023',
                        'deploymentLon':-168.953506,
                        'deploymentLat':67.675377,
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-021',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},

        '300434064046720':{'notes':'UpTempO 2023 #3', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','3'],           #  
                        'imeiabbv':'046720',
                        'wmo':'NA',
                        'deploymentDate':'06/16/2023',
                        'deploymentLon':-168.599060,
                        'deploymentLat':67.784035,
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-008',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},

        '300434064042710':{'notes':'UpTempO 2023 #4', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','4'],           #  
                        'imeiabbv':'042710',
                        'wmo':'NA',
                        'deploymentDate':'06/16/2023',
                        'deploymentLon':-167.877716,
                        'deploymentLat':68.016502,
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-012',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},

        '300534062891690':{'notes':'UpTempO 2023 #5', # Salinity Ball
                           'name':['2023','5'],           #  
                           'imeiabbv':'891690',
                           'wmo':'4802674',
                           'deploymentDate':'07/29/2023',
                           'deploymentLon':-157.045905,
                           'deploymentLat':72.036395,
                           'vessel':'Healy',
                           'brand':'Pacific Gyre',
                           'pgname':'UW-IB-SVPS-0005',
                           'tdepths':[0.14],
                           'tdepthsMadeBy':['PG'],
                           'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                           'HULLtdepthsMadeBy':['S9'],
                           'HULLsdepths':[0.38],          # hull
                           'HULLsdepthsMadeBy':['S9'],
                           'vbatt_ind':1,
                           'sub_ind':1,
                           'gps_ind':1},

        '300534062893740':{'notes':'UpTempO 2023 #6', # Salinity Ball
                           'name':['2023','6'],           #  
                           'imeiabbv':'893740',
                           'wmo':'4802675',
                           'deploymentDate':'07/29/2023',
                           'deploymentLon':-157.090813,
                           'deploymentLat':72.954506,
                           'vessel':'Healy',
                           'brand':'Pacific Gyre',
                           'pgname':'UW-IB-SVPS-0006',
                           'tdepths':[0.14],
                           'tdepthsMadeBy':['PG'],
                           'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                           'HULLtdepthsMadeBy':['S9'],
                           'HULLsdepths':[0.38],          # hull
                           'HULLsdepthsMadeBy':['S9'],
                           'vbatt_ind':1,
                           'sub_ind':1,
                           'gps_ind':1},

        '300534062895700':{'notes':'UpTempO 2023 #7', # Salinity Ball
                           'name':['2023','7'],           #  
                           'imeiabbv':'895700',
                           'wmo':'4802676',
                           'deploymentDate':'07/29/2023',
                           'deploymentLon':-157.831502,
                           'deploymentLat':72.927767,
                           'vessel':'Healy',
                           'brand':'Pacific Gyre',
                           'pgname':'UW-IB-SVPS-0007',
                           'tdepths':[0.14],
                           'tdepthsMadeBy':['PG'],
                           'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                           'HULLtdepthsMadeBy':['S9'],
                           'HULLsdepths':[0.38],          # hull
                           'HULLsdepthsMadeBy':['S9'],
                           'vbatt_ind':1,
                           'sub_ind':1,
                           'gps_ind':1},
        
        '300534063449630':{'notes':'UpTempO 2023 #8', # Salinity Ball
                           'name':['2023','8'],           #  
                           'imeiabbv':'449630',
                           'wmo':'4802678',
                           'deploymentDate':'09/16/2023',
                           'deploymentLon':-143.072099,
                           'deploymentLat':70.853401,
                           'vessel':'Mirai',
                           'brand':'Pacific Gyre',
                           'pgname':'UW-IB-SVPS-0009',      # NOTE: UW-IB-SVPS-0008 next summer?
                           'tdepths':[0.14],
                           'tdepthsMadeBy':['PG'],
                           'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                           'HULLtdepthsMadeBy':['S9'],
                           'HULLsdepths':[0.38],          # hull
                           'HULLsdepthsMadeBy':['S9'],
                           'vbatt_ind':1,
                           'sub_ind':1,
                           'gps_ind':1},

        '300434064040440':{'notes':'UpTempO 2023 #9', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','9'],           #  
                        'imeiabbv':'040440',
                        'wmo':'NA',
                        'deploymentDate':'09/21/2023',
                        'deploymentLon':-157.2373, 
                        'deploymentLat':71.2812,  
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-022',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},
        
        '300434064048220':{'notes':'UpTempO 2023 #10', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','10'],           #  
                        'imeiabbv':'048220',
                        'wmo':'NA',
                        'deploymentDate':'09/21/2023',
                        'deploymentLon':-149.9744, 
                        'deploymentLat':71.4873,  
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-038',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},
        
        '300434064044730':{'notes':'UpTempO 2023 #11', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','11'],           #  
                        'imeiabbv':'044730',
                        'wmo':'NA',
                        'deploymentDate':'09/21/2023',
                        'deploymentLon':-150.0241, 
                        'deploymentLat':71.9934,  
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-035',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},

        '300434064045210':{'notes':'UpTempO 2023 #12', # Jim Thomson's microSWIFT, salinity ball type
                        'name':['2023','12'],           #  
                        'imeiabbv':'045210',
                        'wmo':'NA',
                        'deploymentDate':'09/21/2023',
                        'deploymentLon':-149.9652, 
                        'deploymentLat':70.9912,  
                        'vessel':'NOAA Twin Otter',
                        'brand':'University of Washington',
                        'pgname':'microSWIFT-039',
                        'tdepths':[0.5],         
                        'sdepths':[0.5],
                        'vbatt_ind':23},
        
        '300534062897690':{'notes':'UpTempO 2023 #13', # 60M One Wire 2022 Mike Steele #19.pdf, in newBuoys_2023
                            'name':['2023','13'],           #  2023_One_Wire_T_Chain_Drifters_Data_Fields.xlsx
                            'imeiabbv':'897690',
                            'wmo':'4802672',                
                            'deploymentDate':'10/20/2023',
                            'deploymentLon':-149.96,
                            'deploymentLat':71.99,
                            'vessel':'SIZRS',
                            'brand':'Pacific Gyre',
                            'pgname':'UW-TC-1W-0019',       # NOTE UW-TC-1W-0017 bad deployment, destroyed
                            'tdepths':[0,2.5,5.0,7.5,10,15,20,25,30,35,40,50,60],         
                            'tdepthsMadeBy':['PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG'],
                            'pdepths':[20,40,60],
                            'pdepthsMadeBy':['PG','PG','PG'],
                            'bp_ind':1,
                            'vbatt_ind':1,
                            'sub_ind':1,
                            'gps_ind':1},
        
        # '300434064041420':{'notes':'UpTempO 2023 #b', # Jim Thomson's microSWIFT, salinity ball type
        #                 'name':['2023','b'],           #  
        #                 'imeiabbv':'041420',
        #                 'wmo':'NA',
        #                 'deploymentDate':'09/01/2023',
        #                 'deploymentLon':'', 
        #                 'deploymentLat':'',  
        #                 'vessel':'NOAA Twin Otter',
        #                 'brand':'University of Washington',
        #                 'pgname':'microSWIFT-026',
        #                 'tdepths':[0.5],         
        #                 'sdepths':[0.5],
        #                 'vbatt_ind':23},
        
        # '300434064049300':{'notes':'UpTempO 2023 #c', # Jim Thomson's microSWIFT, salinity ball type
        #                 'name':['2023','c'],           #  
        #                 'imeiabbv':'049300',
        #                 'wmo':'NA',
        #                 'deploymentDate':'09/01/2023',
        #                 'deploymentLon':'', 
        #                 'deploymentLat':'',  
        #                 'vessel':'NOAA Twin Otter',
        #                 'brand':'University of Washington',
        #                 'pgname':'microSWIFT-027',
        #                 'tdepths':[0.5],         
        #                 'sdepths':[0.5],
        #                 'vbatt_ind':23},
        
        
        
        # either h or i will be deployed, not both (supply chain woes)
        '300534063446630':{'notes':'UpTempO 2023 #h', # Salinity Ball
                           'name':['2023','h'],           #  
                           'imeiabbv':'446630',
                           'wmo':'4802677',
                           'deploymentDate':'09/01/2023',
                           'deploymentLon':'',
                           'deploymentLat':'',
                           'vessel':'Healy',
                           'brand':'Pacific Gyre',
                           'pgname':'UW-IB-SVPS-0008',
                           'tdepths':[0.14],
                           'tdepthsMadeBy':['PG'],
                           'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                           'HULLtdepthsMadeBy':['S9'],
                           'HULLsdepths':[0.38],          # hull
                           'HULLsdepthsMadeBy':['S9'],
                           'vbatt_ind':1,
                           'sub_ind':1,
                           'gps_ind':1},

        
        # '300434064606280':{'notes':'UpTempO 2023 #4', # Jim Thomson's microSWIFT, salinity ball type
        #                 'name':['2023','4'],           #  
        #                 'imeiabbv':'606280',
        #                 'wmo':'NA',
        #                 'deploymentDate':'06/15/2023',
        #                 'deploymentLon':-122.3216,  # PLACE HOLDER
        #                 'deploymentLat':47.6552,  # PLACE HOLDER
        #                 'vessel':'NOAA Twin Otter',
        #                 'brand':'University of Washington',
        #                 'pgname':'microSWIFT-010',
        #                 'tdepths':[0.5],         
        #                 'sdepths':[0.5],
        #                 'spddepths':[0.5],
        #                 'dirdepths':[0.5]},



#  --------------------------2022 buoys-------------------------------------

          '300534062898720':{'notes':'UpTempO 2022 #1', # Mike\ Steele\ ONR\ SVP-S2.pdf
                         'name':['2022','1'],           #  also ONR_SVPS2_37IM_DataFields_2022.pdf
                         'imeiabbv':'898720',
                         'wmo':'4802638',
                         'deploymentDate':'09/09/2022',
                         'deploymentLon':-150.020707,
                         'deploymentLat':72.257601,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-SVPS2-37IM-0001',
                         'tdepths':[0.14],          # SST 0.14
                         'tdepthsMadeBy':['PG'],
                         'HULLtdepths':[0.44],      # hull 0.44
                         'HULLtdepthsMadeBy':['SBE'],
                         'CTDtdepths':[5.],          # 37IM 5m
                         'CTDtdepthsMadeBy':['SBE'],
                         'HULLsdepths':[0.38],      # hull 0.38
                         'HULLsdepthsMadeBy':['SBE'],
                         'CTDsdepths':[5.],          # 37IM
                         'CTDsdepthsMadeBy':['SBE'],
                         'CTDpdepths':[5.],          # 37IM
                         'CTDpdepthsMadeBy':['SBE'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534062897730':{'notes':'UpTempO 2022 #2', # Mike\ Steele\ ONR\ SVP\ Salinity\ Ball\ 0004.pdf
                             'name':['2022','2'],       #  also, ONR_SVPS_DataFields_2022.pdf
                             'imeiabbv':'897730',
                             'wmo':'4802634',
                             'deploymentDate':'09/09/2022',
                             'deploymentLon':-149.958246,
                             'deploymentLat':72.976345,
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-IB-SVPS-0004',
                             'tdepths':[0.14],
                             'tdepthsMadeBy':['PG'],
                             'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                             'HULLtdepthsMadeBy':['SBE'],
                             'HULLsdepths':[0.38],          # hull
                             'HULLsdepthsMadeBy':['SBE'],
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

          '300534063704980':{'notes':'UpTempO 2022 #3', # Uptempo_NASA_Sound9_0002.pdf
                         'name':['2022','3'],           #  also, Nasa_T-Chain_DataFields_2022.pdf
                         'imeiabbv':'704980',
                         'wmo':'4802640',
                         'deploymentDate':'09/10/2022',
                         'deploymentLon':-150.022594,
                         'deploymentLat':72.406403,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-TC-S9-XT-XIM-0001',
                         'tdepths':[0.25,2.5,5.0,7.5,15,25,35,50],
                         'tdepthsMadeBy':['PG','S9','S9','S9','S9','S9','S9','S9'],
                         'CTDtdepths':[10,20,30,40,60],
                         'CTDtdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'CTDsdepths':[10,20,30,40,60],
                         'CTDsdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'CTDpdepths':[10,20,30,40,60],
                         'CTDpdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534063807110':{'notes':'UpTempO 2022 #4', # Mike\ Steele\ ONR\ SVP-S2_0002.pdf
                             'name':['2022','4'],           #  also ONR_SVPS2_37IM_DataFields_2022.pdf
                             'imeiabbv':'807110',
                             'wmo':'4802639',
                             'deploymentDate':'09/11/2022',
                             'deploymentLon':-150.873074,
                             'deploymentLat':72.184906,
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-SVPS2-37IM-0002', # UW-SVPS2-0002 ?
                             'tdepths':[0.14],          # SST 0.14
                             'tdepthsMadeBy':['PG'],
                             'HULLtdepths':[0.44],      # hull 0.44
                             'HULLtdepthsMadeBy':['SBE'],
                             'CTDtdepths':[5],          # 37IM 5m
                             'CTDtdepthsMadeBy':['SBE'],
                             'HULLsdepths':[0.38],      # hull 0.38
                             'HULLsdepthsMadeBy':['SBE'],
                             'CTDsdepths':[5],          # 37IM
                             'CTDsdepthsMadeBy':['SBE'],
                             'CTDpdepths':[5],          # 37IM
                             'CTDpdepthsMadeBy':['SBE'],
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

          '300534063803100':{'notes':'UpTempO 2022 #5', # Uptempo_NASA_Sound9_0002.pdf
                         'name':['2022','5'],           #  also, Nasa_T-Chain_DataFields_2022.pdf
                         'imeiabbv':'803100',
                         'wmo':'4802666',
                         'deploymentDate':'09/13/2022',
                         'deploymentLon':-149.187969,
                         'deploymentLat':73.285186,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-TC-S9-XT-XIM-0002',
                         'tdepths':[0.25,2.5,5.0,7.5,15,25,35,50],
                         'tdepthsMadeBy':['PG','S9','S9','S9','S9','S9','S9','S9'],
                         'CTDtdepths':[10,20,30,40,60],
                         'CTDtdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'CTDsdepths':[10,20,30,40,60],
                         'CTDsdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'CTDpdepths':[10,20,30,40,60],
                         'CTDpdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534062892700':{'notes':'UpTempO 2022 #6', # Mike\ Steele\ ONR\ SVPS_0001.pdf
                             'name':['2022','6'],       #  also, ONR_SVPS_DataFields_2022.pdf
                             'imeiabbv':'892700',       #  SVPS surface velocity program, TC cell and no ? droque
                             'wmo':'4802632',
                             'deploymentDate':'09/15/2022',
                             'deploymentLon':-144.908260,
                             'deploymentLat':72.540937,
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-SVPS-0001',
                             'tdepths':[0.14],
                             'tdepthsMadeBy':['PG'],
                             'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                             'HULLtdepthsMadeBy':['SBE'],
                             'HULLsdepths':[0.38],          # hull
                             'HULLsdepthsMadeBy':['SBE'],
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

          '300534062894700':{'notes':'UpTempO 2022 #7', # Mike\ Steele\ ONR\ SVP\ Salinity\ Ball\ 0003.pdf
                             'name':['2022','7'],       #  also, ONR_SVPS_DataFields_2022.pdf
                             'imeiabbv':'894700',
                             'wmo':'4802633',
                             'deploymentDate':'09/17/2022',
                             'deploymentLon':-145.860054,
                             'deploymentLat':73.077240,
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-IB-SVPS-0003',
                             'tdepths':[0.14],
                             'tdepthsMadeBy':['PG'],
                             'HULLtdepths':[0.44],     # SST 0.14, hull 0.44
                             'HULLtdepthsMadeBy':['SBE'],     # SST 0.14, hull 0.44
                             'HULLsdepths':[0.38],          # hull
                             'HULLsdepthsMadeBy':['SBE'],     # SST 0.14, hull 0.44
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

          '300534062894740':{'notes':'UpTempO 2022 #8', # Mike\ Steele\ NASA\ SVP-S2_0003.pdf
                             'name':['2022','8'],           #  also Nasa_SVPS_XIM_DataFields_2022.pdf
                             'imeiabbv':'894740',
                             'wmo':'4802637',
                             'deploymentDate':'09/20/2022',
                             'deploymentLon':-149.653811,
                             'deploymentLat':72.036372,
                             'vessel':'SASSIE',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-SVPS-XIM-0003',
                             'tdepths':[0.14],              # SST 0.14m
                             'tdepthsMadeBy':['PG'],
                             'CTDtdepths':[5],                 # 37IM 5m
                             'CTDtdepthsMadeBy':['S9'],
                             'CTDsdepths':[5],                 # 37IM
                             'CTDsdepthsMadeBy':['S9'],
                             'CTDpdepths':[5],                 # 37IM
                             'CTDpdepthsMadeBy':['S9'],
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

          '300534062896730':{'notes':'UpTempO 2022 #9', # Uptempo_ONR_Sound9_Seabird.pdf
                         'name':['2022','9'],           #  also, ONR_T-Chain_DataFields_2022.pdf
                         'imeiabbv':'896730',
                         'wmo':'4802667',
                         'deploymentDate':'09/20/2022',
                         'deploymentLon':-149.666614,
                         'deploymentLat':72.362386,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-TCS-37IM-S9XT-0001',
                         'tdepths':[0.25,2.5,5.0,7.5,15,25,35,50],
                         'tdepthsMadeBy':['PG','S9','S9','S9','S9','S9','S9','S9'],
                         'HULLtdepths':[0.57],
                         'HULLtdepthsMadeBy':['SBE'],
                         'CTDtdepths':[10,20,30,40,60],
                         'CTDtdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'HULLsdepths':[0.51],
                         'HULLsdepthsMadeBy':['SBE'],
                         'CTDsdepths':[10,20,30,40,60],
                         'CTDsdepthsMadeBy':['SBE','SBE','SBE','SBE','SBE'],
                         'CTDpdepths':[20,40,60],
                         'CTDpdepthsMadeBy':['SBE','SBE','SBE'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534062894730':{'notes':'UpTempO 2022 #10', # Mike\ Steele\ NASA\ SVP-S2_0002.pdf
                         'name':['2022','10'],           #  also Nasa_SVPS_XIM_DataFields_2022.pdf
                         'imeiabbv':'894730',
                         'wmo':'4802636',
                         'deploymentDate':'09/25/2022',
                         'deploymentLon':-150.500603,
                         'deploymentLat':73.002847,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-SVPS-XIM-0002',
                         'tdepths':[0.14],              # SST 0.14m
                         'tdepthsMadeBy':['PG'],
                         'CTDtdepths':[5],                 # 37IM 5m
                         'CTDtdepthsMadeBy':['S9'],
                         'CTDsdepths':[5],                 # 37IM
                         'CTDsdepthsMadeBy':['S9'],
                         'CTDpdepths':[5],                 # 37IM
                         'CTDpdepthsMadeBy':['S9'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534062893700':{'notes':'UpTempO 2022 #11', # Mike\ Steele\ NASA\ SVP-S2_0001.pdf
                         'name':['2022','11'],           #  also Nasa_SVPS_XIM_DataFields_2022.pdf
                         'imeiabbv':'893700',
                         'wmo':'4802635',
                         'deploymentDate':'09/25/2022',
                         'deploymentLon':-150.497286,
                         'deploymentLat':73.259164,
                         'vessel':'SASSIE',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-SVPS-XIM-0001',
                         'tdepths':[0.14],              # SST 0.14m
                         'tdepthsMadeBy':['PG'],
                         'CTDtdepths':[5],                 # 37IM 5m    (SBE)
                         'CTDtdepthsMadeBy':['S9'],
                         'CTDsdepths':[5],                 # 37IM
                         'CTDsdepthsMadeBy':['S9'],
                         'CTDpdepths':[5],                 # 37IM
                         'CTDpdepthsMadeBy':['S9'],
                         'vbatt_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},

          '300534062895730':{'notes':'UpTempO 2022 #12', # SIZRS_2022-12.png
                         'name':['2022','12'],           #  also
                         'imeiabbv':'895730',
                         'wmo':'4802669',
                         'deploymentDate':'10/12/2022',
                         'deploymentLon':-149.955533,
                         'deploymentLat':72.285642,
                         'vessel':'SIZRS',
                         'brand':'Pacific Gyre',
                         'pgname':'UW-TC-1W-0018',
                         'tdepths':[0.25,2.5,5.0,7.5,10,15,20,25,30,35,40,50,60],  # all made by PG, for the 1 wire drifters (see Glen email, uptempo/10.6.22)
                         'tdepthsMadeBy':['PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG','PG'],
                         'pdepths':[20,40,60],
                         'pdepthsMadeBy':['PG','PG','PG'],
                         'vbatt_ind':1,
                         'bp_ind':1,
                         'sub_ind':1,
                         'gps_ind':1},




#  --------------------------2021 buoys-------------------------------------

          '300534060649670':{'notes':'UpTempO 2021 #1',
                            'name':['2021','1'],
                            'imeiabbv':'649670',
                            'wmo':'',
                            'deploymentDate':'8/25/2021',
                            'deploymentLon':-150.035994,
                            'deploymentLat':72.052522,
                            'vessel':'SIZRS',
                            'brand':'Pacific Gyre',
                            'pgname':'UW-TC-S9C-0001',
                            'pdepths':[5.,10.,20.,25.],  # Called DepthPodx, changed from ddepths 2/1/2022
                            'CTDsdepths':[5.,10.,20.],   # sal readings at 5, 10, 20m
                            'tdepths':[0.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0],
                            'vbatt_ind':1,
                            'bp_ind':1,
                            'sub_ind':1,
                            'gps_ind':1},
          
          '300534060251600':{'notes':'UpTempO 2021 #2',
                             'name':['2021','2'],
                             'imeiabbv':'251600',
                             'wmo':'',
                             'deploymentDate':'9/15/2021',
                             'deploymentLon':-150.008014,
                             'deploymentLat':72.036603,
                             'vessel':'SIZRS',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-TC-1W-0016',
                             'pdepths':[20.,40.,60.],
                             'tdepths':[0.0, 2.5, 5., 7.5, 10., 15., 20., 25., 30., 35., 40., 50., 60.],
                             'bp_ind':1,
                             'sub_ind':1,
                             'vbatt_ind':1,
                             'gps_ind':1},

          '300534060051570':{'notes':'UpTempO 2021 #3',
                             'name':['2021','3'],
                             'imeiabbv':'051570',
                             'wmo':'',
                             'deploymentDate':'9/29/2021',
                             'deploymentLon':-152.502925,
                             'deploymentLat':57.736547,
                             'vessel':'SIZRS',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-TC-1W-0015',
                             'pdepths':[25],
                             'tdepths':[0.0,2.5, 5, 7.5, 10, 15, 20, 25],
                             'bp_ind':1,
                             'sub_ind':1,
                             'vbatt_ind':1,
                             'gps_ind':1},

          '300534062158480':{'notes':'UpTempO 2021 #4',
                             'name':['2021','4'],
                             'imeiabbv':'158480',
                             'wmo':'',
                             'deploymentDate':'10/13/2021',
                             'deploymentLon':-156.980291,
                             'deploymentLat':72.966354,
                             'vessel':'SIZRS',
                             'brand':'Pacific Gyre',
                             'pgname':'UW-IB-SVPS-0002',
                             'tdepths':[0,0.28],  # changed from 0.22 2/2/2022
                             'sdepths':[0.28],
                             'vbatt_ind':1,
                             'sub_ind':1,
                             'gps_ind':1},

 
          '300534062158460':{'notes':'UpTempO 2021 #5',
                            'name':['2021','5'],
                            'imeiabbv':'158460',
                            'wmo':'',
                            'deploymentDate':'11/02/2021',
                            'deploymentLon':-167.035249,
                            'deploymentLat':69.148342,
                            'vessel':'SIZRS',
                            'brand':'Pacific Gyre',
                            'pgname':'UW-IB-SVPS-0001',
                            'tdepths':[0,0.28],  # changed from 0.22 2/2/2022
                            'sdepths':[0.28],
                            'vbatt_ind':1,
                            'sub_ind':1,
                            'gps_ind':1},


#  --------------------------2020 buoys-------------------------------------
 
          '300234067939910':{'notes':'UpTempO 2020 JW-2',
                             'name':['2020','JW-2'],
                             'imeiabbv':'9910',
                             'vessel':'WARM',
                             'brand':'Pacific Gyre',
                             'tdepths':[3.,12.],
                             'cpdepths':[10.],
                             'ctdepths':[10.],
                             'T1_ind':6,
                             'CTDT1_ind':11,
                             'CTDS1_ind':10,
                             'CTDP1_ind':9,
                             'vbatt_ind':8},

       '300234061160500':{'notes':'UpTempO 2020 #1',
                            'name':['2020','1'],
                            'imeiabbv':'160500',
                            'deploymentDate':'11/10/2020',
                            'deploymentLon':207.9928,
                            'deploymentLat':76.4946,
                            'vessel':'MIRAI',
                            'brand':'Marlin-Yug',
                            'pdepths':[20.,40.,60.],
                            'tdepths':[0.,1.,4.,6.5,9.,12.,14.5,17.,20.,25.,30.,35.,40.,45.,50.,55.,60.],
                            'P1_ind':6,
                            'ED1_ind':9,
                            'T1_ind':26,
                            'bp_ind':43,
                            'vbatt_ind':7,
                            'ta_ind':45,
                            'sub_ind':46},

#  --------------------------2019 buoys-------------------------------------

	   '300234067936870':{'notes':'WARM 2019 W9',
                          'name':['2019','W-9'],
                          'brand':'Pacific Gyre',
                          'imeiabbv':'6870',
                          'deploymentDate':'03/31/2019',
                          'deploymentLon':-156.6791,
                          'deploymentLat':71.3257,
                          'vessel':'WARM',
                          'pdepths':9.,
                          'tdepths':[-1,3.3,9.],   # These changed May 2023 to reflect pres data beginning of time series 
                          # 'pdepths':10.,
                          # 'tdepths':[0.0,4.3,10.],
                          'T1_ind':7,
                          'P1_ind':6,
                          'vbatt_ind':10,
                          #****BIOSENSOR INFO****
                          'biosensors':['LI_192_0','LI_192_1','LI_192_2','LI_192_3','LI_192_4','LI_192_5','Cyclops_CHL'],
                          'biodepths':[0.0, 0.5, 1.0, 4.1, 6.4, 8.0, 4.7],
                          #----for "plot_warm" in webplots---
                          'lidepths':[0.0, 0.5, 1.0, 4.1, 6.4, 8.0]},

	   '300234068514830':{'inote':'DEPLOYED via airdrop by Jamie Morison 7/10/2019',
                          'notes':'UpTempO 2019 #1',
                          'name':['2019','1'],
                          'brand':'Pacific Gyre',
                          'imeiabbv':'4830',
                          'wmo':'4801660',
                          'deploymentDate':'7/30/2019',
                          'deploymentLon':-150.4506,
                          'deploymentLat':72.346753, 
                          'vessel':'SIZRS',
                          'pdepths':[20.0],
                          'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.],
                          'T1_ind':9,
                          'P1_ind':6,
                          'bp_ind':22,
                          'vbatt_ind':23,
                          'sub_ind':24},


	'300234068519450':{'inote':'DEPLOYED 8/13/2019 via SIZRS by Jamie Morison',
				'notes':'UpTempO 2019 #2',
				'name':['2019','2'],
				'brand':'Pacific Gyre',
				'imeiabbv':'9450',
                'wmo':'4801670',
                'deploymentDate':'8/14/2019',
                'deploymentLon':-149.817103,
                'deploymentLat':72.013322,
				'vessel':'SIZRS',
                'pgname':'UW-TC-1W-0014',
				'pdepths':[20.,40.,60.],
				'tdepths':[0.0,2.5,5.,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.],
				'T1_ind':9,
				'P1_ind':6,
				'bp_ind':22,
				'vbatt_ind':23,
				'sub_ind':24},

	'300234068719480':{'inote':'Deployed 9/12/2019 via SIZRS by Mike',
                           'notes':'UpTempO 2019 #3',
                           'name':['2019','3'],
                           'brand':'Pacific Gyre',
                           'imeiabbv':'9480',
                           'deploymentDate':'09/122019',
                           'deploymentLon':-149.9738,
                           'deploymentLat':72.0200,
                           'vessel':'SIZRS',
                           'pdepths':[25.],
                           'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.],
                           'reportTilt':1,
                           'tiltdepths':[2.5,5.0,7.5,10.,15.,20.,25.],
                           'T1_ind':7,
                           'P1_ind':6,
                           'bp_ind':15,
                           'vbatt_ind':16,
                           'sub_ind':17,
                           'tilt1_ind':24},

        '300234060320930':{'inote':'NOT YET DEPLOYED (ETD = mid aug) --> NABOS cruise cancelled',
                           'notes':'UpTempO 2019 #4',
                           'name':['2019','4'],
                           'brand':'Marlin-Yug',
                           'imeiabbv':'320930',
                           'deploymentDate':'10/28/2019',
                           'deploymentLon':128.6381,
                           'deploymentLat':85.5843,
                           'vessel':'MOSAiC',
                           'pdepths':[25],
                           'tdepths':[0.,2.5,5.0,7.5,10.,15.,20.,25.],
                           'ED1_ind':6,
                           'P1_ind':14,
                           'T1_ind':16,
                           'bp_ind':24,
                           'vbatt_ind':25,
                           'sub_ind':26},



          '300234060320940':{'notes':'UpTempO 2019 #5',
                             'name':['2019','5'],
                             'brand':'Marlin-Yug',
                             'imeiabbv':'320940',
                             'deploymentDate':'10/28/2019',
                             'deploymentLon':128.6381,
                             'deploymentLat':85.5843,
                             'vessel':'MOSAiC',
                             'pdepths':[20.,40.,60.],
                             'tdepths':[0.,2.5, 5., 7.5, 10., 15., 20., 25., 30., 35., 40., 50., 60.],
                             'P1_ind':6,
                             'ED1_ind':9,
                             'T1_ind':23,
                             'bp_ind':36,
                             'vbatt_ind':37,
                             'sub_ind':38},

    
#  --------------------------2018 buoys-------------------------------------

   '300234064735100':{'notes':'used to be UpTempO 2017 #6... was returned',
                          'name':['2018','2'],
		                  'brand':'Pacific Gyre',
                          'imeiabbv':'5100',
                          'vessel':'SIZRS',
                          'pdepths':[20.,40.,60.],
                          'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.],
                          'T1_ind':9,
                          'P1_ind':6,
                          'bp_ind':22,
                          'vbatt_ind':23,
                          'sub_ind':24},

   '300234066712490':{'notes':'WARM 2018 JW-1 ICEX',
                          'name':['2018','JW-1'],
		                  'brand':'Pacific Gyre',
                          'imeiabbv':'2490',
                          'deploymentDate':'3/22/2018',
                          'deploymentLon':-148.8227,
                          'deploymentLat':72.3030,
                          'vessel':'ICEX',
                          'CTDpdepths':[20.,60.],
                          'tdepths':[0.0,7.5,15,25],
                          'CTDtdepths':[5,10,20,30,45,60],
                          'CTDsdepths':[5,10,20,30,45,60],
                          'T1_ind':9,  # Suzanne doesn't know what these 'ind' keys do
                          'P1_ind':6,
                          'vbatt_ind':23},

#  --------------------------2017 buoys-------------------------------------   

   '300234064734090':{'notes':'2017 W-5',
                          'name':['2017','W-5'],
		                  'brand':'Pacific Gyre',
                          'imeiabbv':'4090',
                          'deploymentDate':'03/11/2017',
                          'deploymentLon':-148.0399,
                          'deploymentLat':71.9774,        
                          'vessel':'WARM',
                          'pdepths':[20],
                          'tdepths':[ 0, 2.5, 5, 7.5, 10.6, 12.5, 16, 20],
                          'sdepths':[2.5,10.6,20.0],
                          'T1_ind':9,  # SD does not know what the *_ind keys are for.
                          'P1_ind':6,
                          'bp_ind':22,
                          'vbatt_ind':23,
                          'sub_ind':24},

   '300234064739080':{'notes':'2017 W-6',
                         'name':['2017','W-6'],
	                     'brand':'Pacific Gyre',
                         'imeiabbv':'9080',
                         'deploymentDate':'03/09/2017',
                         'deploymentLon':-147.2774,   
                         'deploymentLat':72.7602,        
                         'vessel':'WARM',
                         'pdepths':[21.7, 49.5],
                         'tdepths':[0, 2.5, 5.5, 7.5, 10.6, 12.5, 16, 21.7, 25, 30, 40, 49.5],
                         'sdepths':[2.5,10.6,21.7,49.5],
                         'T1_ind':9,  # SD does not know what the *_ind keys are for.
                         'P1_ind':6,
                         'bp_ind':22,
                         'vbatt_ind':23,
                         'sub_ind':24},

   '300234065419120':{'notes':'2017 05',
                         'name':['2017','5'],
	               'brand':'Pacific Gyre',
                         'imeiabbv':'9120',
                         'deploymentDate':'09/30/2017',
                         'deploymentLon':-133.7371,
                         'deploymentLat':70.3321,
                         'vessel':'Laurier',
                         'pdepths':[20, 40, 60],
                         'tdepths':[0, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 50, 60],
                         'T1_ind':9,  # SD does not know what the *_ind keys are for.
                         'P1_ind':6,
                         'bp_ind':22,
                         'vbatt_ind':23,
                         'sub_ind':24},

   '300234064737080':{'notes':'2017 04',
                          'name':['2017','4'],
		                  'brand':'Pacific Gyre',
                          'imeiabbv':'7080',
                          'deploymentDate':'09/10/2017',
                          'deploymentLon':-161.094036,
                          'deploymentLat':70.979519,
                          'vessel':'Healy',
                          'pdepths':[25.],
                          'tdepths':[0, 2.5, 5, 7.5, 10, 15, 20, 25],
                          'T1_ind':9,  # SD does not know what the *_ind keys are for.
                          'P1_ind':6,
                          'bp_ind':22,
                          'vbatt_ind':23,
                          'sub_ind':24},

#  --------------------------2016 buoys-------------------------------------   

    '300234063991680':{'notes':'Amundsen 2016 07',
                           'name':['2016','7'],
			               'brand':'Pacific Gyre',
                           'imeiabbv':'1680',
                           'wmo':'4801612',             # get this from L1 or L2.dat
                           'vessel':'Healy',
                           'deploymentDate':'9/5/2016',
                           'deploymentLon':-144.9120, # get this from pacificgyre website, or L1
                           'deploymentLat':74.6038,
                           'pdepths':[20,40,60],
                           'tdepths':[0, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 50, 60],
                           'P1_ind':6,  # Suzanne doesn't use the *_ind keys
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

    '300234063993850':{'notes':'Amundsen 2016 06',
                           'name':['2016','6'],
			               'brand':'Pacific Gyre',
                           'imeiabbv':'3850',
                           'wmo':'4801613',             # get this from L1 or L2.dat
                           'pgname':'UW-TC-37IM-0015',  # get this from api.pacificgyre.com
                           'vessel':'Amundsen',
                           'deploymentDate':'9/1/2016',
                           'deploymentLon':-139.02, # get this from L1 or L2.dat
                           'deploymentLat':70.44, # get this from L1 or L2.dat
                           'pdepths':[25.],
                           'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.],
                           'P1_ind':6,
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

    '300234063861170':{'notes':'Amundsen 2016 05',
                           'name':['2016','5'],
			               'brand':'Pacific Gyre',
                           'imeiabbv':'1170',
                           'wmo':'4801614',             # get this from L1 or L2.dat
                           'pgname':'UW-TC-37IM-0011',  # get this from api.pacificgyre.com
                           'vessel':'Amundsen',
                           'deploymentDate':'8/31/2016',
                           'deploymentLon':-135.517942, # get this from L1 or L2.dat
                           'deploymentLat':71.00741, # get this from L1 or L2.dat
                           'pdepths':[20,40,60],
                           'tdepths':[0, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 50, 60],
                           'P1_ind':6,
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

    '300234062491420':{'notes':'Ukpik 2016 04',
                           'name':['2016','4'],
			               'brand':'Pacific Gyre',
                           'imeiabbv':'1420',
                           'wmo':'4801617',             # get this from L1 or L2.dat
                           'vessel':'Ukpik',
                           'deploymentDate':'8/23/2016', # get this from pacificgyre website, or L1
                           'deploymentLon':-141.2005,    # get this from pacificgyre website, or L1
                           'deploymentLat':70.4040,      # get this from pacificgyre website, or L1
                           'pdepths':[25],
                           'tdepths':[0, 2.5, 5, 7.5, 10, 15, 20, 25],
                           'P1_ind':6,  # Suzanne doesn't use the *_ind keys
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

    '300234063994900':{'notes':'Araon 2016 03',
                           'name':['2016','3'],
			               'brand':'Pacific Gyre',
                           'imeiabbv':'4900',
                           'wmo':'4801613',
                           'pgname':'UW-TC-1W-0005',
                           'vessel':'Araon',
                           'deploymentDate':'8/20/2016',
                           'deploymentLon':-161.00,
                           'deploymentLat':76.00,
                           'pdepths':[25.],
                           'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.],
                           'P1_ind':6,
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

#  --------------------------2014 buoys-------------------------------------   
    '300234060236150':{'notes':'Mirai 2014 13',
                           'name':['2014','13'],
			               'brand':'Marlin-Yug',
                           'imeiabbv':'6150',
                           'wmo':'48678',
                           'pgname':'',
                           'vessel':'Mirai',
                           'deploymentDate':'9/06/2014',
                           'deploymentLon':-162.9634,
                           'deploymentLat':74.3794,
                           'pdepths':[20, 40, 60],
                           'tdepths':[0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30, 35, 40, 45, 50, 55, 60],
                           'P1_ind':6,
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},

    '300234060340370':{'notes':'Amundsen 2014 11',
                           'name':['2014','11'],
			               'brand':'MetOcean',
                           'imeiabbv':'0370',
                           'wmo':'48673',
                           'pgname':'',
                           'vessel':'Amundsen',
                           'deploymentDate':'8/30/2014',
                           'deploymentLon':-128.5544 ,
                           'deploymentLat':73.2933,
                           'pdepths':[15, 30],
                           'tdepths':[0, 2.5, 5.0, 7.5, 10., 15., 20., 25., 30.],
                           'P1_ind':6,
                           'T1_ind':9,
                           'bp_ind':22,
                           'vbatt_ind':23,
                           'sub_ind':24},






##     '300234064735100':{'notes':'JWARM 2018 #1',
#                            'name':['2018','JW-1'],
# 			               'brand':'Pacific Gyre',
#                            'imeiabbv':'2490',
#                            'vessel':'ICEX',
#                            'pdepths':[20.,40.,60.],
#                            'tdepths':[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.],
#                            'T1_ind':9,
#                            'P1_ind':6,
#                            'bp_ind':22,
#                            'vbatt_ind':23,
#                            'sub_ind':24},

          }

    binf=bids[bid]
    if 'listening' not in binf: binf['listening']='1'


    return binf
