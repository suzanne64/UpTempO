FUNCTION BuoyMaster,buoy=buoy,summary=summary,noprint=noprint
if not keyword_set(noprint) then noprint=0
if keyword_set(summary) then begin;
	print,'Buoy List: 8650, 2020, 6420, 2080'

return, 0
endif


;This function returns the following information about the selected buoy:
;notes = notes about the buoy
;data   = the master data file
;tdepths = the nominal depths of the temperature sensors 
;T1_ind  = the index of the first temperature measurement
;pdepths = the nominal depths of the pressure sensors
;P1_ind = the index of the first pressure measurement
;vbatt_ind = the index of battery voltage
;bp_ind = the index of the barometric pressure
;days    = the dates translated into days
;prepath='/Users/WendyE/Sept6thUpTempO/'
prepath='/Users/WendyE/Dropbox/'
northsouth=0
tcordepths=-99.
pcordata=-99.
vesselCAP='none'
                        tcordepths=-99. ;readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-0600-CorrectedDepths.dat')
			pdepths=-99
                        pcal=0  ;unknown
			sdepths=-1
			biodepths=-1
			biosensors='none'
			
			s1_ind=-1
                        
			T1_ind=-99
			P1_ind=-99
			D1_ind=-1
			bp_ind=-1
			at_ind=-1
			salt_inds=-1
			tsalt_ind=-1
			psalt_ind=-1
			vbatt_ind=-1
			wind_ind=-1
			
			ll=-99
			days=-99
			momarks=-99
                        ll=-99	
			moddepth=-99
			meandepth=-99
			stddepth=-99
            vessel=-99
            db20goodtill=-99  ;absolute day 
			tbias=0 ;unknown

			Tair_ind=-1
			submergedata=-1
			subind=-1
                        reportdepths=0
			reportsalt=0
			reportsalttemp=0
			reportwind=0
			reportAT=0
			reportTilt=0
			multiCTD=0
			CTDdepths=-1
			cpdepths=-1
			ctdepths=-1
			csdepths=-1
			tiltdepths=-1
			CTDS1_ind=-1
			CTDT1_ind=-1
			CTDP1_ind=-1
			tilt1_ind=-1
			
			lidepths=-1

			
			listening=1

    			fwind=findfile(prepath+'UpTempO/DataAnalysis/WindData/Wind-'+buoy+'.dat')
			fOWshortFlux=findfile(prepath+'UpTempO/DataAnalysis/WindData/OWshortFlux-'+buoy+'.dat')
			fICEshortFlux=findfile(prepath+'UpTempO/DataAnalysis/WindData/ICEshortFlux-'+buoy+'.dat')
			fICEfrac=findfile(prepath+'UpTempO/DataAnalysis/WindData/ICEfrac-'+buoy+'.dat')

			if fwind(0) ne '' then wind=readit(prepath+'UpTempO/DataAnalysis/WindData/Wind-'+buoy+'.dat') else wind=-99.
			if fOWshortFlux(0) ne '' then OWshortFlux=readit(prepath+'UpTempO/DataAnalysis/WindData/OWshortFlux-'+buoy+'.dat') else OWshortFlux=-99.
			if fICEshortFlux(0) ne '' then ICEshortFlux=readit(prepath+'UpTempO/DataAnalysis/WindData/ICEshortFlux-'+buoy+'.dat') else ICEshortFlux=-99.
			if fICEfrac(0) ne '' then ICEfrac=readit(prepath+'UpTempO/DataAnalysis/WindData/ICEfrac-'+buoy+'.dat') else ICEfrac=-99.


			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			if ff(0) ne '' then data=readit(ff(0),noprint=noprint) else data=-99.
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif

case buoy of
;-------------ADDED 2020-------------------
	'9910': BEGIN
				;JAMSTEC JAM-WB-0003
				notes='UpTempO 2020 JW-1'
				name=['2020','JW-2']
				imei='300234067939910'
				vessel='WARM'
				brand='Pacific Gyre'

				multiCTD=1
				reportsalt=1
			
				pdepths=-1 ;no pressure pods
				tdepths=[3.0,12.0]
				cpdepths=[10.0]
				csdepths=[10.0]
				ctdepths=[10.0]
			
				CTDT1_ind=11
				CTDS1_ind=10
				CTDP1_ind=9
				T1_ind=6
				P1_ind=-1
				bp_ind=-1
				vbatt_ind=8
			END
			
			
;-------------ADDED 2019-------------------
	'320940': BEGIN
			;NOT YET DEPLOYED (EDT early Sep) --> NABOS cruise cancelled
			;SET for deployment during MOSAiC 2019
			notes='UpTempO 2019 #5'
			name=['2019','5']
			brand='Marlin-Yug'
			imei='300234060320940'
			vessel='MOSAiC'
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 15., 20., 25., 30., 35., 40., 50., 60.]
			T1_ind=23
			P1_ind=6
			D1_ind=9
			bp_ind=36
			vbatt_ind=37
			reportdepths=1.0
			submergedata=1
			subind=38

		END
			

		
		    
	'320930': BEGIN
			;NOT YET DEPLOYED (ETD = mid aug) --> NABOS cruise cancelled
			notes='UpTempO 2019 #4'
			name=['2019','4']
			brand='Marlin-Yug'
			imei='300234060320930'
			vessel='MOSAiC'
			pdepths=[25]
			tdepths=[0.,2.5,5.0,7.5,10.,15.,20.,25.]
			P1_ind=14
			T1_ind=16
			D1_ind=6
			bp_ind=24
			vbatt_ind=25
			subind=26
			
			

		END
	'6870': BEGIN
				notes='WARM 2019 W9'
				name=['2019','W-9']
				brand='Pacific Gyre'
				imei='300234067936870'
				vessel='WARM'
				
				pdepths=10.
				tdepths=[0.0,4.3,10.]
				
				T1_ind=7
				P1_ind=6
				vbatt_ind=10
				
			;****BIOSENSOR INFO****
			biosensors=['LI_192_0','LI_192_1','LI_192_2','LI_192_3','LI_192_4','LI_192_5','Cyclops_CHL']
			biodepths=[0.0, 0.5, 1.0, 4.1, 6.4, 8.0, 4.7]

			;----for "plot_warm" in webplots---
			lidepths=[0.0, 0.5, 1.0, 4.1, 6.4, 8.0]	    
				
				
				
	        END
	'9480': BEGIN
				;Deployed 9/12/2019 via SIZRS by Mike
				notes='UpTempO 2019 #3'
				name=['2019','3']
				brand='Pacific Gyre'
				imei='300234068719480'
				vessel='SIZRS'
				pdepths=[25.]
				tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
				reportTilt=1
				tiltdepths=[2.5,5.0,7.5,10.,15.,20.,25.]
				
				T1_ind=7
				P1_ind=6
				bp_ind=15
				vbatt_ind=16
				subind=17
				tilt1_ind=24
				
			END
				
	'9450': BEGIN
				;DEPLOYED 8/13/2019 via SIZRS by Jamie Morison
				notes='UpTempO 2019 #2'
				name=['2019','2']
				brand='Pacific Gyre'
				imei='300234068519450'
				vessel='SIZRS'
				pdepths=[20.,40.,60.]
				tdepths=[0.0,2.5,5.,7.5,10.,15.,25.,30.,35.,50.]
				multiCTD=0
				reportTilt=0
				reportsalt=0
				
				T1_ind=9
				P1_ind=6
				bp_ind=22
				vbatt_ind=23
				subind=24
			END
	'4830': BEGIN
				;DEPLOYED via airdrop by Jamie Morison 7/10/2019
				notes='UpTempO 2019 #1'
				name=['2019','1']
				brand='Pacific Gyre'
				imei='300234068514830'
				vessel='SIZRS'
				pdepths=[20.0]
				tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
				multiCTD=0
				reportTilt=0
				reportsalt=0
		
				T1_ind=9
				P1_ind=6
				bp_ind=22
				vbatt_ind=23
				subind=24

					
	          END
				
;-------------ADDED 2018-------------------
	'2490': BEGIN
				;DEPLOYED at ICEX 2018 on 3/22/2018, JAMSTEC WARM UPTEMPO
				notes='JWARM 2018 #1'
				name=['2018','JW-1']
				brand='Pacific Gyre'
				imei='300234066712490'
				data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
				vessel='ICEX'
				
				multiCTD=1
				reportsalt=1
				
				pdepths=-1 ;no pressure pods
				tdepths=[0.0,7.5,15.0,25.0]
				cpdepths=[20.0,60.0]
				csdepths=[5.0,10.0,20.0,30.0,45.0,60.0]
				ctdepths=[5.0,10.0,20.0,30.0,45.0,60.0]
				
				CTDT1_ind=19
				CTDS1_ind=13
				CTDP1_ind=11
				T1_ind=6
				P1_ind=-1
				bp_ind=-1
				vbatt_ind=10
				
			
				lidepths=[0.5]	    
				
				listening=0
			END
				
	'1310': BEGIN
				;Deployed 3/29/2018
				notes='WARM 2017 #7'
				name=['2018','W-7']
				brand='Pacific Gyre'
				imei='300234066711310'	
				data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)

				vessel='WARM'

				multiCTD=1
				reportsalt=1
				CTDdepths=[2.5,10.6,20.5]

				pdepths=-1 ;no pressure pods
				tdepths=[0.0,5.2,7.5,12.5,15.4]
				cpdepths=[20.5]
				csdepths=[2.5,10.6,20.5]
				ctdepths=[2.5,10.6,20.5]
			
				CTDT1_ind=20
				CTDS1_ind=16	
				CTDP1_ind=14
				T1_ind=6
				P1_ind=-1
			
				bp_ind=-1
				vbatt_ind=13
			
				listening=0
			;****BIOSENSOR INFO****
			biosensors=['LI_192_0','LI_192_1','LI_192_2', $
					'LI_192_3; MS9_1 410,440,490,510,550,636,660,685,710nm,&tilt','ECO 460CDOM, 532nm, & 695Chl', $
			            'LI_192_4','LI_192_5','L1_192_6','Cyclops_CHL']
			biodepths=[0.0,0.51,1.0,5.0,5.6,10.0,15.0,19.4,19.9]
				
			;----for "plot_warm" in webplots---
			lidepths=[0,0.5,1,5,10,15,19.4]	    
			END
	'3470': BEGIN
				;NOT YET DEPLOYED (ETD end of March 2018)
				notes='WARM 2018 #8'
				name=['2018','W-8']
				brand='Pacific Gyre'
				imei='300234066713470'			    
				data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)

				vessel='WARM'

				multiCTD=1
				reportsalt=1
				CTDdepths=[2.51,10.74,21,49.5]
				pdepths=-1 ;no pressure pods
				tdepths=[0.0,5.2,7.5,12.5,15.4,25,30.35,40.0]
				cpdepths=[21.0,49.5]
				csdepths=[2.51,10.74,21.0,49.5]
				ctdepths=[2.51,10.74,21.0,49.5]
				
				CTDT1_ind=21
				CTDS1_ind=17	
				CTDP1_ind=15
				T1_ind=6
				P1_ind=-1
			
				bp_ind=-1
				vbatt_ind=14
			
				listening=0
			;****BIOSENSOR INFO****
			biosensors=['LI_192_0','LI_192_1','LI_192_2', $
					'LI_192_3; MS9_1 410,440,490,510,550,636,660,685,710nm,&tilt','ECO 460CDOM, 532nm, & 695Chl', $
			            'LI_192_4','LI_192_5','L1_192_6','L1_192_7','L1_192_8','Cyclops_CHL']
			biodepths=[0.0,0.5,1.0,5.0,5.7,10.0,15.0,20.0,30.0,48.9,49.0]
				
				
				;----for "plot_warm" in webplots---
				lidepths=[0.0,0.5,1.0,5.0,10.0,15.0,20.0,30.0,48.9]	    
			END
			
	'7090': BEGIN
			;notes='UpTempO 2017 Not Deployed'
			;This one was to be deployed in the Hudson, but the cruise was canceled.
			notes='UpTempO 2018 #1'
			name=['2018','1']
			brand='Pacific Gyre'
			imei='300234064737090'
			vessel='Amundsen'
			pdepths=[25.0]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			CTDdepths=[3.0,9.0,15.5]
			csdepths=CTDdepths
			ctdepths=CTDdepths
			cpdepths=-1
			multiCTD=1
			reportTilt=1
			reportsalt=1
			
			;Year;Month;Day;Hour;Lat;Lon;
			;P1;T1;T2;T3;T4;T5;T6;T7;
			;SLP;BATT;SUB;
			;CTD-S1;CTD-S2;CTD-S3;
			;CTD-T1;CTD-T2;CTD-T3;
			;Tilt1;Tilt2;Tilt3;Tilt4;Tilt5;Tilt6;Tilt7
			T1_ind=7
			P1_ind=6
			CTDS1_ind=18
			CTDT1_ind=21
			CTDP1_ind=-1
			tilt1_ind=24
			bp_ind=15
			vbatt_ind=16
			subind=17
			listening=0

					
	        END

	'5100': BEGIN
			;NOT YET DEPLOYED (ETD early Oct 2017, from Healy... was returned)
			;notes='UpTempO 2017 #6'
			;NOT YET DEPLOYED (ETD August 2018)
			notes='UpTempO 2018 #2'
			name=['2018','2']
			brand='Pacific Gyre'
			imei='300234064735100'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			vessel='SIZRS'
			
			;60m 1W
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0
            END	
;-------------ADDED 2017-------------------
                   		
	'9120': BEGIN
			;Deployed 10/1/2017
			notes='UpTempO 2017 #5'
			name=['2017','5']
			brand='Pacific Gyre'
			imei='300234065419120'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			vessel='Laurier'
			
			;60m 1W
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0
                   END

		
	'7080': BEGIN
			;Deployed 9/10/2017
			;Healy 1704 (aka UW-TC-1W-0007) was deployed this morning by Bob Pickarts team 
			;at around 6:30AM.  It is the 25m buoy.  Precise location of deployment was 
			;70 - 57.63 N, 161 - 5.20 W of the NW coast of Alaska, pretty close to the canyon.  
			;Water depth at the location is 42m.  I just want to say that Leah, Bob’s onboard 
			;engineer was great to work with.  We had been in close touch regarding all updates 
			;to the cruise timing and she confirmed every minute change of deployment location 
			;and bathymetry with me over the days leading up to launch.  CTD cast is being done as I type.

			notes='UpTempO 2017 #4'
			name=['2017','4']
			brand='Pacific Gyre'
			imei='300234064737080'
			vessel='Healy'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
				
			;25m 1W
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24


		    END

	'3390': BEGIN
			;deployed 9/3/2017
			notes='UpTempO 2017 #3'
			name=['2017','3']
			brand='Pacific Gyre'
			imei='300234065713390'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			vessel='Mirai'
			
			;60m 1W
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
 			listening=0
           END			

	'8420': BEGIN
			;deployed 8/20/2017
			notes='UpTempO 2017 #2'
			name=['2017','2']
			brand='Pacific Gyre'
			imei='300234065718420'
			vessel='Sikuliaq'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
				
			;25m 1W
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0


		    END	
	
	'9310': BEGIN
			;DEPLOYED 7/10/2017
			notes='UpTempO 2017 #1'
			name=['2017','1']
			brand='Pacific Gyre'
			imei='300234064709310'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			vessel='SIZRS'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0
                   END			
	'9080': BEGIN
			notes='WARM 2017 #6'
			name=['2017','W-6']
			brand='Pacific Gyre'
			imei='300234064739080'	
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)

			vessel='WARM'

			multiCTD=1
			reportsalt=1
			CTDdepths=[2.5,10.6,21.7,49.5]

			pdepths=-1 ;no pressure pods
			tdepths=[0.0,5.5,7.5,12.5,16.,25.,30.,40.]
			cpdepths=[21.7,49.5]
			csdepths=CTDdepths
			ctdepths=CTDdepths
			
			CTDT1_ind=21
			CTDS1_ind=17	
			CTDP1_ind=15
			T1_ind=6
			P1_ind=-1
			
			bp_ind=-1
			vbatt_ind=14
			
			listening=0
			;****BIOSENSOR INFO****
			biosensors=['L1_192_0','L1_192_1','L1_192_2','ECO 460CDOM, 532nm, & 695Chl; OCR_1 412, 443, 555nm, & PAR', $
			            'OCR_2 412, 443, 555nm, & PAR','L1_192_3','OCR_3 412, 443, 555nm, & PAR', $
			            'Cyclops_CHL; OCR_3 412, 443, 555nm, & PAR']
			biodepths=[0.0,0.5,1.0,5.0,10.0,15.0,20.0,49.0]
			
	        END
	'4090': BEGIN
			notes='WARM UpTempO 2017 #5'
			name=['2017','W-5']
			brand='Pacific Gyre'
			imei='300234064734090'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)

			pdepths=[20.]
			
			multiCTD=1
			CTDdepths=[2.5,10.6,20.0]
			
			tdepths=[0.0,2.5,5.5,7.5,10.6,12.5,16,20.]
			csdepths=CTDdepths
			ctdepths=CTDdepths
			cpdepths=20.
			
			T1_ind=7
			CTDP1_ind=6
			bp_ind=-1
			vbatt_ind=19
			s1_ind=20
			listening=0

			vessel='WARM'
			
			;****BIOSENSOR INFO****
			biosensors=['L1_192_1','L1_192_2','ECO 460CDOM, 532nm, & 695Chl', $
			            'OCR_2 412, 443, 555nm, & PAR','L1_192_3','OCR_3 412, 443, 555nm, & PAR', $
			            'Cyclops_CHL']
			biodepths=[0.5,1.0,5.0,10.0,15.0,18.4,18.8]
			END

;-------------ADDED 2016-------------------
	'0600': BEGIN
			notes='UpTempO 2016 #9'
			name=['2016','9']
			brand='Pacific Gyre'
			imei='300234063990600'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-0600NEW.dat',noprint=noprint)
			
			vessel='Sikuliaq'
			reportsalt=0
			reportsalttemp=0
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=-1
			tsalt_ind=-1
			psalt_ind=-1
			listening=0
		
		    END

	'1870': BEGIN
			notes='UpTempO 2016 #8'
			name=['2016','8']
			brand='Pacific Gyre'
			imei='300234063991870'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='Amundsen'
			reportsalt=1
			reportsalttemp=1
			;reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			;wind_ind=27
			listening=0

			END
	'1680': BEGIN

			notes='UpTempO 2016 #7'
			name=['2016','7']
			brand='Pacific Gyre'
			imei='300234063991680'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='Healy'
			;reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			;wind_ind=27

			END

	'3850': BEGIN
			notes='UpTempO 2016 #6'
			name=['2016','6']
			brand='Pacific Gyre'
			imei='300234063993850'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3850NEW.dat',noprint=noprint)
			
			vessel='Amundsen'
			reportsalt=0
			reportsalttemp=0
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=-1
			tsalt_ind=-1
			psalt_ind=-1
			listening=0
		
		    END



	'1170': BEGIN
			notes='UpTempO 2016 #5'
			name=['2016','5']
			brand='Pacific Gyre'
			imei='300234063861170'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='Amundsen'
			reportsalt=1
			reportsalttemp=1
			;reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			;wind_ind=27
			listening=0

			END


	'1420': BEGIN
			notes='UpTempO 2016 #4'
			name=['2016','4']
			brand='Pacific Gyre'
			imei='300234062491420'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-1420NEW.dat',noprint=noprint)
			
			vessel='Ukpik'
			reportsalt=0
			reportsalttemp=0
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=-1
			tsalt_ind=-1
			psalt_ind=-1
		
		    END

	'4900': BEGIN
			notes='UpTempO 2016 #3'
			name=['2016','3']
			brand='Pacific Gyre'
			imei='300234063994900'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4900NEW.dat',noprint=noprint)
			
			vessel='Araon'
			reportsalt=0
			reportsalttemp=0
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=-1
			tsalt_ind=-1
			psalt_ind=-1
			listening=0
		
		    END

	'9150': BEGIN
			notes='UpTempO 2016 #1'
			name=['2016','1']
			brand='Pacific Gyre'
			imei='300234063869150'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-9150NEW.dat',noprint=noprint)
			
			vessel='ICEX'
			reportsalt=1
			reportsalttemp=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			listening=0
		
		    END
	'2660': BEGIN
			notes='UpTempO 2016 #2'
			name=['2016','2']
			brand='Pacific Gyre'
			imei='300234063992660'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2660NEW.dat',noprint=noprint)
			
			vessel='Healy'
			reportsalt=1
			reportsalttemp=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			listening=0
		END
;-------------ADDED 2015-------------------
	'8970': BEGIN
			notes='UpTempO 2015 #1'
			name=['2015','1']
			brand='Pacific Gyre'
			imei='300234062958970'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8970NEW.dat',noprint=noprint)
			
			vessel='Healy'
			reportsalt=1
			reportsalttemp=1
			reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			wind_ind=27
			listening=0

			END
	'5460': BEGIN
			notes='UpTempO 2015 #2'
			name=['2015','2']
			brand='Pacific Gyre'
			imei='300234061655460'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='SIZRS'
			reportsalt=1
			reportsalttemp=1
			;reportwind=1
			submergedata=1
			listening=0
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			;wind_ind=27

			END

	'5260': BEGIN
			notes='UpTempO 2015 #3'
			name=['2015','3']
			brand='Pacific Gyre'
			imei='300234062065260'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='SIZRS'
			reportsalt=1
			reportsalttemp=1
			;reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			;wind_ind=27
			listening=0

			END
	'1010': BEGIN
			notes='UpTempO 2015 #4'
			name=['2015','4']
			brand='Pacific Gyre'
			imei='300234062061010'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			
			vessel='SIZRS'
			reportsalt=1
			reportsalttemp=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			listening=0
			
			
	        END
	'6350': BEGIN
			notes='UpTempO 2015 #5'
			name=['2015','5']
			brand='Pacific Gyre'
			imei='300234062656350'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
						
			vessel='SIZRS'
			reportsalt=1
			reportsalttemp=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			listening=0
			
			
	        END
	'0470': BEGIN
			notes='UpTempO 2015 #6'
			name=['2015','6']
			brand='Pacific Gyre'
			imei='300234062490470'
			pdepths=[25.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			vessel='Healy'
			
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0
			

			END
	'2480': BEGIN
			notes='UpTempO 2015 #7'
			name=['2015','7']
			brand='Pacific Gyre'
			imei='300234062492480'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			listening=0

			
			vessel='Healy'
			END
	'5990': BEGIN
			notes='UpTempO 2015 #8'
			name=['2015','8']
			brand='Pacific Gyre'
			imei='300234062955990'
			pdepths=[25]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.]
			
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat',noprint=noprint)
			
			vessel='SIZRS'
			reportsalt=1
			reportsalttemp=1
			reportwind=1
			submergedata=1
			
			P1_ind=6
			T1_ind=9
			bp_ind=22
			vbatt_ind=23	
			subind=24
			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
			wind_ind=27
			listening=0

			END

	'5470': BEGIN
			notes='WARM UpTempO 2014 #2'
			name=['2014','W-2']
			brand='Pacific Gyre'
			imei='300234061655470'
			
			vessel='WARM'
			pdepths=[10.,50.]
			tdepths=[0.0,2.5,5.,7.5,10.,15.,20.,50.]
			T1_ind=8
			P1_ind=6
			bp_ind=-1
			vbatt_ind=16
			listening=0
			
			biosensors=['LI_192_1','LI_192_2','OCR_1 412nm, 443nm, 555nm, & PAR; ECO_460CDOM, 532nm, 695Chl', $
					   'OCR_2 412nm, 443nm, 555nm, & PAR','OCR_3 412nm, 443nm, 555nm, & PAR','LI_192_3']
			biodepths=[0.5,1.0,4.45,9.45,18.6,49.45]

			END
			
	'51960': BEGIN
			notes='WARM UpTempO 2015 #3'
			name=['2015','W-3']
			brand='Pacific Gyre'
			imei='300234062951960'
			pdepths=[10.,20.]
			tdepths=[0.0,2.5,5.,7.5,10.,15.,20.]
			T1_ind=8
			P1_ind=6
			bp_ind=-1
			vbatt_ind=15
			listening=0

			vessel='WARM'
			
			biosensors=['LI_192_1','LI_192_2','OCR_1 412nm, 443nm, 555nm, & PAR; ECO_460CDOM, 532nm, 695Chl', $
					   'OCR_2 412nm, 443nm, 555nm, & PAR','OCR_3 412nm, 443nm, 555nm, & PAR']
			biodepths=[0.5,1.0,4.45,9.45,18.6]

			END
			
	'7970': BEGIN
			notes='WARM UpTempO 2015 #4'
			name=['2015','W-4']
			brand='Pacific Gyre'
			imei='300234062957970'
			pdepths=[10.,50.]
			tdepths=[0.0,2.5,5.,7.5,10.,15.,20.,50.]
			vessel='WARM'
			T1_ind=8
			P1_ind=6
			bp_ind=-1
			vbatt_ind=16
			listening=0
			biosensors=['LI_192_1','LI_192_2','OCR_1 412nm, 443nm, 555nm, & PAR; ECO_460CDOM, 532nm, 695Chl', $
					   'OCR_2 412nm, 443nm, 555nm, & PAR','OCR_3 412nm, 443nm, 555nm, & PAR','LI_192_3']
			biodepths=[0.5,1.0,4.45,9.45,18.6,49.45]

			END
			
	'3450':	BEGIN
			notes='WARM 2014 #1'
			name=['2014','W-1']
			brand='Pacific Gyre'
			imei='300234061653450'	
			pdepths=[10.,20.]
			tdepths=[0.0,2.5,5.,7.5,10.,15.,20.]
			vessel='WARM'
			T1_ind=8
			P1_ind=6
			bp_ind=-1
			vbatt_ind=16
			listening=0

			vessel='WARM'
			
			biosensors=['LI_192_1','LI_192_2','OCR_1 412nm, 443nm, 555nm, & PAR; ECO_460CDOM, 532nm, 695Chl', $
					   'OCR_2 412nm, 443nm, 555nm, & PAR','OCR_3 412nm, 443nm, 555nm, & PAR']
			biodepths=[0.5,1.0,4.45,9.45,18.6]
			END

;-------------------------------------------------------------					
			
	
	'3190': BEGIN
			notes='UpTempO 2014 # 1'
			name=['2014','1']
			brand='Marlin-Yug'
			imei='300234060233190'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3190NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3190NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=26
			P1_ind=6
			bp_ind=43
			vbatt_ind=44
			vessel='APLIS'	
			reportdepths=1.0
			submergedata=1
			subind=45

			iform='MY3'
			
			listening=0
			
		    END
	'5160': BEGIN
			notes='UpTempO 2014 # 2'
			name=['2014','2']
			brand='Marlin-Yug'
			imei='300234060235160'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5160NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5160NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=26
			P1_ind=6
			bp_ind=43
			vbatt_ind=44
			vessel='APLIS'	
			reportdepths=1.0
			submergedata=1
			subind=45

			iform='MY3'
			listening=0
		    END
	'2260': BEGIN
			notes='UpTempO 2014 # 3'
			name=['2014','3']
			brand='Pacific Gyre'
			imei='300234011882260'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2260NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2260NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=8
			P1_ind=6
			bp_ind=21
			vbatt_ind=22
			vessel='SIZRS'	
			reportdepths=0.0
			submergedata=1
			subind=23

			iform='PG'

			listening=0

		    END

	'9650': BEGIN
			notes='UpTempO 2014 # 4'
			name=['2014','4']
			brand='Pacific Gyre'
			imei='300234061639650'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-9650NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-9650NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			vessel='SIZRS'	
			reportdepths=0.0
			submergedata=1
			subind=24

			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
	
			wind_ind=0	
			reportsalt=1
			reportsalttemp=1
			reportwind=0

			iform='PG'
			
			listening=0

		    END
	'8150': BEGIN
			notes='UpTempO 2014 #5'
			name=['2014','5']
			brand='Marlin-Yug'
			imei='300234060238150'
			vessel='Araon'
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8150NEW.dat',noprint=noprint)
			ll=data(4:5,*)
			
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0
			
		END
	'6910': BEGIN
			notes='UpTempO 2014 #6'
			name=['2014','6']
			brand='Pacific Gyre'
			imei='300234061876910'
			vessel='SIZRS'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6910NEW.dat',noprint=noprint)
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			vessel='SIZRS'	
			reportdepths=0.0
			submergedata=1
			subind=24

			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
	
			wind_ind=0	
			reportsalt=1
			reportsalttemp=1
			reportwind=0
			
			listening=0

		END

	'0940': BEGIN
			notes='UpTempO 2014 #7'
			name=['2014','7']
			brand='Pacific Gyre'
			imei='300234061870940'
			vessel='SIZRS'
			pdepths=[20.,40.,60.]
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-0940.dat',noprint=noprint)
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	

			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			vessel='SIZRS'	
			reportdepths=0.0
			submergedata=1
			subind=24

			salt_inds=25
			tsalt_ind=26
			psalt_ind=-1
	
			wind_ind=0	
			reportsalt=1
			reportsalttemp=1
			reportwind=0
			
			listening=0

		END

	'9180': BEGIN
			notes='UpTempO 2014 #8'
			name=['2014','8']
			brand='Marlin-Yug'
			imei='300234060239180'
			vessel='Araon'
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-9180NEW.dat',noprint=noprint)
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0

		END

	'1390': BEGIN
			notes='UpTempO 2014 #9'
			name=['2014','9']
			brand='MetOcean'
			imei='300234060341390'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[15.,30.]
			tdepths=[0.,2.5,5.0,7.5,10.,15.,20.,25.,30.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			vessel='Amundsen'
			
			T1_ind=8
			P1_ind=6
			bp_ind=17
			vbatt_ind=18
			at_ind=19
			Tair_ind=19
			reportAT=1
			listening=0


		END
	'5390': BEGIN
			notes='UpTempO 2014 #10'
			name=['2014','10']
			brand='MetOcean'
			imei='300234060345390'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[15.,30.]
			tdepths=[0.,2.5,5.0,7.5,10.,15.,20.,25.,30.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			vessel='Amundsen'
			T1_ind=8
			P1_ind=6
			bp_ind=17
			vbatt_ind=18
			at_ind=19
			Tair_ind=19
			reportAT=1
			listening=0

		END

	'0370': BEGIN
			notes='UpTempO 2014 #11'
			name=['2014','11']
			brand='MetOcean'
			imei='300234060340370'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[15.,30.]
			tdepths=[0.,2.5,5.0,7.5,10.,15.,20.,25.,30.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			vessel='Amundsen'
			T1_ind=8
			P1_ind=6
			bp_ind=17
			vbatt_ind=18
			at_ind=19
			Tair_ind=19
			reportAT=1
			listening=0

			

		END

	'3150': BEGIN
			notes='UpTempO 2014 #12'
			name=['2014','12']
			brand='Marlin-Yug'
			imei='300234060233150'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Polarstern'	
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0


		END
	'6150': BEGIN
			notes='UpTempO 2014 #13'
			name=['2014','13']
			brand='Marlin-Yug'
			imei='300234060236150'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Mirai'	
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0

		END
	'5320': BEGIN
			notes='UpTempO 2014 #14'
			name=['2014','14']
			brand='Marlin-Yug'
			imei='300234060235320'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Mirai'	
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0

		END

	'7170': BEGIN
			notes='UpTempO 2014 #15'
			name=['2014','15']
			brand='Marlin-Yug'
			imei='300234060237170'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Mirai'	
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0
		   END

	'3160': BEGIN
			notes='UpTempO 2014 #16'
			name=['2014','16']
			brand='Marlin-Yug'
			imei='300234060233160'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-'+buoy+'NEW.dat')
			data=readit(ff(0),noprint=noprint)
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			ll=data(4:5,*)
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Polarstern'	
			reportdepths=1.0
			submergedata=1
			subind=45
			listening=0

		END

	'7800': BEGIN
			notes='UpTempO 2013 # 20'
			name=['2013','20']
			brand='Marlin-Yug'
			imei='300234011247800'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7800NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7800NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Federov'	
			reportdepths=1.0
			submergedata=1
			subind=45
			
			listening=0

			iform='MY3'
		    END


	'6950': BEGIN
			notes='UpTempO 2013 # 19'
			name=['2013','19']
			brand='Marlin-Yug'
			imei='300234011246950'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6950NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6950NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Federov'	
			reportdepths=1.0
			iform='MY3'
			submergedata=1
			subind=45

			listening=0
			
		    END
	'3770': BEGIN
			notes='UpTempO 2013 # 18'
			name=['2013','18']
			brand='Marlin-Yug'
			imei='300234011243770'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3770NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3770NEW.dat',noprint=noprint) else data=-99.
			pdepths=[83.]
			tdepths=[0.0,11.,13.,16.,21.,26.,32.,37.,42.,47.,53.,58.,63.,68.,73.,78.,83.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Healy'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
                        
            listening=0

		    END
	'2990': BEGIN
			notes='UpTempO 2013 # 17'
			name=['2013','17']
			brand='Marlin-Yug'
			imei='300234011242990'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2990NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2990NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Healy'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
			listening=0
			
		    END
	'4780': BEGIN
			notes='UpTempO 2013 # 16'
			name=['2013','16']
			brand='Marlin-Yug'
			imei='300234011244780'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4780NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4780NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Healy'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
			listening=0
			
		    END



	'46740': BEGIN
			notes='UpTempO 2013 # 15'
			name=['2013','15']
			brand='Marlin-Yug'
			imei='300234011246740'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-46740NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-46740NEW.dat',noprint=noprint) else data=-99.
			pdepths=[20.,40.,60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=26
			P1_ind=6
			D1_ind=9
			bp_ind=43
			vbatt_ind=44
			vessel='Federov'	
			reportdepths=1.0
			iform='MY3'
			submergedata=1
			subind=45
			listening=0
		    END


	'5950': BEGIN
			notes='UpTempO 2013 # 14'
			name=['2013','14']
			brand='Marlin-Yug'
			imei='300234011245950'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5950NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5950NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Araon'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
                    
            listening=0
		    END

	'4960': BEGIN
			notes='UpTempO 2013 # 13'
			name=['2013','13']
			brand='Marlin-Yug'
			imei='300234011244960'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4960NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4960NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Healy'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
			listening=0
			
		    END




	'5960': BEGIN
			notes='UpTempO 2013 # 12'
			name=['2013','12']
			brand='Marlin-Yug'
			imei='300234011245960'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5960NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-5960NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Araon'	
			reportdepths=1.0
	        	submergedata=1		
                        subind=43

			iform='MY1'
			listening=0

		    END

	'4950': BEGIN
			notes='UpTempO 2013 # 11'
			name=['2013','11']
			brand='Marlin-Yug'
			imei='300234011244950'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4950NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4950NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Araon'	
			reportdepths=1.0
	        	submergedata=1		
                        subind=43

			iform='MY1'
			listening=0
		    END
	'1960': BEGIN
			notes='UpTempO 2013 # 10'
			name=['2013','10']
			brand='Marlin-Yug'
			imei='300234011241960'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-1960NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-1960NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Louis'	
			reportdepths=1.0
			iform='MY1'
	        	submergedata=1		
                        subind=43
			listening=0
		    END

	'2840': BEGIN
			notes='UpTempO 2013 # 9'
			name=['2013','9']
			brand='Marlin-Yug'
			imei='300234011242840'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2840NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2840NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			vessel='Louis'	
			reportdepths=1.0
	        	submergedata=1		
                        subind=43
			iform='MY1'
			listening=0

		    END
	'1580': BEGIN
			notes='UpTempO 2013 #8'
			name=['2013','8']
			brand='Pacific Gyre'
			imei='300234060451580'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-1580NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-1580NEW.dat',noprint=noprint) else data=-99.
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			pdepths=[20.,40.,60.]
			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			salt_inds=26
			tsalt_ind=27
			psalt_ind=25
	
			wind_ind=28
			vessel='Louis'
			submergedata=1		
                        subind=24
			reportsalt=1
			reportsalttemp=1
			reportwind=1
			iform='pPG'
			
			listening=0
		END
	'2970': BEGIN
			notes='UpTempO 2013 # 7'
			name=['2013','7']
			brand='Marlin-Yug'
			imei='300234011242970'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2970NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2970NEW.dat',noprint=noprint) else data=-99.
			pdepths=[60.]
			tdepths=[0.,2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 25., 30., 35., 40., 45., 50., 55., 60.]

			if data(0) ne -99 then begin
				ll=data(4:5,*)
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
			endif
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42		
	        	submergedata=1		
                        subind=43

			vessel='Louis'	
			reportdepths=1.0
			iform='MY1'
			listening=0

		    END
	'4260': BEGIN
			notes='UpTempO 2013 #6'
			name=['2013','6']
			brand='Pacific Gyre'
			imei='300234011884260'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4260NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-4260NEW.dat',noprint=noprint) else data=-99
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			pdepths=[20.,60.]
			if data(0) ne -99 then begin
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
				ll=data(4:5,*)
			endif
			T1_ind=8
			P1_ind=6
			bp_ind=21
			vbatt_ind=22
			salt_inds=-99
			;wind_ind=27
			vessel='SIZRS'
			submergedata=1		
                        subind=23
			reportsalt=0
			reportsalttemp=0
			reportwind=0
			iform='sPG'
			listening=0
            
            END

	'6740': BEGIN
			notes='UpTempO 2013 #5'
			name=['2013','5']
			brand='Pacific Gyre'
			imei='300234060456740'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6740NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6740NEW.dat',noprint=noprint) else data=-99
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			pdepths=[20.,40.,60.]
			if data(0) ne -99 then begin
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))	
				ll=data(4:5,*)
			endif
			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			salt_inds=26
			tsalt_ind=27
			psalt_ind=25
	
			wind_ind=28
			vessel='Louis'
			submergedata=1		
                        subind=24
			reportsalt=1
			reportsalttemp=1
			reportwind=1
			iform='pPG'
			listening=0
		END

	'6620': BEGIN
			notes='UpTempO 2013 #4'
			name=['2013','4']
			brand='Pacific Gyre'
			imei='300234060456620'
			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6620NEW.dat')
			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6620NEW.dat',noprint=noprint) else data=-99
			if data(0) ne -99 then begin
				days=DayConverter2(time=data(0:3,*))
				momarks=MarkMonths(data(0:3,*))
				ll=data(4:5,*)
			endif	
			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			pdepths=[20.,40.,60.]
			T1_ind=9
			P1_ind=6
			bp_ind=22
			vbatt_ind=23
			salt_inds=26
			tsalt_ind=27
			psalt_ind=25
	
			
			wind_ind=28
			vessel='Ukpik'
			submergedata=1		
                        subind=24
			reportsalt=1
			reportsalttemp=1
			reportwind=1
			iform='pPG'
			
			listening=0
			
        	END


;	'2260': BEGIN
;  I'm not sure how this got here... 2260 is a 2014 buoy ????
;			notes='UpTempO 2012 #8'
;			name=['2012','8']
;			brand='Pacific Gyre'
;			imei='300234011882260'
;			ff=findfile(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2260NEW.dat')
;			if ff(0) ne '' then data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2260NEW.dat',noprint=noprint) else data=-99.
;			tdepths=[0.0,2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
;			pdepths=[20.,60.]
;			if data(0) ne -99 then begin
;				ll=data(4:5,*)
;				days=DayConverter2(time=data(0:3,*))
;				momarks=MarkMonths(data(0:3,*))	
;			endif
;			T1_ind=8
;			P1_ind=6
;			bp_ind=21
;			vbatt_ind=22
;			salt_inds=25
;			wind_ind=27
;			vessel='SIZRS'
;			submergedata=1		
;                       subind=23
;		reportsalt=0
;			reportsalttemp=0
;			reportwind=0
;			iform='sPG'
;			
;			listening=0
;            END
			
        'WG1': BEGIN
			notes='Wave Glider #1'
			name=['2011','1']
			data=readit(prepath+'UpTempO/WaveGlider/WG1-7-31to9-23-2011.dat')
			
			data(0,*)=2011.0
                        pcordata=-99.
			tdepths=[0.5,1.0,1.5,3.0,4.5,6.0]
			pdepths=-99
			tcordepths=-99
			pcal=0
			imei='0'
			T1_ind=8
			P1_ind=-1
			bp_ind=-1
			vbatt_ind=-1
			ptime=data(1:5,*)
			ctime=fltarr(4,n_elements(ptime(0,*)))
			ctime(0,*)=2011.0
			ctime(1:2,*)=ptime(0:1,*)
			ctime(3,*)=ptime(3,*)+ptime(4,*)/60.
			days=DayConverter2(time=ctime)
			momarks=MarkMonths(ctime)
			ll=data(6:7,*)
			moddepth=0
			meandepth=0
			stddepth=0
			db20goodtill=0
			tbias=0
                       vessel='WaveGlider1'

		    END
	'WG2': BEGIN
			notes='Wave Glider #2'
			name=['2011','2']
			data=readit(prepath+'UpTempO/WaveGlider/WG2-7-31to9-23-2011.dat')
			data(0,*)=2011.0
                        pcordata=-99.
			tdepths=[0.5,1.0,1.5,3.0,4.5,6.0]
			pdepths=-99
			tcordepths=-99
			pcal=0
			imei='0'
			T1_ind=8
			P1_ind=-1
			bp_ind=-1
			vbatt_ind=-1
			ptime=data(1:5,*)
			ctime=fltarr(4,n_elements(ptime(0,*)))
			ctime(0,*)=2011.0
			ctime(1:2,*)=ptime(0:1,*)
			ctime(3,*)=ptime(3,*)+ptime(4,*)/60.
			days=DayConverter2(time=ctime)
			momarks=MarkMonths(ctime)
			ll=data(6:7,*)
			moddepth=0
			meandepth=0
			stddepth=0
			db20goodtill=0
			tbias=0
                        vessel='WaveGlider2'

		    END
	'0110': BEGIN
			notes='UpTempO 2013 #1'
			name=['2013','1']
			brand='Marlin-Yug'
			imei='300234011340110'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-0110NEW.dat',noprint=noprint)
			tdepths=[0.0,11.,13.,16.,21.,26.,32.,37.,42.,47.,53.,58.,63.,68.,73.,78.,83.]
			pdepths=83.
			ll=data(4:5,*)
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			vessel='Palmer'
			northsouth=1
			momarks=MarkMonths(data(0:3,*))	
			submergedata=1		
                        subind=43
			reportdepths=1
			
			listening=0
		
		   END
	'2110': BEGIN
			notes='UpTempO 2013 #2'
			name=['2013','2']
			brand='Marlin-Yug'
			imei='300234011342110'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2110.dat',noprint=noprint)
			tdepths=[0.0,11.,13.,16.,21.,26.,32.,37.,42.,47.,53.,58.,63.,68.,73.,78.,83.]
			pdepths=83.
			ll=data(4:5,*)
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			vessel='Palmer'
			northsouth=1
			submergedata=1		
			momarks=MarkMonths(data(0:3,*))			
                        subind=43
			reportdepths=1
			
			listening=0
		   END
	'3110': BEGIN
			notes='UpTempO 2013 #3'
			name=['2013','3']
			brand='Marlin-Yug'
			imei='300234011343110'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3110NEW.dat',noprint=noprint)
			tdepths=[0.0,11.,13.,16.,21.,26.,32.,37.,42.,47.,53.,58.,63.,68.,73.,78.,83.]
			pdepths=83.
			ll=data(4:5,*)
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			vessel='Palmer'
			northsouth=1
			momarks=MarkMonths(data(0:3,*))			
			submergedata=1		
                        subind=43
			reportdepths=1
			listening=0
		   END


	'40600': BEGIN
			notes='UpTempO 2012 2'
			name=['2012','2']
			;notes='UpTempO 2012 0600'
			;name=['2012','0600']
			brand='Marlin-Yug'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-40600.dat',noprint=noprint)
			tdepths=[0.0,11.0,13.0,15.0,20.,25.,30.,35.,40.,45.,50.,55.,60.,65.,70.,75.,80.]
                        tcordepths=-99. ;readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-0600-CorrectedDepths.dat')
			pdepths=80.0
                        pcal=0.0
                        imei='300234011240600'
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='Louis'
                        db20goodtill=50.  ;absolute day 
			tbias=0
			submergedata=1		
                        subind=43
			reportdepths=1
                        
              listening=0          
		   END
	'2190': BEGIN
			notes='UpTempO 2012 #3'
			name=['2012','3']
			;notes='UpTempO 2012 #1'
			;name=['2012','1']
			brand='MetOcean'
			source='JouBeh'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2190.dat',noprint=noprint)
                        pcordata=-99. 
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=-99. 
			pdepths=[20.0,60.0]
                        pcal=0  ;unknown
                        imei='300234011162190'
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='Louis'
                        db20goodtill=50.  ;absolute day 
			tbias=0 ;unknown

			Tair_ind=22
            listening=0          
                        
		   END
	'8710': BEGIN
			notes='UpTempO 2012 #4'
			name=['2012','4']
			;notes='UpTempO 2012 #2'
			;name=['2012','2']
			brand='MetOcean'
			source='JouBeh'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8710.dat',noprint=noprint)
                        pcordata=-99. 
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=-99. 
			pdepths=[20.0,60.0]
                        pcal=0  ;unknown
                        imei='300234011468710'
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='Louis'
                        db20goodtill=50.  ;absolute day 
			tbias=0 ;unknown
                        
			Tair_ind=22
            listening=0          
		   END

	'0990': BEGIN
			notes='UpTempO 2012 #5 Louis'
			name=['2012','5']
			;notes='UpTempO 2012 #3 Louis'
			;name=['2012','3']
			brand='Marlin-Yug'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-0990.dat',noprint=noprint)
                        pcordata=-99. 
			tdepths=[0.0,3.5,5.,7.5,10.,12.5,15.,17.5,20.,22.5,27.5,32.5,37.5,42.5,47.5,52.5,57.5]
                        tcordepths=-99. 
			pdepths=[60.0]
                        pcal=0  ;unknown
                        imei='300234011240990'
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='Louis'
                        db20goodtill=-99.  ;absolute day 
			tbias=0 ;unknown
			Tair_ind=-1
			submergedata=1		
                        subind=43
			reportdepths=1
			listening=0
		   END

	'6990': BEGIN
			notes='UpTempO 2012 #6 PolarStern'
			name=['2012','6']
			;notes='UpTempO 2012 #4 PolarStern'
			;name=['2012','4']
			brand='Marlin-Yug'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6990.dat',noprint=noprint)
                        pcordata=-99. 
			tdepths=[0.0,11.0,13.0,15.0,20.,25.,30.,35.,40.,45.,50.,55.,60.,65.,70.,75.,80.]
                        tcordepths=-99. ;readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-6990-CorrectedDepths.dat')
			pdepths=[80.0]
                        pcal=0  ;unknown
                        imei='300234011246990'
			T1_ind=24
			P1_ind=6
			D1_ind=7
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='PolarStern'
                        db20goodtill=-99.  ;absolute day 
			tbias=0 ;unknown
			submergedata=1		
                        subind=43
			reportdepths=1
			listening=0
		   END

	'7980': BEGIN
			notes='UpTempO 2012 #8 PolarStern'
			name=['2012','8']
			;notes='UpTempO 2012 #5 PolarStern'
			;name=['2012','5']
			brand='Marlin-Yug'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7980.dat',noprint=noprint)
                        pcordata=-99. ;readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-7980-PressureCorrected.dat')
			tdepths=[0.0,3.5,5.,7.5,10.,12.5,15.,17.5,20.,22.5,27.5,32.5,37.5,42.5,47.5,52.5,57.5]
                        tcordepths=-99. ;readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-7980-CorrectedDepths.dat')
			pdepths=[60.0]
                        pcal=0  ;unknown
                        imei='300234011247980'
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='PolarStern'
                        db20goodtill=-99.  ;absolute day 
			tbias=0 ;unknown
			submergedata=1		
                        subind=43
			reportdepths=1
			tbias=0 ;unknown
			
			listening=0
			
		   END

	'3950': BEGIN
			notes='UpTempO 2012 #7 Healy'
			name=['2012','7']
			;notes='UpTempO 2012 #6 Healy'
			;name=['2012','6']
			brand='Marlin-Yug'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3950.dat',noprint=noprint)
                        pcordata=-99.
			tdepths=[0.0,11.0,13.0,15.0,20.,25.,30.,35.,40.,45.,50.,55.,60.,65.,70.,75.,80.]
                        tcordepths=-99. 
			pdepths=[80.0]
                        pcal=0  ;unknown
                        imei='300234011243950'
			T1_ind=24
			P1_ind=6
			bp_ind=41
			vbatt_ind=42
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
                        vessel='Healy'
                        db20goodtill=-99.  ;absolute day 
			tbias=0 ;unknown
			Tair_ind=-1
			submergedata=1		
                        subind=43
			reportdepths=1
			
			listening=0
			
		   END




	'2080': BEGIN
			notes='UpTempO 2011 #1 APLIS'
			name=['2011','1']
			brand='MetOcean'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2080.dat',noprint=noprint)
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-2080-PressureCorrected.dat')
			tdepths=[2.5,5.0,7.5,10.0,15.0,20.0,25.0]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-2080-CorrectedDepths.dat')
			pdepths=25.0
                        pcal=998.4
                        imei='300234010732080'
			T1_ind=7
			P1_ind=6
			bp_ind=14
			vbatt_ind=15
			days=DayConverter2(time=data(0:3,*))
			momarks=MarkMonths(data(0:3,*))	
                        ll=data(4:5,*)	
			moddepth=28.11
			meandepth=27.98
			stddepth=.26
                        vessel='APLIS'
                        db20goodtill=50.  ;absolute day 
			tbias=0.20
            listening=0         
                        
		   END
	'6420': BEGIN
			notes='UpTempO 2010 #2 Araon'
			name=['2010','2']
			
			;notes='UpTempO 2010 #6 Araon'
			;name=['2010','6']
			

			brand='MetOcean'
                        imei='300034012586420'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6420.dat',noprint=noprint)
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-6420-PressureCorrected.dat')
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-6420-CorrectedDepths.dat')
			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
                         pcal=mean(data(20,*))
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=[23.15,63.95]
			meandepth=[23.06,63.71]
			stddepth=	[.4,.65]
                        vessel='Araon'
                        db20goodtill=30.  ;absolute day 
                        db60goodtill=30.  ;absolute day 
 			tbias=0.0
 			
 			listening=0
		   END
	'6420good': BEGIN
			notes='UpTempO 2010 #2 Araon'
			name=['2010','2']
			
			;notes='UpTempO 2010 #6 Araon'
			;name=['2010','6']
			
                        imei='300034012586420'
			data=readit('BUOY6420-summary/Buoy6420-good.dat',noprint=noprint)
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)		
			moddepth=[23.15,63.95]
			meandepth=[23.06,63.71]
			stddepth=	[.4,.65]
                        vessel='Araon'
 			tbias=-99.0
 			listening=0
		   END
	'8650': BEGIN
			notes='UpTempO 2010 #3 Amundsen'
			name=['2010','3']
			
			;notes='UpTempO 2010 #2 Amundsen'
			;name=['2010','2']
			brand='MetOcean'
			imei='300034013618650'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8650.dat',noprint=noprint)
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-8650-PressureCorrected.dat',noprint=noprint)

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
            tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-8650-CorrectedDepths.dat',noprint=noprint)

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
            pcal=mean(data(20,*))

			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)		
			moddepth=[23.19,65.57]
			meandepth=[22.92,65.03]
			stddepth=[.92,1.72]
                        vessel='Amundsen'
                        db20goodtill=60.  ;absolute day 
                        db60goodtill=45.  ;absolute day 
 			tbias=-99.0
			listening=0
		   END
	'2020': BEGIN
			notes='UpTempO 2010 #1 Araon'
			name=['2010','1']
			
			;notes='UpTempO 2010 #5 Araon'
			;name=['2010','5'] ;old
			
			brand='MetOcean'
                        imei='300034012772020'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-2020.dat',noprint=noprint)
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-2020-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-2020-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
                         pcal=mean(data(20,*))

			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)		
			moddepth=[23.26,66.03]
			meandepth=[22.99,65.59]
			stddepth=[.74,1.32]
                        vessel='Araon'
                        db20goodtill=300.  ;absolute day 
                        db60goodtill=300.  ;absolute day 
 			tbias=-99.0
			listening=0
		   END
	'6630': BEGIN
			notes='UPTEMPO 2011 #5 Araon'
			name=['2011','5']
			
			;notes='UPTEMPO 2011 #9 Araon'
			;name=['2011','9']
			brand='MetOcean'
			imei='300234010956630'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6630.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-6630-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-6630-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
                        pcal=1005.42
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			idealpran=[[18.,22.],[55.,65.]]
			moddepth=-99
			meandepth=-99
			stddepth=	-99
                        vessel='Araon'
                        vesselCAP='ARAON'
 			tbias=0.97
 			listening=0
		   END
	'96870': BEGIN
			notes='UPTEMPO 2011 #4 Louis'
			name=['2011','4']
			brand='MetOcean'
			imei='300034012196870'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-6870.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-6870-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-6870-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
                        pcal=1004.84
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
			vessel='Louis'
			vesselCAP='LOUIE'
 			tbias=0.73
 			listening=0
		   END
	'7630': BEGIN
			notes='UPTEMPO 2011 #6 Araon'
			name=['2011','6']
			
			;notes='UPTEMPO 2011 #8 Araon'
			;name=['2011','8']
			brand='MetOcean'
			imei='300234010957630'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7630.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-7630-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-7630-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
                        pcal=1005.42
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Araon'
			vesselCAP='ARAON'
 			tbias=0.79
 			listening=0
		   END
	'7960': BEGIN
			notes='UPTEMPO 2011 #3 Louis'
			name=['2011','3']
			;notes='UPTEMPO 2011 #5 Louis'
			;name=['2011','5']
			brand='MetOcean'
			imei='300034013707960'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7960.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-7960-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-7960-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1004.84
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Louis'
			vesselCAP='LOUIE'
 			tbias=-99.0
 			listening=0
		   END
	'8880': BEGIN
			notes='UPTEMPO 2011 #2 Healy'
			name=['2011','2']
			
			;notes='UPTEMPO 2011 #3 Healy'
			;name=['2011','3']
			brand='MetOcean'
			imei='300034012488880'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8880.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-8880-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-8880-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1023.19
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Healy'
			vesselCAP='HEALY'
 			tbias=0.28
 			listening=0
		   END
	'0530': BEGIN
			notes='UPTEMPO 2011 #7 Healy'
			name=['2011','7']
			
			;notes='UPTEMPO 2011 #2 Healy'
			;name=['2011','2']
			brand='MetOcean'
			imei='300034013610530'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-0530.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-0530-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-0530-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1018.23
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=-99
			vessel='Healy'
			vesselCAP='HEALY'
 			tbias=0.34
 			listening=0
		   END
	'3640': BEGIN
			notes='UPTEMPO 2011 #9 Amundsen'
			name=['2011','9']
			;notes='UPTEMPO 2011 #7 Amundsen'
			;name=['2011','7']
			brand='MetOcean'
			imei='300234010953640'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3640.dat')
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-3640-PressureCorrected.dat')

			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-3640-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1012.07
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Amundsen'
			vesselCAP='AMUNDSEN'
 			tbias=0.71
 			listening=0
		   END
	'7610': BEGIN
			notes='UPTEMPO 2011 #8 Amundsen'
			name=['2011','8']
			
			;notes='UPTEMPO 2011 #6 Amundsen'
			;name=['2011','6']
            brand='MetOcean'
			imei='300234010957610'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-7610.dat')
			pcordata=data
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=-99.

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1012.07
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Amundsen'
			vesselCAP='AMUNDSEN'
 			tbias=-99.0
 			listening=0
		   END
	'3910': BEGIN
			notes='UPTEMPO 2011 #10 Laurier'
			name=['2011','10']
			brand='MetOcean'
			imei='300234010853910'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-3910.dat')
			;pcordata=data
                        pcordata=readit(prepath+'UpTempO/NEWBUOYDATA/PressureCorrected/UpTempO-3910-PressureCorrected.dat')
			tdepths=[2.5,5.0,7.5,10.,15.,20.,25.,30.,35.,40.,50.,60.]
                        tcordepths=readit(prepath+'UpTempO/NEWBUOYDATA/TempDepths/UpTempO-3910-CorrectedDepths.dat')

			days=DayConverter2(time=data(0:3,*))
			pdepths=[20.0,60.0]
			pcal=1001.14
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Laurier'
			vesselCAP='LAURIER'
 			tbias=0.44
 			listening=0
		   END

	'8240': BEGIN
			notes='Antartica Palmer 1'
			name=['2012','1']
			;notes='Antartica Palmer 3'
			;name=['2012','3']
			brand='MetOcean'
			imei='300234011918240'
			data=readit(prepath+'UpTempO/NEWBUOYDATA/UpTempO-8240.dat')
			ll=data(4:5,*)

			;pcordata=data
                        pcordata=-99
			tdepths=[5.,10.,15.,25.,35.,50.,75.,100.,125.,150.,175.,200.]
                        tcordepths=-99

			days=DayConverter2(time=data(0:3,*))
			pdepths=[75.0,200.0]
			pcal=1000. ;UNKNOWN at this time
			T1_ind=8
			P1_ind=6
			bp_ind=20
			vbatt_ind=21
			momarks=MarkMonths(data(0:3,*))			
                        ll=data(4:5,*)	
			moddepth=-99
			meandepth=-99
			stddepth=	-99
			vessel='Palmer'
 			tbias=0.0 ;UNKNOWN
 			listening=0
		   END

	else: return, {notes:'UNREGISTERED',name:['NA','NA'],tdepths:-1,status:-1}
endcase

if s1_ind ne -1 then reportsalt=1

minday=round(min(days))
maxday=round(max(days))

for cd=minday,maxday do begin
	wd=where(days eq cd)
	if n_elements(wd) eq 2 then begin
		days(wd(0))=days(wd(0))-1.0
	endif
end
momarks=MarkMonths(data(0:3,*))			
ll=data(4:5,*)	

help,days
print,notes
print,'-----------'


RETURN, {notes:notes, name:name, data:data, tdepths:tdepths, ctdepths:ctdepths, biodepths:biodepths, $
		biosensors:biosensors, T1_ind:T1_ind, D1_ind:D1_ind, $ 
		 reportdepths:reportdepths, reportwind:reportwind, salt_inds:salt_inds, $
         vbatt_ind:vbatt_ind, bp_ind:bp_ind, tbias:tbias, northsouth:northsouth, subind:subind, $
        reportsalt:reportsalt, reportsalttemp:reportsalttemp, days:days, pdepths:pdepths, cpdepths:cpdepths, $
        ll:ll, wind:wind, OWshortFlux:OWshortFlux, ICEshortFlux:ICEshortFlux, ICEfrac:ICEfrac, $
        wind_ind:wind_ind,P1_ind:P1_ind,momarks:momarks,moddepth:moddepth,meandepth:meandepth, $
        submergedata:submergedata, brand:brand, tsalt_ind:tsalt_ind, psalt_ind:psalt_ind, csdepths:csdepths,$
        stddepth:stddepth,vessel:vessel,imei:imei,pcal:pcal, pcordata:pcordata,tcordepths:tcordepths, $
        Tair_ind:Tair_ind,reportAT:reportAT,at_ind:at_ind,vesselCAP:vesselCAP,listening:listening, $
        s1_ind:s1_ind,sdepths:sdepths,reportTilt:reportTilt,multiCTD:multiCTD,CTDdepths:CTDdepths,tiltdepths:tiltdepths, $
        CTDS1_ind:CTDS1_ind,CTDT1_ind:CTDT1_ind,CTDP1_ind:CTDP1_ind,tilt1_ind:tilt1_ind,lidepths:lidepths,status:1}

END