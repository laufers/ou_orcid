#!/usr/bin/env python

import pprint
import orcid
import time
from requests import RequestException
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AbsoluteETA, AdaptiveTransferSpeed



# recurse function allows for recursivly printing out m
def recurse(d, keys=()):
    if type(d) == dict:
         for k in d:
            for rv in recurse(d[k], keys + (k, )):
                yield rv
    else:
        yield (keys, d)


#  Set or calculate program varaiables here

api = orcid.PublicAPI()
people = {}
counter = 0
stepcount = 25
ringgoldid = '6187'   
place = 'University of Oklahoma'

# search = ringgoldid + ' ' + place
# search = place 
search = ringgoldid

total_records = api.search_public('%s' % (search))['orcid-search-results']['num-found']
# total_records = api.search_public('%s %s' % (ringgoldid, place))['orcid-search-results']['num-found']
# total_records = 8000
print('The total number of entries matching %s is %s.\n' % (search, total_records))


# define log file
import os
from datetime import datetime
if not os.path.exists('output'):
    os.makedirs('output')

#  File output names 
logfile = datetime.now().strftime('%Y%m%d%H%M_orcid.log')
csvfile = datetime.now().strftime('%Y%m%d%H%M_orcid.csv')


    
# log 
request_log = open(('output/' + logfile), 'w')
request_log.write('Timestamp\t\t\tstep\tORCID\n')
# define log entries template
tmpl = '%s\t%s\t%s\n'

# raise SystemExit 
    
#  Progress bar setup
widgets = ['Working: ', AnimatedMarker(markers='←↖↑↗→↘↓↙')]
pbar = ProgressBar(widgets=widgets, max_value=total_records + stepcount).start()
# pbar = ProgressBar(widgets=['Working: ', Percentage(), Bar()]).start()
# pbar = ProgressBar(widgets=['Working: ', Percentage(), Bar()]).start()

for step in range(0, total_records, stepcount):
    try:
        # print (step)
        university = api.search_public('%s' % (search), start=str(step), rows=stepcount)
        # university = api.search_public('%s' % (search), start=str(step), rows=stepcount)
        for result in university.get('orcid-search-results').get('orcid-search-result'):
            orcid_id = result.get('orcid-profile').get('orcid-identifier').get('path')
            
            try:
                fname = result.get('orcid-profile').get('orcid-bio').get('personal-details').get('given-names').get('value')
            except:
                fname = ''
            try:
                lname = result.get('orcid-profile').get('orcid-bio').get('personal-details').get('family-name').get('value')
            except:
                lname = ''
            
            try:
                summary = api.read_record_public(orcid_id, 'activities')
                try:
                    for employment in summary.get('employments').get('employment-summary'):
                        if employment.get('organization').get('disambiguated-organization').get('disambiguated-organization-identifier') == ringgoldid:
                            if not employment.get('end-date'):
                                people.setdefault(orcid_id, {}).setdefault((fname + ' ' + lname), []).append(employment.get('department-name'))
                            # request_log.write(tmpl % (datetime.isoformat(datetime.now()), counter, orcid_id))
                    # request_log.write(tmpl % (datetime.isoformat(datetime.now()), counter, orcid_id))

                except AttributeError:
                    pass
            except Exception as e:
                # print (e)
                request_log.write(tmpl % (datetime.isoformat(datetime.now()), orcid_id, e))
            #print ('Processing record %d' % counter)
            counter += 1
            # print(counter)
            pbar += 1
        # pprint.pprint(people)
    except Exception as e:
        request_log.write(tmpl % (datetime.isoformat(datetime.now()), orcid_id, e))
    #time.sleep(3)

pbar.finish()

request_log.write('The total number of entries matching %s and %s is %s.\n' % (ringgoldid, place, total_records))
request_log.write('Total number of employess at OU with ORCID: %s\n' % len(people))

# Output to csv file
import csv

with open (('output/' + csvfile), 'w', newline='') as fileout:
    peoplewriter = csv.writer(fileout, delimiter=',')
    for ids, val in recurse(people):
            peoplewriter.writerow([ j for j in ids] +  [k for k in val])
fileout.close()
request_log.close()
print ('Done\n\n')