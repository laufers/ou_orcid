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
stepcount = 20
ringgoldid = '6187'   
place = 'University of Oklahoma'

total_records = api.search_public('%s %s' % (ringgoldid, place))['orcid-search-results']['num-found']
total_records = 100
print('The total number of entries matching %s and %s is %s.\n' % (ringgoldid, place, total_records))


# define log file
import os
from datetime import datetime
if not os.path.exists('output'):
    os.makedirs('output')
    
# log 
request_log = open('output/orcid.log', 'w')
request_log.write('Timestamp\t\t\tstep\tORCID\n')
# define log entries template
tmpl = '%s\t%s\t%s\n'
    
#  Progress bar setup
pbar = ProgressBar(widgets=['Working: ', Percentage(), Bar()], max_value=total_records + stepcount).start()
# pbar = ProgressBar(widgets=['Working: ', Percentage(), Bar()]).start()
# pbar = ProgressBar(widgets=['Working: ', Percentage(), Bar()]).start()

for step in range(0, total_records, stepcount):
    try:
        university = api.search_public('%s %s' % (ringgoldid, place), start=str(step), rows=stepcount)
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
                    request_log.write(tmpl % (datetime.isoformat(datetime.now()), counter, orcid_id))

                except AttributeError:
                    pass
            except Exception as e:
                # print (e)
                request_log.write(tmpl % (datetime.isoformat(datetime.now()), orcid_id, e))
            #print ('Processing record %d' % counter)
            counter += 1
            # print(counter)
            pbar += 1
        # pbar += stepcount
        # pprint.pprint(people)
    except Exception as e:
        request_log.write(tmpl % (datetime.isoformat(datetime.now()), orcid_id, e))
    # pbar.update(step)
    #time.sleep(3)

pbar.finish()

request_log.write('The total number of entries matching %s and %s is %s.\n' % (ringgoldid, place, total_records))
request_log.write('Total number of employess at OU with ORCID: %s\n' % len(people))

# Output to csv file
import csv

with open ('output/ou_orcid.csv', 'w', newline='') as fileout:
    peoplewriter = csv.writer(fileout, delimiter=',')
    for ids, val in recurse(people):
            peoplewriter.writerow([ j for j in ids] +  [k for k in val])
fileout.close()
request_log.close()