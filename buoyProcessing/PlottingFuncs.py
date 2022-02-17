import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import BuoyTools_py3_toot as BT




def PolyList(nors='N'):
    if nors == 'S':
        polypath='/Volumes/GoogleDrive/My Drive/UpTempO/PolyPlot2/landbitsS/'
        polyfiles=BT.FileList(polypath)
        
    else:
        polypath='/Volumes/GoogleDrive/My Drive/UpTempO/PolyPlot2/'
        polyfiles=os.listdir(polypath)

    return [polyfiles,polypath]

def splitPolys(poly):
    #poly is a list of string xy values: 'x y'


    polys={}
    pcount=0
    for row in poly:
        srow=row.split(' ')
        srow=[r for r in srow if r]
        x=float(srow[0])
        y=float(srow[1])
        if (x == -99.) and (y == -99.0):
            pcount+=1
            polys[pcount]=[]
        else:
            polys[pcount].append([x,y])

    return polys
            
        


def ArcticMap(rot=0,domain=[-2500.,2500.,-2500.,2500.],fsize=(10,10)):


    fig=plt.figure(figsize=fsize)
    plt.xlim(domain[0],domain[1])
    plt.ylim(domain[2],domain[3])
    
    pfiles,ppath=PolyList()
    filemarkers=['Land','Wate']
    for p in pfiles:
        if p[0:4] in filemarkers:
            opf=open(ppath+p,'r')
            xy=opf.read()
            opf.close()
            xy=xy.split('\n')[0:-2]
            polys=splitPolys(xy)

            if 'Land' in p: ucol='dimgrey'
            if 'Water' in p:
                ucol='b'
            for p in polys:
                cpoly=np.asarray(polys[p])

                if rot:
                    la,lo=XYtoLL(cpoly[:,0],cpoly[:,1],0.0)
                    x,y=LLtoXY(la,lo,rot)
                    plt.fill(x,y,ucol)
                else:
                
                    plt.fill(cpoly[:,0],cpoly[:,1],ucol)
                
                
    return plt        
 

def ArcticMapOP(plt,rot=0.0,pcol='k'):


    
    pfiles,ppath=PolyList()
    filemarkers=['Land','Wate']
    for p in pfiles:
        if p[0:4] in filemarkers:
            opf=open(ppath+p,'r')
            xy=opf.read()
            opf.close()
            xy=xy.split('\n')[0:-2]
            polys=splitPolys(xy)

            if 'Land' in p: ucol=pcol
            if 'Water' in p:
                ucol='b'
            for p in polys:
                cpoly=np.asarray(polys[p])

                if rot:
                    la,lo=gf.XYtoLL(cpoly[:,0],cpoly[:,1],0.0)
                    x,y=gf.LLtoXY(la,lo,rot)
                    plt.fill(x,y,ucol)
                else:
                
                    plt.fill(cpoly[:,0],cpoly[:,1],ucol)
                
    return plt               

def AntMap(rot=0,domain=[-5000.,5000.,-5000.,5000.],fsize=(10,10)):
    
    fig=plt.figure(figsize=fsize)
    plt.xlim(domain[0],domain[1])
    plt.ylim(domain[2],domain[3])

    pfiles,ppath=PolyList(nors='S')
    for pp in pfiles:
##        opf=open(ppath+pp,'r')
##        xy=opf.read()
##        opf.close()
##        xy=xy.split('\n')

        cpoly=np.loadtxt(ppath+pp)

        ucol='dimgrey'
        #for p in polys:
        #cpoly=np.asarray(polys[p])

        if rot:
            la,lo=XYtoLL(cpoly[:,0],cpoly[:,1],0.0)
            x,y=LLtoXY(la,lo,rot)
            plt.fill(x,y,ucol)
        else:
        
            plt.fill(cpoly[:,0],cpoly[:,1],ucol)
                
                
    return plt                

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

    alat=np.asarray(alat)
    alon=np.asarray(alon)
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
#-------------------------
def XYtoLL(xx,yy,rot):
    #xx and yy are lists or arrays
    #rot is the rotation, where rot=0 points the meridian straight down

    nel=len(xx)
    alat=np.zeros(nel)
    alon=np.zeros(nel)
    tt=np.zeros(nel)
    chi=np.zeros(nel)

    xx=np.asarray(xx)
    yy=np.asarray(yy)
    re=6378.273 #Radius of earth (km) -Hughes Ellipsoid
    e2=np.double(0.006693883) #eccentricity of the earth
    e=np.float64(np.sqrt(e2))
    slat=70.0
    RDEG=57.2958
    DRAD=np.double(0.0174533)

    rho=np.sqrt(xx*xx + yy*yy)
    cm=np.cos(DRAD*slat)/np.sqrt(1.0-e2*(np.sin(DRAD*slat)**2.))
    t=np.tan( (pi/4.0) -(slat/(2.*RDEG) )) /((1.-e*np.sin(DRAD*slat))/(1.+e*np.sin(DRAD*slat)))**(e/2.0)

    tt=rho*t/(re*cm)
    chi=(pi/2.)-2.*np.arctan(tt)
    
    alat = chi + ((e2/2.)+(5.*(e2**2.)/24.)+((e2**3.)/12.)) * np.sin(2.*chi) + ((7.*(e2**2)/48.)+(29*(e2**3.)/240.)) * np.sin(4.*chi)+ (7.*(e2**3.)/120.) * np.sin(6.*chi)
 
    alat=alat * RDEG
    alon=(np.arctan2(yy,xx)*RDEG+90.) - rot
    neg=alon<=-180.
    alon[neg]=alon[neg]+360.

    return alat,alon

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
    

def laloLines(plt,rot,lats=[30.,40.,50.,60.,70.,80.],lons=[45.,90.,135.,180.,225.,270.,315.,360.]):
    lonar=range(3600)
    lonar=[round((u+1)*.1,1) for u in lonar]

    latar=range(600)
    latar=[round(la*.1,1)+30 for la in latar]

    for la in lats:
        ladat=[la for i in lonar]
        xla,yla=LLtoXY(ladat,lonar,rot)
        plt.plot(xla,yla,'dimgrey',linewidth=1)

    for lo in lons:
        lodat=[lo for i in latar]
        xlo,ylo=LLtoXY(latar,lodat,rot)
        plt.plot(xlo,ylo,'dimgrey',linewidth=1)

    return plt
    
