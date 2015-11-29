from ligo.gracedb.rest import GraceDb 

from datetime import datetime

import numpy

import os

import pickle, json

from optparse import OptionParser

from sys import argv

g = GraceDb()

now = datetime.now()

parser = OptionParser()

parser.add_option("-d", help = "The arguments should be in this order: lower bound gps time, upper bound gps time, upper bound FAR threshold, the string gstlal, the string mbtaonline, your ligo username, your ligo password")
parser.add_option("-e", help = "An example list of arguments would be: 1127451353.80912 1127529738.14937 1.0e-4 gstlal mbtaonline user.name password")
(options, args) = parser.parse_args()
all_events = [ l for l in g.events(' %s .. %s far < %s'%tuple(argv[1:4])) if (l['pipeline'].lower() in argv[4:]) ]
#chooses events from GraceDb that are under a certain FAR threshold, in between two GPS times, and certain pipelines

results = []

def open_url_wget(url,un=None,pw=None,args=[]):
	import subprocess
        import urlparse
        if un is not None and pw is not None:
                args+=["--user",un,"--password",pw,"--no-check-certificate"]
        retcode=subprocess.call(['wget']+[url]+args)
        return retcode

string = "%10s | %20s | %20s | %45s | %15s | %40s | %20s | %40s"%("graceid", "far", "lalstart", "lalfinish", "snr", "lalsnr", "mchirp", "lalmchirp")
#creates a header string to organize the array

for e in all_events:
#loops through all events satisfying our conditions and collects important data and compiles it into an array

    graceid = e['graceid']
    far = e['far']
    mchirp = e['extra_attributes']['CoincInspiral']['mchirp']
    snr = e['extra_attributes']['CoincInspiral']['snr']
    logs = g.logs(graceid).json()['log']
    lalstart = "Not Started"
    lalfinish = "Not finished as of %s/%s/%s %s:%s:%s" % (now.month, now.day, now.year, now.hour, now.minute, now.second)
    lalmchirp = "None"
    lalsnr = "None"
    for log in logs:
#checks to see if lalinference started and/or ended

	comment = log['comment']
	if "LALInference online parameter estimation started." in comment:
		lalstart = log['created'] 

	if "LALInference online parameter estimation finished." in comment:
		lalfinish = log['created']
		http = comment.find("http")
		html = comment.find(">resu")
		pp_url = comment[http:html]
		url = pp_url.replace("posplots.html","summary_statistics.dat")
		un = argv[6]
		pw = argv[7]
		open_url_wget(url, un, pw, args=[]) 
		return_array = open("summary_statistics.dat", "r")
		for  line in return_array:
                        if "optimal_snr" in line:
                                lalsnr = line.split()[4] + " +- " + line.split()[3]
                        if "mc" in line:
                                lalmchirp = line.split()[4] + " +- " + line.split()[3]
		return_array.close()
		os.remove("summary_statistics.dat")
    string += "\n%10s | %20s | %20s | %45s | %15s | %40s | %20s | %40s"%(graceid, far, lalstart, lalfinish, snr, lalsnr, mchirp, lalmchirp)
#Puts all data together and adds it to the previous data

print string

'''
filename = "mydata.pkl"
print "writing : %s"%filename
file_obj = open(filename, "w")
pickle.dump( all_events, file_obj )
file_obj.close()
'''
