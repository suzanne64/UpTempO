#!/usr/bin/python
import sys
import numpy as np
from math import pi
import os
import matplotlib.pyplot as plt 

#LLtoXY
##;  Polar stereo projection of lat,lon onto an x,y grid in kilometers
##;  (From Fortran subroutine rmaps.f)
##;
##;  NSIDC SSMI grids rotated 45 deg in Arctic and 0 in Antarctic
##;  Roger C's basin rotated 60 deg
##;
##;  Here we assume northern hemisphere!
##;  This version (Harry's edit of Erika's wave version) allows
##;  vector arguments for lat and lon, with vectors x,y returned.

#translated from IDL to python by Wendy Ermold

def LLtoXY(alat,alon,rot):
    #alat = a list of latitudes
    #alon = a list of longitudes
    #rot = the map rotations

    x=np.zeros(len(alat))
    y=np.zeros(len(alat))
    t0=np.zeros(len(alat))
    rho=np.zeros(len(alat))
    NP=np.zeros(len(alat))
    XP=np.zeros(len(alat))

    re=6378.273                                #radius of the earth (km) -Hughes Ellipsoid
    e2=np.double(0.006693883)      # eccentricity of the earth
    e=np.float64(np.sqrt(e2))
    slat=70.0

    alat=np.array(alat)
    alon=np.array(alon)
    RDEG = 57.2958
    DRAD = np.double(0.0174533)

    t0[alat < 89.995] = np.tan((pi/4.) - (alat[alat < 89.995]/(2.* RDEG))) \
                        /((1.0 - e*np.sin(DRAD*alat[alat < 89.995]))/(1.+e*np.sin(DRAD*alat[alat < 89.995])))**(e/2)

    t1=np.tan((pi/4.)-(slat/(2.*RDEG)))/             \
        ((1.-e*np.sin(DRAD*slat))/                     \
        (1.+e*np.sin(DRAD*slat)))**(e/2)

    cm=np.cos(DRAD*slat)/np.sqrt(1.-e2*(np.sin(DRAD*slat)**2.))
    rho[alat < 89.995] =(re*cm*t0[alat < 89.995])/t1

    x[alat < 89.995] =  rho[alat < 89.995]*np.sin(DRAD*(alon[alat < 89.995]+rot))
    y[alat < 89.995] = -rho[alat < 89.995]*np.cos(DRAD*(alon[alat < 89.995]+rot))


    
    return x,y

#------------------------
def dist_ll(lat1,lon1,lat2,lon2):

    #Note that lat1,lon1, lat2, lon2 must be lists or arrays,
    #even if they are single valued.

    lat1=np.asarray(lat1)
    lon1=np.asarray(lon1)
    lat2=np.asarray(lat2)
    lon2=np.asarray(lon2)
    
    nlat1=len(lat1)
    nlat2=len(lat2)


    if (nlat1 == 1) and (nlat2 > 1):
        slat1=lat1
        slon1=lon1
        lat1=lat2
        lat2=slat1
        
        lon2=lon1
        lon1=slon1

        nlat1=len(lat1)
        nlat2=len(lat2)

    zlat2=np.zeros(nlat1)
    zlon2=np.zeros(nlat1)
    zlat2[:]=lat2
    zlon2[:]=lon2
    lat2=zlat2
    lon2=zlon2

    rlat1=np.float64(lat1 * (pi/180.0))
    rlon1=np.float64(lon1 * (pi/180.0))
    rlat2=np.float64(lat2 * (pi/180.0))
    rlon2=np.float64(lon2 * (pi/180.0))

    x1=np.float64( np.cos(rlat1) * np.cos(rlon1))
    y1=np.float64( np.cos(rlat1) * np.sin(rlon1))
    z1=np.float64(np.sin(rlat1))
    x2=np.float64( np.cos(rlat2) * np.cos(rlon2))
    y2=np.float64( np.cos(rlat2) * np.sin(rlon2))
    z2=np.float64( np.sin(rlat2))

    midlat=np.float64( (rlat1+rlat2)/2.0 )
    radius=np.float64(6378.139 * (1 - ((np.sin(midlat))**2.0)/298.256))

    T=np.float64(x1*x2+y1*y2+z1*z2)
    
    try:
        b=np.where(T < -1.0)[0]
        if len(b) > 0: T[b]=-1.0
    except:
        if T < -1.0: T=-1.0

    d=np.float64(radius*np.arccos(T))

    try:
        w=np.where(np.isnan(d))[0]
        if len(w) > 0: d[w]=0
    except:
        if np.isnan(d): d=0

    return d

#===============================#
def where(npar,bounds,op1='>',op2='<'):
    #npar is an array of values
    #bounds = [a,b]
    #RETURN index of values in npar where a < npar < b

    if op1 == '>': w=np.where(npar > bounds[0])[0]
    else: w=np.where(npar >= bounds[0])[0]

    if op2 == '<': w2=np.where(npar < bounds[1])[0]
    else: w2=np.where(npar <= bounds[1])[0]

    i=np.intersect1d(w,w2)

    return i

#===============================#
def mycopy(fromar):

    toar=np.empty_like(fromar)
    np.copyto(toar,fromar)

    return toar
    
#===============================#
def smooth(quan,box,missing):

    out=[]
    n=len(quan)
    for i in range(n):
        if i-box < 0: out.append(quan[i])
        else:
            #print i+box
            if i+box+1 > n:
                out.append(quan[i])
            else:

                #print quan[i-box:i+box+1]
                cvals=quan[i-box:i+box+1]
                cvals=[c for c in cvals if c != missing]
                if len(cvals) > 0:
                    m=np.mean(cvals)
                    out.append(m)
                else: out.append(-999.0)

    return out
#=================================#
def median(quan,box,missing):

    out=[]
    n=len(quan)
    for i in range(n):
        if i-box < 0: out.append(quan[i])
        else:
            #print i+box
            if i+box+1 > n:
                out.append(quan[i])
            else:

                #print quan[i-box:i+box+1]
                cvals=quan[i-box:i+box+1]
                cvals=[c for c in cvals if c != missing]
                if len(cvals) > 0:
                    m=np.median(cvals)
                    out.append(m)
                else:
                    out.append(-999.0)

    return out
#==================================#
def PatchInterp(idoys,quan,quandoys,missing=-999.0):

    quan=np.asarray(quan)
    quandoys=np.asarray(quandoys)
    wmissing=np.where(quan == missing)[0]
    wgood=np.where(quan != missing)[0]

    iquan=np.interp(idoys,quandoys[wgood],quan[wgood])

##    fig=plt.figure()
##    plt.plot(quandoys,quan,marker='x')
##    #plt.plot(quandoys[wgood],quan[wgood],marker='o')
##    plt.plot(idoys,iquan,marker='o')
##    #plt.show()

    missingdoys=quandoys[wmissing]
    stobounds=[]
    bound=[0,0]
    boundstarted=0
    for r in range(len(wmissing)-1):

        if not boundstarted:
            if wmissing[r+1] == wmissing[r]+1:
                bound[0]=missingdoys[r]
                boundstarted=1
            else:
                boundstarted=0
        else:
            if wmissing[r+1] == wmissing[r]+1: bound[1]=missingdoys[r]
            else:
                boundstarted=0
                if bound[1] != 0: stobounds.append(bound)
                bound=[0,0]


    for s in stobounds:
        #print s
        ws=where(idoys,bounds=s)
        iquan[ws]=-999.0

    return iquan
                
                
#=================
def calcVelocity(cumdoy,lat,lon):


    deldists=[]
    for r in range(len(lat)-1):
        cdist=dist_ll([lat[r+1]],[lon[r+1]],[lat[r]],[lon[r]])
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

    return velocity

#======================

    
    
    
    
        
    
