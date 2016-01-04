#!/usr/bin/env python

import pprint
import orcid
import time
from requests import RequestException

def recurse(d, keys=()):
    if type(d) == dict:
         for k in d:
            for rv in recurse(d[k], keys + (k, )):
                yield rv
    else:
        yield (keys, d)


def search_persons(ringgoldid, place):
    api = orcid.PublicAPI()
    persons = {}
    counter = 1
    row = 20
    total_records = api.search_public('%s %s' % (ringgoldid, place))['orcid-search-results']['num-found']
    print ('The total number of entries matching', ringgoldid, 'and', place, 'is', total_records)
    total_records = 200

    # define log entries
    tmpl = '%s\t%s\t%s\n'

    for step in range(0, total_records, row):
        try:
            university = api.search_public('%s %s' % (ringgoldid, place), start=str(step), rows=row)
            for result in university.get('orcid-search-results').get('orcid-search-result'):
                orcid_id = result.get('orcid-profile').get('orcid-identifier').get('path')
              #  request_log.write(tmpl % (datetime.isoformat(datetime.now()), counter, orcid_id))
                
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
                                    persons.setdefault(orcid_id, {}).setdefault((fname + ' ' + lname), []).append(employment.get('department-name'))
                                request_log.write(tmpl % (datetime.isoformat(datetime.now()), counter, orcid_id))

                    except AttributeError:
                        pass
                except RequestException as e:
                    print (e.response.text)
                #print ('Processing record %d' % counter)
                counter += 1
            # pprint.pprint(persons)
        except RequestException as e:
            print (e.response.text)
        #time.sleep(3)
    return persons

# Start program run here
# define log file
import os
from datetime import datetime
if not os.path.exists('output'):
	os.makedirs('output')
    
# log 
request_log = open('output/orcid.log', 'w')
request_log.write('Timestamp\t\t\tstep\tORCID\n')


# Call function for search 
   
people = search_persons ('6187', 'University of Oklahoma')

print ('Total number of employess at OU with ORCID: ', len(people))
pprint.pprint(people)

# Output to csv file
import csv

with open ('output/ou_orcid.csv', 'w', newline='') as fileout:
    peoplewriter = csv.writer(fileout, delimiter=',')
    for ids, val in recurse(people):
            peoplewriter.writerow([ j for j in ids] +  [k for k in val])
fileout.close()