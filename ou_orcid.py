import pprint
import orcid
from requests import RequestException

def search_persons(ringgoldid, place):
    api = orcid.PublicAPI()
    try:
        uni = api.search_public('%s %s' % (ringgoldid, place), rows=2000)
        persons = {}
        counter = 1
        person_counter = 0
        for result in uni.get('orcid-search-results').get('orcid-search-result'):
            theid = result.get('orcid-profile').get('orcid-identifier').get('path')
            try:
                summary = api.read_record_public(theid, 'activities')
                try:
                    for employment in summary.get('employments').get('employment-summary'):
                        if employment.get('organization').get('disambiguated-organization').get(
                                'disambiguated-organization-identifier') == ringgoldid:
                            if not employment.get('end-date'):
                                persons.setdefault(employment.get('department-name'), []).append(theid)
                                person_counter += 1
                except AttributeError:
                    pass
            except RequestException as e:
                print (e.response.text)
            print ('Processing record %d' % counter)
            counter += 1
        print (person_counter)
        pprint.pprint(persons)
    except RequestException as e:
        print (e.response.text)

# search_persons('9142', 'Bochum')
# search_persons('14311', 'Dortmund')
search_persons ('6187', 'University of Oklahoma')