#!/usr/bin/python2.7
import ftplib
from ftplib import FTP
import cgi
import cgitb
import urllib
import os
cgitb.enable()
import sys


transrecs='UPTEMPO/transferRecord.dat'

file1=open(transrecs,'rb')

datarecs='UPTEMPO/DataFilesToTransfer.dat'
data=open(datarecs,'rb')


ftp=FTP('psctestsite.org')
ftp.login('psctestsite.org','Ice+Melt3go')
ftp.cwd('UpTempO')


for f in file1:
    tup=f.partition(' ')
    tofile=tup[2].rstrip()
    fromfile=tup[0]
    try:
        ftp.storbinary('STOR '+tofile,open(fromfile,'rb'))
        print 'TRANSFER SUCCESSFUL: '+tofile+'<br>'
    except ftplib.all_errors:
        print 'This data file did not go: '+tofile+'<br>'
        

print '<br><b>Transfering Data Files...</b><br>'
for d in data:
    tup=d.partition(' ')
    tofile=tup[2].rstrip()
    fromfile=tup[0]
    try:
        ftp.storbinary('STOR '+tofile,open(fromfile,'rb'))
        print 'DATA TRANSFER SUCCESSFUL: '+tofile+'<br>'
    except ftplib.all_errors:
        print 'This data file did not go: '+tofile+'<br>'


print '<br><br>'

print '<br><br>'
print '<a href="http://psc.apl.washington.edu/UpTempO/UpTempO.php">Go to live UpTempO site</a>'
print '    </body>'
print '</html>'


ftp.quit()
file1.close()
data.close()


