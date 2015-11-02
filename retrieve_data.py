'''
arg1 = Lower bound of gpstime
arg2 = Upper bound of gpstime
arg3 = far threshold
arg4 = specific pipeline that you are interested in
arg5 = specific pipeline that you are interested in
'''

from ligo.gracedb.rest import GraceDb 
#imports database

from datetime import datetime

import pickle, json

from sys import argv
#imports arguments

g = GraceDb()

now = datetime.now()

all_events = [ l for l in g.events(' %s .. %s far < %s'%tuple(argv[1:4])) if (l['pipeline'].lower() in argv[4:]) ]
#chooses events from GraceDb that are under a certain FAR threshold, in between two GPS times, and certain pipelines

results = []

string = "%10s | %20s | %15s | %15s | %20s | %45s"%("graceid", "far", "snr", "mchirp", "lalstart", "lalfinish")
#creates a header string to organize the array

for e in all_events:
#loops through all events satisfying our conditions and collects important data and compiles it into an array

    graceid = e['graceid']
    far = e['far']
    mchirp = e['extra_attributes']['CoincInspiral']['mchirp']
    snr = e['extra_attributes']['CoincInspiral']['mchirp']
    logs = g.logs(graceid).json()['log']
    lalstart = "Not Started"
    lalfinish = "Not finished as of %s/%s/%s %s:%s:%s" % (now.month, now.day, now.year, now.hour, now.minute, now.second)
    for log in logs:
#checks to see if lalinference started and/or ended
	comment = log['comment']
	if "LALInference online parameter estimation started." in comment:
		lalstart = log['created'] 

	if "LALInference online parameter estimation finished." in comment:
		lalfinish = log['created']

    string += "\n%10s | %20s | %15s | %15s | %20s | %45s"%(graceid, far, snr, mchirp, lalstart, lalfinish)
#Puts all data together and adds it to the previous data

print string
'''
filename = "mydata.pkl"
print "writing : %s"%filename
file_obj = open(filename, "w")
pickle.dump( all_events, file_obj )
file_obj.close()
'''
