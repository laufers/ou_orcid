#!/usr/bin/env python

import pprint
import orcid
import time
from requests import RequestException

def search_persons(ringgoldid, place):
    api = orcid.PublicAPI()
    persons = {}
    counter = 1
    row = 20
    total_records = api.search_public("6187 University of Oklahoma")['orcid-search-results']['num-found']
    total_records = 1000
    
    for step in range(0, total_records, row):
        try:
            university = api.search_public('%s %s' % (ringgoldid, place), start=str(step), rows=row)
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
                                    persons.setdefault(orcid_id, {}).setdefault((fname + ' ' + lname), []).append(employment.get('department-name'))
                    except AttributeError:
                        pass
                except RequestException as e:
                    print (e.response.text)
                print ('Processing record %d' % counter)
                counter += 1
            # pprint.pprint(persons)
        except RequestException as e:
            print (e.response.text)
        #time.sleep(3)
    return persons

    
people = search_persons ('6187', 'University of Oklahoma')

print ('Total number of employess at OU with ORCID: ', len(people))
pprint.pprint(people)