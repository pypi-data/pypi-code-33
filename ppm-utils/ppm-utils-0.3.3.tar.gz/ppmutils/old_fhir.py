import requests
from furl import furl
import re
import uuid
import json
import collections
from datetime import datetime
import base64
import random
from dateutil.parser import parse
from dateutil import tz
from urllib.parse import quote

from django.conf import settings
from django.utils.safestring import mark_safe

from fhirclient.client import FHIRClient
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.patient import Patient
from fhirclient.models.period import Period
from fhirclient.models.flag import Flag
from fhirclient.models.bundle import Bundle

from ppmutils.ppm import PPM
from ppmutils.p2md import P2MD
from ppmutils.p2m2 import P2M2

import logging
logger = logging.getLogger(__name__)


class FHIR:

    @staticmethod
    def _query_bundle(resource_type, query=None):
        """
        This method will fetch all resources for a given type, including paged results.
        :param resource: FHIR resource type
        :type resource: str
        :param query: A dict of key value pairs for searching resources
        :type query: dict
        :return: A Bundle of FHIR resources matching query
        :rtype: Bundle
        """
        logger.debug('Query bundle: {}'.format(resource_type))

        # Build the URL.
        url_builder = furl(PPM.fhir_url())
        url_builder.path.add(resource_type)

        # Add query if passed and set a return count to a high number, despite the server
        # probably ignoring it.
        url_builder.query.params.add('_count', 1000)
        if query is not None:
            url_builder.query.params.update(query)

        # Prepare the final URL
        url = url_builder.url

        # Collect them.
        total_bundle = None

        # The url will be set to none on the second iteration if all resources
        # were returned, or it will be set to the next page of resources if more exist.
        while url is not None:

            # Make the request.
            response = requests.get(url)
            response.raise_for_status()

            # Parse the JSON.
            bundle = response.json()
            if total_bundle is None:
                total_bundle = bundle
            elif bundle.get('total', 0) > 0:
                total_bundle['entry'].extend(bundle.get('entry'))

            # Check for a page.
            url = None

            for link in bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']

        return Bundle(total_bundle)

    @staticmethod
    def _query_resources(resource_type, query=None):
        """
        This method will fetch all resources for a given type, including paged results.
        :param resource: FHIR resource type
        :type resource: str
        :param query: A dict of key value pairs for searching resources
        :type query: dict
        :return: A list of FHIR resource dicts
        :rtype: list
        """
        logger.debug('Query resource: {}'.format(resource_type))

        # Get the bundle
        bundle = FHIR._query_bundle(resource_type, query)

        # Get entries
        entries = bundle.as_json().get('entry', []) if bundle else []

        # Return the list
        return entries

    @staticmethod
    def _query_resource(resource_type, _id):
        """
        This method will fetch a resource for a given type.
        :param fhir_url: FHIR server URL
        :type fhir_url: str
        :param resource_type: FHIR resource type
        :type resource_type: str
        :param _id: The ID of the resource
        :type _id: str
        :return: A FHIR resource dict
        :rtype: dict
        """
        logger.debug('Query resource "{}": {}'.format(resource_type, _id))

        # Build the URL.
        url_builder = furl(PPM.fhir_url())
        url_builder.path.add(resource_type)
        url_builder.path.add(_id)

        # Make the request.
        response = requests.get(url_builder.url)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _query_transaction(operations):
        """
        Accepts a list of operations and returns the resulting list of resources. Operations are
        dicts containing a 'url' and a 'method' (e.g. get, post, delete)
        :param operations: A list of operation dicts
        :return: list
        """

        # Build the transaction
        transaction = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': []
        }

        # Add the request
        for request in operations:
            transaction['entry'].append({
                'request': {
                    'url': request['url'],
                    'method': request['method']
                }
            })

        logger.debug(transaction)

        # Make the FHIR request.
        response = requests.post(PPM.fhir_url(), headers={'content-type': 'application/json'},
                                 data=json.dumps(transaction))

        # Get the JSON
        bundle_json = response.json()

        # Check for paged results
        next_urls = []
        for bundle in [entry['resource'] for entry in bundle_json['entry'] if entry['resource']['total'] > 0
                                                                              and len(entry['resource']['link']) > 1]:

            # Get the next URL
            next_url = FHIR._get_next_url(bundle, True)
            if next_url:
                next_urls.append(next_url)

        while len(next_urls) > 0:
            logger.debug('Getting pages: {}'.format(next_urls))

            # Build the transaction
            transaction = {
                'resourceType': 'Bundle',
                'type': 'transaction',
                'entry': []
            }

            # Add the request
            for next_url in next_urls:
                transaction['entry'].append({
                    'request': {
                        'url': next_url,
                        'method': 'GET',
                    }
                })

            # Make the FHIR request.
            response = requests.post(PPM.fhir_url(), headers={'content-type': 'application/json'},
                                     data=json.dumps(transaction))

            # Clear next URLs
            next_urls.clear()

            # Get the JSON
            next_bundle_json = response.json()

            # Process bundles
            for next_bundle in [entry['resource'] for entry in next_bundle_json['entry'] if entry['resource']['total'] > 0]:

                # Determine resource type
                resource_type = next_bundle['entry'][0]['resource']['resourceType']

                # Append entries
                bundle = next((entry['resource'] for entry in bundle_json['entry']
                              if entry['resource']['entry'][0]['resource']['resourceType'] == resource_type), None)
                if not bundle:
                    logger.error('Could not find original bundle for {}'.format(resource_type))
                    continue

                bundle['entry'].extend(next_bundle['entry'])

                # Get the next URL
                next_url = FHIR._get_next_url(next_bundle, True)
                if next_url:
                    next_urls.append(next_url)

        # Patch non-compliant json
        FHIR._fix_bundle_json(bundle_json)

        # Create the bundles
        bundle = Bundle(bundle_json)

        # Check totals
        for resource_bundle in [entry.resource for entry in bundle.entry if entry.resource.total > 0]:
            logger.debug('{}: Found {} out of {}'.format(resource_bundle.entry[0].resource.resource_type,
                                                         len(resource_bundle.entry), resource_bundle.total))
        # Return the list of entries
        resources = [entry.resource for entry in bundle.entry]

        return resources

    @staticmethod
    def format_date(date_string, date_format, utc=True):
        """
        Accepts a date string, parses it, and then formats it according
        to the passed format string. Also, ensures timezone is set to ET
        if needed.
        :param date_string: A datetime string
        :param date_format: A date formatting string (strftime)
        :param utc: Whether the source date is in UTC or not
        :return:
        """
        try:
            # Parse it
            date = parse(date_string)
            et_zone = tz.gettz('America/New_York')

            if utc:
                # Set UTC as timezone
                utc_zone = tz.gettz('UTC')
                utc_date = date.replace(tzinfo=utc_zone)

                # Convert time zone to assumed ET
                et_date = utc_date.astimezone(et_zone)

            else:
                # Set it as ET
                et_date = date.replace(tzinfo=et_zone)

            # Format it and return it
            return et_date.strftime(date_format)

        except ValueError as e:
            logger.exception('FHIR date parsing error: {}'.format(e), exc_info=True,
                             extra={'date_string': date_string, 'date_format': date_format})

            return '--/--/----'

    @staticmethod
    def flatten_questionnaire_response(bundle_dict, questionnaire_id):
        '''
        Picks out the relevant Questionnaire and QuestionnaireResponse resources and
        returns a dict mapping the text of each question to a list of answer texts.
        To handle duplicate question texts, each question is prepended with an index.
        :param bundle_dict: The parsed JSON response from a FHIR query
        :param questionnaire_id: The ID of the Questionnaire to parse for
        :return: dict
        '''

        # Build the bundle
        bundle = Bundle(bundle_dict)

        # Pick out the questionnaire and its response
        questionnaire = next((entry.resource for entry in bundle.entry if entry.resource.id == questionnaire_id), None)
        questionnaire_response = next((entry.resource for entry in bundle.entry if
                                       entry.resource.resource_type == 'QuestionnaireResponse' and
                                       entry.resource.questionnaire.reference ==
                                       'Questionnaire/{}'.format(questionnaire_id)), None)

        # Ensure resources exist
        if not questionnaire or not questionnaire_response:
            logger.debug('Missing resources: {}'.format(questionnaire_id))
            return None

        # Get questions and answers
        questions = FHIR._questions(questionnaire.item)
        answers = FHIR._answers(questionnaire_response.item)

        # Process sub-questions first
        for linkId, condition in {linkId: condition for linkId, condition in questions.items() if type(condition) is dict}.items():

            try:
                # Assume only one condition, fetch the parent question linkId
                parent = next(iter(condition))
                if not parent:
                    logger.warning('FHIR Error: Subquestion not properly specified: {}:{}'.format(linkId, condition),
                                   extra={'questionnaire': questionnaire_id, 'ppm_id': questionnaire_response.source,
                                          'questionnaire_response': questionnaire_response.id})
                    continue

                if len(condition) > 1:
                    logger.warning('FHIR Error: Subquestion has multiple conditions: {}:{}'.format(linkId, condition),
                                   extra={'questionnaire': questionnaire_id, 'ppm_id': questionnaire_response.source,
                                          'questionnaire_response': questionnaire_response.id})

                # Ensure they've answered this one
                if not answers.get(parent) or condition[parent] not in answers.get(parent):
                    continue

                # Get the question and answer item
                answer = answers[parent]
                index = answer.index(condition[parent])

                # Check for commas
                sub_answers = answers[linkId]
                if ',' in next(iter(sub_answers)):

                    # Split it
                    sub_answers = [sub.strip() for sub in next(iter(sub_answers)).split(',')]

                # Format them
                value = '{} <span class="label label-primary">{}</span>'.format(
                    answer[index], '</span>&nbsp;<span class="label label-primary">'.join(sub_answers))

                # Append the value
                answer[index] = mark_safe(value)

            except Exception as e:
                logger.exception('FHIR error: {}'.format(e), exc_info=True,
                                 extra={'questionnaire': questionnaire_id, 'link_id': linkId,
                                        'ppm_id': questionnaire_response.source})

        # Build the response
        response = collections.OrderedDict()

        # Process top-level questions first
        top_questions = collections.OrderedDict(sorted({linkId: question for linkId, question in questions.items() if
                                                        type(question) is str}.items(),
                                                       key=lambda q: int(q[0].split('-')[1])))
        for linkId, question in top_questions.items():

            # Check for the answer
            answer = answers.get(linkId)
            if not answer:
                answer = [mark_safe('<span class="label label-info">N/A</span>')]
                logger.warning(f'FHIR Error: No answer found for {linkId}',
                               extra={'questionnaire': questionnaire_id, 'link_id': linkId,
                                      'ppm_id': questionnaire_response.source})

            # Format the question text
            text = '{}. {}'.format(len(response.keys()) + 1, question)

            # Add the answer
            response[text] = answer

        return response

    @staticmethod
    def _questions(items):

        # Iterate items
        questions = {}
        for item in items:

            # Leave out display or ...
            if item.type == 'display':
                continue

            elif item.type == 'group' and item.item:

                # Get answers
                sub_questions = FHIR._questions(item.item)

                # Add them
                questions.update(sub_questions)

            elif item.enableWhen:

                # This is a sub-question
                questions[item.linkId] = {
                    next(condition.question for condition in item.enableWhen):
                        next(condition.answerString for condition in item.enableWhen)
                }

            else:

                # Ensure it has text
                if item.text:
                    # List them out
                    questions[item.linkId] = item.text

                else:
                    # Indicate a blank question text, presumably a sub-question
                    questions[item.linkId] = '-'

                # Check for subtypes
                if item.item:
                    # Get answers
                    sub_questions = FHIR._questions(item.item)

                    # Add them
                    questions.update(sub_questions)

        return questions

    @staticmethod
    def _answers(items):

        # Iterate items
        responses = {}
        for item in items:

            # List them out
            responses[item.linkId] = []

            # Ensure we've got answers
            if not item.answer:
                logger.error('FHIR questionnaire error: Missing items for question', extra={'link_id': item.linkId})
                responses[item.linkId] = ['------']

            else:

                # Iterate answers
                for answer in item.answer:

                    # Get the value
                    if answer.valueBoolean is not None:
                        responses[item.linkId].append(answer.valueBoolean)
                    elif answer.valueString is not None:
                        responses[item.linkId].append(answer.valueString)
                    elif answer.valueInteger is not None:
                        responses[item.linkId].append(answer.valueInteger)
                    elif answer.valueDate is not None:
                        responses[item.linkId].append(answer.valueDate)
                    elif answer.valueDateTime is not None:
                        responses[item.linkId].append(answer.valueDateTime)
                    elif answer.valueDateTime is not None:
                        responses[item.linkId].append(answer.valueDateTime)

                    else:
                        logger.warning('Unhandled answer value type: {}'.format(answer.as_json()),
                                       extra={'link_id': item.linkId})

            # Check for subtypes
            if item.item:
                # Get answers
                sub_answers = FHIR._answers(item.item)

                # Add them
                responses[item.linkId].extend(sub_answers)

        return responses

    @staticmethod
    def get_client():

        # Create the server
        settings = {
            'app_id': 'hms-dbmi-ppm-p2m2-admin',
            'api_base': PPM.fhir_url()
        }

        return FHIRClient(settings=settings)

    @staticmethod
    def get_ppm_id(email):

        try:
            # Get the client
            client = FHIR.get_client()

            # Query the Patient
            search = Patient.where(struct={'identifier': 'http://schema.org/email|{}'.format(email)})
            resources = search.perform_resources(client.server)
            for resource in resources:

                # Return the ID of the first Patient
                return resource.id

        except Exception as e:
            logger.debug('Could not fetch Patient\'s ID: {}'.format(e))

        return None

    @staticmethod
    def get_name(patient, full=False):

        # Default to a generic name
        names = []

        # Check official names
        for name in [name for name in patient.name if name.use == 'official']:
            if name.given:
                names.extend(name.given)

            # Add family if full name
            if name.family and (full or not names):
                names.append(name.family)

        if not names:
            logger.warning('Could not find name for {}'.format(patient.id))

            # Default to their email address
            email = next((identifier.value for identifier in patient.identifier if
                          identifier.system == 'http://schema.org/email'), None)

            if email:
                names.append(email)

            else:
                logger.error('Could not find email for {}'.format(patient.id))

        if not names:
            names = ['Participant']

        return ' '.join(names)

    @staticmethod
    def get_document_references(ppm_id, code=''):
        """
        Queries the current user's FHIR record for any DocumentReferences related to this type
        :return: A list of DocumentReferences
        :rtype: list
        """
        # Set the query
        query = {'patient': ppm_id, 'type': 'https://peoplepoweredmedicine.org/document-type|{}'.format(code)}

        return FHIR._query_resources('DocumentReference', query=query)

#######################################################################################################################
# Method below are untested amongst all services and unused ###########################################################
#######################################################################################################################

    @staticmethod
    def questionnaire_id(project):
        return PPM.Questionnaire.questionnaire_for_project(project)

    @staticmethod
    def consent_questionnaire_id(patient):
        if not patient.get('composition') or patient.get('project') != PPM.Project.ASD.value:
            return None

        return PPM.Questionnaire.questionnaire_for_project(patient.get('composition'))

    @staticmethod
    def is_test_patient(email):
        '''
        Checks test user email patterns and returns True if a user's email
        matches.
        :param email: The user's email address
        :return: bool
        '''

        # Iterate through all patterns
        for pattern in settings.TEST_EMAIL_PATTERNS:
            if re.match(pattern, email):
                return True

        return False

    @staticmethod
    def get_patients(request, project=None, enrollment=None):
        logger.debug('Getting patients - enrollment: {}'.format(enrollment))

        # Get patients.
        patients = FHIR._query_patients(active='false' if enrollment == 'ineligible' else 'true')

        # Filter on enrollment
        if enrollment:
            # Perform the filter and log the result, overwrite the patients list
            filtered_patients = [patient for patient in patients if patient['enrollment'] == enrollment]
            logger.debug('Enrollment \'{}\': {} of {}'.format(enrollment, len(filtered_patients), len(patients)))
            patients = filtered_patients

        # Collect emails.
        emails = [patient['email'] for patient in patients]

        # Collect participants.
        participants = P2M2.get_participants(request, emails)

        # Filter on project
        if project:
            # Filter the list of participants first
            filtered_participants = [email for email, participant in participants.items() if
                                     participant['project'] == project]

            # Do the filter
            filtered_patients = [patient for patient in patients if patient['email'] in filtered_participants]
            logger.debug('Enrollment \'{}\': {} of {}'.format(enrollment, len(filtered_patients), len(patients)))
            patients = filtered_patients

        # Compile test users
        show_test_users = request.user.email in settings.TEST_ADMIN_EMAILS

        # Collect them
        patient_list = []
        for patient in patients:

            # Check for a tester
            if not show_test_users and PPM.is_tester(patient['email']):
                logger.debug('Removing test patient: {}'.format(patient['email']))
                continue

            # Get the participant.
            participant = participants.get(patient['email'])
            if participant:
                patient['project'] = participant.get('project', 'ppm')

                # Set the date registered
                patient['date_registered'] = participant.get('date_registered')

            else:
                logger.error('No p2m2.participant found for {}'.format(patient['fhir_id']))
                patient['project'] = 'ppm'
                patient['date_registered'] = '???'

            # Add them
            patient_list.append(patient)

        return patient_list

    @staticmethod
    def get_patient(request, fhir_id=None, email=None, project=None, date_registered=None):

        # Set the url
        patient_url = furl(PPM.fhir_url())
        patient_url.path.segments.append('Patient')

        # Check what to query on
        if fhir_id:
            patient_url.query.params.add('_id', fhir_id)
        elif email:
            patient_url.query.params.add('identifier', 'http://schema.org/email|' + email)
        else:
            logger.error('Must pass FHIR ID or email!')
            return None

        patient_url.query.params.add('_include', '*')
        patient_url.query.params.add('_revinclude', '*')

        try:
            # Get it
            response = requests.get(patient_url.url)
            response.raise_for_status()

            # Get the list of entries
            patient_bundle = response.json()

            # Ensure a patient exists
            if not patient_bundle or not patient_bundle.get('total') or not patient_bundle.get('entry'):
                logger.debug('No resources returned for patient query: {}'.format(fhir_id))
                return {}

            # Get included resources
            patient_entries = patient_bundle['entry']

            # Flatten patient profile
            participant = FHIR.flatten_patient(patient_bundle)

            # Fetch details from p2m2
            if not project or not date_registered:
                p2m2_participant = P2M2.get_participant(request, participant['email'])

                if not project:
                    # Get the project and the registered date.
                    participant['project'] = p2m2_participant['project']

                if not date_registered:
                    # Convert the date
                    participant['date_registered'] = FHIR.format_date(p2m2_participant['date_registered'], '%m/%d/%Y')

        except Exception as e:
            logger.exception('FHIR error: {}'.format(e), exc_info=True,
                             extra={'ppm_id': fhir_id, 'email': email})
            return None

        try:
            # Get the Flag resource
            flag = next(
                resource['resource'] for resource in patient_entries if resource['resource']['resourceType'] == 'Flag')
            enrollment = FHIR.flatten_enrollment_flag(flag)
            participant['enrollment'] = enrollment['enrollment']

            # Check for accepted and a start date
            if participant['enrollment'] == 'accepted' and enrollment['start']:

                # Convert time zone to assumed ET
                participant['enrollment_accepted_date'] = FHIR.format_date(enrollment['start'], '%-m/%-d/%Y')

            else:
                participant['enrollment_accepted_date'] = ""

        except Exception as e:
            logger.exception('FHIR enrollment flag error: {}'.format(e), exc_info=True,
                             extra={'ppm_id': fhir_id, 'email': email})

        try:
            participant['composition'] = FHIR.flatten_consent_composition(patient_bundle)
        except KeyError:
            participant['composition'] = None

        if participant['project'] == 'autism':
            try:
                # Get the questionnaire ID
                quiz_id = FHIR.consent_questionnaire_id(participant)

                # Sort it.
                participant['consent_quiz'] = FHIR.questionnaire_response(patient_bundle, quiz_id)

            except Exception:
                participant['consent_quiz'] = None

        try:
            # Get the project
            _questionnaire_id = FHIR.questionnaire_id(participant['project'])

            # Parse out the responses
            participant['questionnaire'] = FHIR.questionnaire_response(patient_bundle, _questionnaire_id)

        except Exception:
            participant['questionnaire'] = None

        try:
            participant['points_of_care'] = FHIR.flatten_list(patient_bundle, 'Organization')
        except Exception:
            participant['points_of_care'] = None

        if participant['project'] == 'neer':

            try:
                participant['research_studies'] = FHIR.query_research_studies(patient_bundle)

            except Exception:
                participant['research_studies'] = None

        try:
            p2md_smart_authorizations = P2MD.get_smart_authorizations(request, fhir_id)
            logger.debug('Found {} SMART authorizations'.format(len(p2md_smart_authorizations)))

            # Check for SMART authorizations
            participant['smart_authorizations'] = p2md_smart_authorizations

        except Exception:
            participant['smart_authorizations'] = []

        return participant

    @staticmethod
    def _bundle_get(bundle, resource_type, query={}):
        '''
        Searches through a bundle for the resource matching the given resourceType
        and query, if passed,
        '''

        # Get matching resources
        resources = [entry.resource for entry in bundle.entry if entry.resource.resource_type == resource_type]

        # Match
        for resource in resources:
            for key, value in query:
                attribute = FHIR._get_attribute_or(resource, key)

                # Compare
                if not attribute or attribute != value:
                    break

            # All comparisons passed
            return resource

        return None

    @staticmethod
    def _get_or(item, keys, default=''):
        '''
        Fetch a property from a json object. Keys is a list of keys and indices to use to
        fetch the property. Returns the passed default string if the path through the json
        does not exist.
        :param item: The json to parse properties from
        :type item: json object
        :param keys: The list of keys and indices for the property
        :type keys: A list of string or int
        :param default: The default string to use if a property could not be found
        :type default: String
        :return: The requested property or the default value if missing
        :rtype: String
        '''
        try:
            # Try it out.
            for key in keys:
                item = item[key]

            return item
        except (KeyError, IndexError):
            return default

    @staticmethod
    def _get_attribute_or(item, keys, default=None):
        '''
        Fetch an attribute from an object. Keys is a list of attribute names and indices to use to
        fetch the property. Returns the passed default object if the path through the object
        does not exist.
        :param item: The object to get from
        :type item: object
        :param keys: The list of keys and indices for the property
        :type keys: A list of string or int
        :param default: The default object to use if a property could not be found
        :type default: object
        :return: The requested property or the default value if missing
        :rtype: object
        '''
        try:
            # Try it out.
            for key in keys:

                # Check for integer or string
                if type(key) is str:
                    item = getattr(item, key)

                elif type(key) is int:
                    item = item[key]

            return item
        except (AttributeError, IndexError):
            return default

    @staticmethod
    def _get_resource_type(bundle):

        # Check for entries
        if bundle.get('entry') and len(bundle.get('entry', [])) > 0:
            return bundle['entry'][0]['resource']['resourceType']

        logger.warning('Could not determine resource type: {}'.format(bundle))
        return None

    @staticmethod
    def _get_next_url(bundle, relative=False):

        # Get the next URL
        next_url = next((link['url'] for link in bundle['link'] if link['relation'] == 'next'), None)
        if next_url:

            # Check URL type
            if relative:

                # We only want the resource type and the parameters
                resource_type = bundle['entry'][0]['resource']['resourceType']

                return '{}?{}'.format(resource_type, next_url.split('?', 1)[1])

            else:
                return next_url

        return None

    @staticmethod
    def _query_patients(active='true'):

        # Build the query
        query = {
            'active': active,
            '_revinclude': 'Flag:subject',
        }

        # Peel out patients
        bundle = FHIR._query_bundle('Patient', query)

        # Check empties
        if bundle.total == 0:
            logger.debug('No patients!')
            return []
        else:
            logger.debug('Found {} patients'.format(int(len(bundle.entry) / 2)))

        # Process them
        enrollments = {entry.resource.subject.reference.split('/')[1]: entry.resource.code.coding[0].code
                       for entry in bundle.entry if entry.resource.resource_type == 'Flag'}

        # Process patients
        patients = []
        for patient in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Patient']:

            # Build the dict
            patient_dict = {
                'email': patient.identifier[0].value,
                'fhir_id': patient.id,
                'enrollment': enrollments.get(patient.id, '???'),
            }

            # Check names
            try:
                patient_dict['firstname'] = patient.name[0].given[0]
            except Exception:
                patient_dict['firstname'] = "---"
                logger.warning('No firstname for Patient/{}'.format(patient.id))
            try:
                patient_dict['lastname'] = patient.name[0].family
            except Exception:
                patient_dict['lastname'] = "---"
                logger.warning('No lastname for Patient/{}'.format(patient.id))

            # Add twitter handle
            try:
                for telecom in patient.telecom:
                    if telecom.system == "other" and telecom.value.startswith("https://twitter.com"):
                        patient_dict['twitter_handle'] = telecom.value
            except Exception:
                pass

            # Add it
            patients.append(patient_dict)

        return patients

    @staticmethod
    def delete_consent(patient_id, project):
        logger.debug('Deleting consents: Patient/{}'.format(patient_id))

        # Build the transaction
        transaction = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': []
        }

        # Add the composition delete
        transaction['entry'].append({
            'request': {
                'url': 'Composition?subject=Patient/{}'.format(patient_id),
                'method': 'DELETE',
            }
        })

        # Add the consent delete
        transaction['entry'].append({
            'request': {
                'url': 'Consent?patient=Patient/{}'.format(patient_id),
                'method': 'DELETE',
            }
        })

        # Add the contract delete
        transaction['entry'].append({
            'request': {
                'url': 'Contract?signer=Patient/{}'.format(patient_id),
                'method': 'DELETE',
            }
        })

        # Check project
        if project == 'autism':

            questionnaire_ids = ['ppm-asd-consent-guardian-quiz',
                                 'ppm-asd-consent-individual-quiz',
                                 'individual-signature-part-1',
                                 'guardian-signature-part-1',
                                 'guardian-signature-part-2',
                                 'guardian-signature-part-3', ]

            # Add the questionnaire response delete
            for questionnaire_id in questionnaire_ids:
                transaction['entry'].append({
                    'request': {
                        'url': 'QuestionnaireResponse?questionnaire=Questionnaire/{}&source=Patient/{}'
                            .format(questionnaire_id, patient_id),
                        'method': 'DELETE',
                    }
                })

            # Add the contract delete
            transaction['entry'].append({
                'request': {
                    'url': 'Contract?signer.patient={}'.format(patient_id),
                    'method': 'DELETE',
                }
            })

            # Remove related persons
            transaction['entry'].append({
                'request': {
                    'url': 'RelatedPerson?patient=Patient/{}'.format(patient_id),
                    'method': 'DELETE',
                }
            })

        elif project == 'neer':

            # Delete questionnaire responses
            questionnaire_id = 'neer-signature'
            transaction['entry'].append({
                'request': {
                    'url': 'QuestionnaireResponse?questionnaire=Questionnaire/{}&source=Patient/{}'
                        .format(questionnaire_id, patient_id),
                    'method': 'DELETE',
                }
            })

        else:
            logger.error('Unsupported project: {}'.format(project), extra={'ppm_id': patient_id})

        # Make the FHIR request.
        response = requests.post(PPM.fhir_url(), headers={'content-type': 'application/json'},
                                 data=json.dumps(transaction))
        response.raise_for_status()

    @staticmethod
    def update_patient_enrollment(patient_id, status):
        logger.debug("Patient: {}, Status: {}".format(patient_id, status))

        # Fetch the flag.
        url = furl(PPM.fhir_url())
        url.path.segments.append('Flag')

        query = {
            'subject': 'Patient/{}'.format(patient_id),
        }

        content = None
        try:
            # Fetch the flag.
            response = requests.get(url.url, params=query)
            flag_entries = Bundle(response.json())

            # Check for nothing.
            if flag_entries.total == 0:
                logger.warning('FHIR Error: Flag does not already exist for Patient/{}'.format(patient_id),
                               extra={'status': status})

                # Create it.
                return FHIR.create_patient_enrollment('Patient/{}'.format(patient_id), status)

            else:
                logger.debug('Existing enrollment flag found')

                # Get the first and only flag.
                entry = flag_entries.entry[0]
                flag = entry.resource
                code = flag.code.coding[0]

                # Update flag properties for particular states.
                logger.debug('Current status: {}'.format(code.code))
                if code.code != 'accepted' and status == 'accepted':
                    logger.debug('Setting enrollment flag status to "active"')

                    # Set status.
                    flag.status = 'active'

                    # Set a start date.
                    now = FHIRDate(datetime.now().isoformat())
                    period = Period()
                    period.start = now
                    flag.period = period

                elif code.code != 'terminated' and status == 'terminated':
                    logger.debug('Setting enrollment flag status to "inactive"')

                    # Set status.
                    flag.status = 'inactive'

                    # Set an end date.
                    now = FHIRDate(datetime.now().isoformat())
                    flag.period.end = now

                elif code.code == 'accepted' and status != 'accepted':
                    logger.debug('Reverting back to inactive with no dates')

                    # Flag defaults to inactive with no start or end dates.
                    flag.status = 'inactive'
                    flag.period = None

                elif code.code != 'ineligible' and status == 'ineligible':
                    logger.debug('Setting as ineligible, inactive with no dates')

                    # Flag defaults to inactive with no start or end dates.
                    flag.status = 'inactive'
                    flag.period = None

                else:
                    logger.debug('Unhandled flag update: {} -> {}'.format(code.code, status))

                # Set the code.
                code.code = status
                code.display = status.title()
                flag.code.text = status.title()

                # Build the URL
                flag_url = furl(PPM.fhir_url())
                flag_url.path.segments.extend(['Flag', flag.id])

                logger.debug('Updating Flag "{}" with code: "{}"'.format(flag_url.url, status))

                # Post it.
                response = requests.put(flag_url.url, json=flag.as_json())
                content = response.content
                response.raise_for_status()

                return flag

        except requests.HTTPError as e:
            logger.exception('FHIR Connection Error: {}'.format(e), exc_info=True,
                             extra={'response': content, 'url': url.url, 'ppm_id': patient_id, 'status': status})
            raise

        except Exception as e:
            logger.exception('FHIR error: {}'.format(e), exc_info=True, extra={'ppm_id': patient_id})
            raise

    @staticmethod
    def create_patient_enrollment(patient_id, status='registered'):
        """
        Create a Flag resource in the FHIR server to indicate a user's enrollment.
        :param patient_id:
        :param status:
        :return:
        """
        logger.debug("Patient: {}".format(patient_id))

        # Use the FHIR client lib to validate our resource.
        flag = Flag(FHIR.Resources.enrollment_flag(patient_id, status))

        # Set a date if enrolled.
        if status == 'accepted':
            now = FHIRDate(datetime.now().isoformat())
            period = Period()
            period.start = now
            flag.period = period

        # Build the FHIR Flag destination URL.
        url = furl(PPM.fhir_url())
        url.path.segments.append('Flag')

        logger.debug('Creating flag at: {}'.format(url.url))

        # Create the flag
        content = None
        try:
            response = requests.post(url.url, json=flag.as_json())
            content = response.content
            response.raise_for_status()

            return response

        except requests.HTTPError as e:
            logger.exception('FHIR Connection Error: {}'.format(e), exc_info=True,
                             extra={'response': content, 'url': url.url, 'ppm_id': patient_id, 'status': status})

        return None

    @staticmethod
    def update_twitter(email, handle=None):
        logger.debug('Twitter handle: {}'.format(handle))

        try:
            # Fetch the Patient.
            url = furl(PPM.fhir_url())
            url.path.segments.extend(['Patient'])
            url.query.params.add('identifier', 'http://schema.org/email|{}'.format(email))
            response = requests.get(url.url)
            response.raise_for_status()
            patient = response.json().get('entry')[0]['resource']

            # Check if handle submitted or not
            if handle:

                # Set the value
                twitter = {'system': 'other', 'value': 'https://twitter.com/' + handle}

                # Add it to their contact points
                patient.setdefault('telecom', []).append(twitter)

            else:
                # Check for existing handle and remove it
                for telecom in patient.get('telecom', []):
                    if 'twitter.com' in telecom['value']:
                        patient['telecom'].remove(telecom)

            # Check for an existing Twitter status extension
            uses_twitter = next((extension for extension in patient.get('extension', [])
                                 if 'uses-twitter' in extension.get('url')), None)
            if uses_twitter:

                # Update the flag
                uses_twitter['valueBoolean'] = True if handle else False

            else:
                # Add an extension indicating their use of Twitter
                uses_twitter = {
                        'url': 'https://p2m2.dbmi.hms.harvard.edu/fhir/StructureDefinition/uses-twitter',
                        'valueBoolean': True if handle else False
                    }

                # Add it to their extensions
                patient.setdefault('extension', []).append(uses_twitter)

            logger.debug('Extension: {}'.format(patient['extension']))

            # Save
            url.query.params.clear()
            url.path.segments.append(patient['id'])
            response = requests.put(url.url, data=json.dumps(patient))
            response.raise_for_status()

            return response.ok

        except Exception as e:
            logger.exception('FHIR error: {}'.format(e), exc_info=True, extra={'ppm_id': email})

        return False

    @staticmethod
    def _fix_bundle_json(bundle_json):
        '''
        Random tasks to make FHIR resources compliant. Some resources from early-on were'nt
        strictly compliant and would throw exceptions when building FHIRClient objects. This
        takes the json and adds needed properties/attributes.
        :param bundle_json: FHIR Bundle json from server
        :return: json
        '''

        # Appeases the FHIR library by ensuring question items all have linkIds, regardless of an associated answer.
        for question in [entry['resource'] for entry in bundle_json['entry']
                         if entry['resource']['resourceType'] == 'Questionnaire']:
            for item in question['item']:
                if 'linkId' not in item:
                    # Assign a random string for the linkId
                    item['linkId'] = "".join(
                        [random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for _ in range(10)])

        # Appeases the FHIR library by ensuring document references have 'indexed'
        for document in [entry['resource'] for entry in bundle_json['entry']
                         if entry['resource']['resourceType'] == 'DocumentReference']:
            if not document.get('indexed'):
                document['indexed'] = datetime.utcnow().isoformat()

        return bundle_json

    @staticmethod
    def flatten_enrollment_flag(resource):

        # Get the resource.
        record = dict()

        # Try and get the values
        record['enrollment'] = FHIR._get_or(resource, ['code', 'coding', 0, 'code'])
        record['status'] = FHIR._get_or(resource, ['status'])
        record['start'] = FHIR._get_or(resource, ['period', 'start'])
        record['end'] = FHIR._get_or(resource, ['period', 'end'])

        return record

    @staticmethod
    def _exception_description(display):

        # Check the various exception display values
        if 'equipment monitoring' in display.lower() or 'fitbit' in display.lower():
            return mark_safe('<span class="label label-danger">Fitbit monitoring</span>')

        elif 'referral to clinical trial' in display.lower():
            return mark_safe('<span class="label label-danger">Future contact/questionnaires</span>')

        elif 'saliva' in display.lower():
            return mark_safe('<span class="label label-danger">Saliva sample</span>')

        elif 'blood sample' in display.lower():
            return mark_safe('<span class="label label-danger">Blood sample</span>')

        elif 'stool sample' in display.lower():
            return mark_safe('<span class="label label-danger">Stool sample</span>')

        elif 'tumor' in display.lower():
            return mark_safe('<span class="label label-danger">Tumor tissue samples</span>')

        else:
            logger.warning('Could not format exception: {}'.format(display))
            return display

    @staticmethod
    def flatten_patient(bundle_dict):

        # Get the patient
        resource = next(resource['resource'] for resource in bundle_dict['entry']
                        if resource['resource']['resourceType'] == 'Patient')

        # Collect properties
        patient = dict()

        # Get email and FHIR ID
        patient["email"] = FHIR._get_or(resource, ['identifier', 0, 'value'])
        patient["fhir_id"] = resource['id']
        if not patient['email']:
            logger.error('Patient email could not be found: {}'.format(resource['id']))
            return {}

        # Get the remaining optional properties
        patient["firstname"] = FHIR._get_or(resource, ['name', 0, 'given', 0], '')
        patient["lastname"] = FHIR._get_or(resource, ['name', 0, 'family'], '')
        patient["street_address1"] = FHIR._get_or(resource, ['address', 0, 'line', 0], '')
        patient["street_address2"] = FHIR._get_or(resource, ['address', 0, 'line', 1], '')
        patient["city"] = FHIR._get_or(resource, ['address', 0, 'city'], '')
        patient["state"] = FHIR._get_or(resource, ['address', 0, 'state'], '')
        patient["zip"] = FHIR._get_or(resource, ['address', 0, 'postalCode'], '')
        patient["phone"] = FHIR._get_or(resource, ['telecom', 0, 'postalCode'], '')

        # Parse telecom properties
        patient['phone'] = next((telecom['value'] for telecom in resource.get('telecom', [])
                                 if telecom.get('system') == 'phone'), '')
        patient['twitter_handle'] = next((telecom['value'] for telecom in resource.get('telecom', [])
                                         if telecom.get('system') == 'other'), '')
        patient['contact_email'] = next((telecom['value'] for telecom in resource.get('telecom', [])
                                        if telecom.get('system') == 'email'), '')

        # Get how they heard about PPM
        patient['how_did_you_hear_about_us'] = next((extension['valueString'] for extension in resource.get('extension', [])
                                                    if 'how-did-you-hear-about-us' in extension.get('url')), '')

        # Get if they are not using Twitter
        patient['uses_twitter'] = next((extension['valueBoolean'] for extension in resource.get('extension', [])
                                                    if 'uses-twitter' in extension.get('url')), True)

        return patient

    @staticmethod
    def flatten_consent_composition(bundle_json):
        logger.debug('Flatten composition')

        # Add link IDs.
        FHIR._fix_bundle_json(bundle_json)

        # Parse the bundle in not so strict mode
        incoming_bundle = Bundle(bundle_json, strict=True)

        # Prepare the object.
        consent_object = {
            'consent_questionnaires': [],
            'assent_questionnaires': [],
        }
        consent_exceptions = []
        assent_exceptions = []

        if incoming_bundle.total > 0:

            for bundle_entry in incoming_bundle.entry:
                if bundle_entry.resource.resource_type == "Consent":

                    signed_consent = bundle_entry.resource

                    # We can pull the date from the Consent Resource. It's stamped in a few places.
                    consent_object["date_signed"] = signed_consent.dateTime.origval

                    # Exceptions are for when they refuse part of the consent.
                    if signed_consent.except_fhir:
                        for consent_exception in signed_consent.except_fhir:

                            # Check for conversion
                            display = consent_exception.code[0].display
                            consent_exceptions.append(FHIR._exception_description(display))

                elif bundle_entry.resource.resource_type == 'Composition':

                    composition = bundle_entry.resource

                    entries = [section.entry for section in composition.section if section.entry is not None]
                    references = [entry[0].reference for entry in entries if
                                  len(entry) > 0 and entry[0].reference is not None]
                    text = [section.text.div for section in composition.section if section.text is not None][0]

                    # Check the references for a Consent object, making this comp the consent one.
                    if len([r for r in references if 'Consent' in r]) > 0:
                        consent_object['consent_text'] = text
                    else:
                        consent_object['assent_text'] = text

                elif bundle_entry.resource.resource_type == "RelatedPerson":
                    pass
                elif bundle_entry.resource.resource_type == "Contract":

                    contract = bundle_entry.resource

                    # Contracts with a binding reference are either the individual consent or the guardian consent.
                    if contract.bindingReference:

                        # Fetch the questionnaire and its responses.
                        questionnaire_response_id = re.search('[^\/](\d+)$', contract.bindingReference.reference).group(0)
                        questionnaire_response = next((entry.resource for entry in incoming_bundle.entry if
                                                  entry.resource.resource_type == 'QuestionnaireResponse' and
                                                  entry.resource.id == questionnaire_response_id), None)

                        # Get the questionnaire and its response.
                        questionnaire_id = questionnaire_response.questionnaire.reference.split('/')[1]
                        questionnaire = [entry.resource for entry in incoming_bundle.entry if
                                         entry.resource.resource_type == 'Questionnaire'
                                         and entry.resource.id == questionnaire_id][0]

                        if not questionnaire_response or not questionnaire:
                            logger.error('FHIR Error: Could not find bindingReference Questionnaire/Response'
                                         ' for Contract/{}'.format(contract.id),
                                         extra={'ppm_id': contract.subject, 'questionnaire': questionnaire_id,
                                                'questionnaire_response': questionnaire_response_id})
                            break

                        # The reference refers to a Questionnaire which is linked to a part of the consent form.
                        if questionnaire_response.questionnaire.reference == "Questionnaire/individual-signature-part-1"\
                                or questionnaire_response.questionnaire.reference == "Questionnaire/neer-signature":

                            # This is a person consenting for themselves.
                            consent_object["type"] = "INDIVIDUAL"
                            consent_object["signer_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                            consent_object["participant_name"] = contract.signer[0].signature[0].whoReference.display

                            # These don't apply on an Individual consent.
                            consent_object["participant_acknowledgement_reason"] = "N/A"
                            consent_object["participant_acknowledgement"] = "N/A"
                            consent_object["signer_name"] = "N/A"
                            consent_object["signer_relationship"] = "N/A"
                            consent_object["assent_signature"] = "N/A"
                            consent_object["assent_date"] = "N/A"
                            consent_object["explained_signature"] = "N/A"

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-1":

                            # This is a person consenting for someone else.
                            consent_object["type"] = "GUARDIAN"

                            related_id = contract.signer[0].party.reference.split('/')[1]
                            related_person = [entry.resource for entry in incoming_bundle.entry if
                                             entry.resource.resource_type == 'RelatedPerson'
                                         and entry.resource.id == related_id][0]

                            consent_object["signer_name"] = related_person.name[0].text
                            consent_object["signer_relationship"] = related_person.relationship.text

                            consent_object["participant_name"] = contract.signer[0].signature[0].onBehalfOfReference.display
                            consent_object["signer_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-2":

                            # This is the question about being able to get acknowledgement from the participant by the guardian/parent.
                            consent_object["participant_acknowledgement"] = next(item.answer[0].valueString for item in questionnaire_response.item if item.linkId == 'question-1').title()

                            # If the answer to the question is no, grab the reason.
                            if consent_object["participant_acknowledgement"].lower() == "no":
                                consent_object["participant_acknowledgement_reason"] = next(item.answer[0].valueString for item in questionnaire_response.item if item.linkId == 'question-1-1')

                            # This is the Guardian's signature letting us know they tried to explain this study.
                            consent_object["explained_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":

                            # A contract without a reference is the assent page.
                            consent_object["assent_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                            consent_object["assent_date"] = contract.issued.origval

                            # Append the Questionnaire Text if the response is true.
                            for current_response in questionnaire_response.item:

                                if current_response.answer[0].valueBoolean:
                                    answer = [item for item in questionnaire.item if item.linkId == current_response.linkId][0]
                                    assent_exceptions.append(FHIR._exception_description(answer.text))

                        # Prepare to parse the questionnaire.
                        questionnaire_object = {
                            'template': 'dashboard/{}.html'.format(questionnaire.id),
                            'questions': []
                        }

                        for item in questionnaire.item:

                            question_object = {
                                'type': item.type,
                            }

                            if item.type == 'display':
                                question_object['text'] = item.text

                            elif item.type == 'boolean' or item.type == 'question':
                                # Get the answer.
                                for response in questionnaire_response.item:
                                    if response.linkId == item.linkId:
                                        # Process the question, answer and response.
                                        if item.type == 'boolean':
                                            question_object['text'] = item.text
                                            question_object['answer'] = response.answer[0].valueBoolean

                                        elif item.type == 'question':
                                            question_object['yes'] = item.text
                                            question_object['no'] = 'I was not able to explain this study to my child or ' \
                                                                    'individual in my care who will be participating'
                                            question_object['answer'] = response.answer[0].valueString is 'yes'

                            # Add it.
                            questionnaire_object['questions'].append(question_object)

                        # Check the type.
                    if questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":
                        consent_object['assent_questionnaires'].append(questionnaire_object)
                    else:
                        consent_object['consent_questionnaires'].append(questionnaire_object)

        consent_object["exceptions"] = consent_exceptions
        consent_object["assent_exceptions"] = assent_exceptions

        return consent_object

    @staticmethod
    def update_patient(fhir_id, form):

        # Get their resource
        patient = FHIR._query_resource('Patient', fhir_id)

        # Make the updates
        content = None
        try:
            # Check form data and make updates where necessary
            first_name = form.pop('firstname')
            if first_name:
                patient['name'][0]['given'][0] = first_name

            last_name = form.pop('lastname')
            if last_name:
                patient['name'][0]['family'] = last_name

            street_address1 = form.pop('street_address1')
            if street_address1:
                patient['address'][0]['line'][0] = street_address1

            street_address2 = form.pop('street_address2')
            if street_address2:
                patient['address'][0]['line'][1] = street_address2

            city = form.pop('city')
            if city:
                patient['address'][0]['city'] = city

            state = form.pop('state')
            if state:
                patient['address'][0]['state'] = state

            zip_code = form.pop('zip')
            if zip_code:
                patient['address'][0]['postalCode'] = zip_code

            phone = form.pop('phone')
            if phone:
                for telecom in patient['telecom']:
                    if telecom['system'] == 'phone':
                        telecom['value'] = phone
                else:
                    # Add it
                    patient['telecom'].append({'system': 'phone', 'value': phone})

            email = form.pop('contact_email')
            if email:
                for telecom in patient['telecom']:
                    if telecom['system'] == 'email':
                        telecom['value'] = email
                else:
                    # Add it
                    patient['telecom'].append({'system': 'email', 'value': email})

            # Build the URL
            url = furl(PPM.fhir_url())
            url.path.segments.append('Patient')
            url.path.segments.append(fhir_id)

            # Put it
            response = requests.put(url.url, json=patient)
            content = response.content
            response.raise_for_status()

            return response.ok

        except requests.HTTPError as e:
            logger.error('FHIR Request Error: {}'.format(e), exc_info=True,
                         extra={'ppm_id': fhir_id, 'response': content})

        except Exception as e:
            logger.error('FHIR Error: {}'.format(e), exc_info=True, extra={'ppm_id': fhir_id})

        return False

    @staticmethod
    def get_list(bundle, resource_type):

        # Check the bundle type
        if type(bundle) is dict:
            bundle = Bundle(bundle)

        for list in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'List']:

            # Compare the type
            for item in [entry.item for entry in list.entry]:

                # Check for a reference
                if item.reference and resource_type == item.reference.split('/')[0]:

                    return list

        return None

    @staticmethod
    def flatten_list(bundle, resource_type):

        # Check the bundle type
        if type(bundle) is dict:
            bundle = Bundle(bundle)

        list = FHIR.get_list(bundle, resource_type)

        # Get the references
        references = [entry.item.reference for entry in list.entry if entry.item.reference]

        # Find it in the bundle
        resources = [entry.resource for entry in bundle.entry if '{}/{}'.format(resource_type, entry.resource.id)
                     in references]

        # Flatten them according to type
        if resource_type == 'Organization':

            return [organization.name for organization in resources]

        elif resource_type == 'ResearchStudy':

            return [study.title for study in resources]

        else:
            logger.error('Unhandled list resource type: {}'.format(resource_type))
            return None

    @staticmethod
    def query_enrollment_flag(email, flatten_return=False):

        # Build the FHIR Consent URL.
        url = furl(PPM.fhir_url())
        url.path.segments.append('Flag')

        # Get flags for current user
        query = {
            'subject:Patient.identifier': 'http://schema.org/email|' + email
        }

        # Make the call
        content = None
        try:
            # Make the FHIR request.
            response = requests.get(url.url, params=query)
            content = response.content

            if flatten_return:
                return FHIR.flatten_enrollment_flag(response.json())
            else:
                return response.json()

        except requests.HTTPError as e:
            logger.exception('FHIR Connection Error: {}'.format(e), exc_info=True, extra={'response': content})

        except KeyError as e:
            logger.exception('FHIR Error: {}'.format(e), exc_info=True, extra={'response': content})

        return None

    @staticmethod
    def query_enrollment_status(email):

        try:
            # Make the FHIR request.
            response = FHIR.query_enrollment_flag(email)

            # Parse the bundle.
            bundle = Bundle(response)
            if bundle.total > 0:

                # Check flags.
                for flag in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Flag']:

                    # Get the code's value
                    state = flag.code.coding[0].code
                    logger.debug('Fetched state "{}" for user'.format(state))

                    return state

            else:
                logger.debug('No flag found for user!')

        except KeyError as e:
            logger.exception('FHIR Error: {}'.format(e), exc_info=True)

        return None

    @staticmethod
    def query_enrollment_flags(emails):
        logger.debug("Querying enrollment for patients: {}".format(len(emails)))

        # Build the transaction
        transaction = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': []
        }

        # Iterate emails
        for email in emails:

            # Add the request
            transaction['entry'].append({
                'request': {
                    'url': '/Flag?subject:Patient.identifier=http://schema.org/email|' + quote(email) + '&_include=*',
                    'method': 'GET'
                }
            })

        try:
            # Make the FHIR request.
            response = requests.post(PPM.fhir_url(), headers={'content-type': 'application/json'},
                                     data=json.dumps(transaction))
            response.raise_for_status()

            # Create the bundle resource
            bundle = Bundle(response.json())

            # Get patient email to ID mapping
            mappings = FHIR.map_patients_id_to_email(bundle)

            enrollments = {}

            # Iterate flags
            for flag in [entry.resource for entry in bundle.entry[0].resource.entry if entry.resource.resource_type == 'Flag']:

                # Get the status string and patient id
                patient = flag.subject.reference.split('/')[1]
                code = flag.code.coding[0].code

                # Set it
                enrollments[mappings[patient]] = code

            return enrollments

        # Set it
        except KeyError as e:
            logger.exception('FHIR error: {}'.format(e), exc_info=True)

            raise

    @staticmethod
    def map_patients_id_to_email(bundle):

        # Set up the dict
        patients = {}

        # Iterate resources
        for patient in [entry.resource for entry in bundle.entry[0].resource.entry if entry.resource.resource_type == 'Patient']:

            # Get their email identifier
            identifier = next(identifier for identifier in patient.identifier
                              if identifier.system == 'http://schema.org/email')
            if identifier:

                # Get the id
                patients[patient.id] = identifier.value

            else:
                logger.warning('Identifier not found for Patient {}'.format(patient.id))

        return patients

    @staticmethod
    def questionnaire_answers(bundle_dict, questionnaire_id):
        '''
        Returns a list of the correct answer values for the given questionnaire quiz. This is
        pretty hardcoded so not that useful for anything but ASD consent quizzes.
        :param bundle_dict: A bundle resource from FHIR containing the Questionnaire
        :type bundle_dict: dict
        :param questionnaire_id: The FHIR ID of the Questionnaire to handle
        :type questionnaire_id: str
        :return: List of correct answer values
        :rtype: [str]
        '''

        # Build the bundle
        bundle = Bundle(bundle_dict)

        # Pick out the questionnaire and its response
        questionnaire = next((entry.resource for entry in bundle.entry if entry.resource.id == questionnaire_id), None)

        # Ensure resources exist
        if not questionnaire:
            logger.error('Missing Questionnaire: {}'.format(questionnaire_id))
            return []

        # Return the correct answers
        answers = []

        # Check which questionnaire
        if questionnaire_id == 'ppm-asd-consent-individual-quiz':

            answers = [
                questionnaire.item[0].option[0].valueString,
                questionnaire.item[1].option[0].valueString,
                questionnaire.item[2].option[1].valueString,
                questionnaire.item[3].option[3].valueString,
            ]

        elif questionnaire_id == 'ppm-asd-consent-guardian-quiz':

            answers = [
                questionnaire.item[0].option[0].valueString,
                questionnaire.item[1].option[0].valueString,
                questionnaire.item[2].option[1].valueString,
                questionnaire.item[3].option[3].valueString,
            ]

        return answers

    @staticmethod
    def query_research_studies(bundle):

        # Find Research subjects
        subjects = [entry['resource'] for entry in bundle['entry'] if
                    entry['resource']['resourceType'] == 'ResearchSubject']
        if not subjects:
            logger.debug('No Research Subjects, no Research Studies')
            return None

        # Get study IDs
        research_study_ids = [subject['study']['reference'].split('/')[1] for subject in subjects]

        if not research_study_ids:
            logger.error('Could not get IDs from resources: {}'.format(subjects), extra={
                'subjects': subjects
            })
            return None

        # Make the query
        research_study_url = furl(PPM.fhir_url())
        research_study_url.path.add('ResearchStudy')
        research_study_url.query.params.add('_id', ','.join(research_study_ids))

        # Fetch them
        research_study_response = requests.get(research_study_url.url)

        # Get the IDs
        research_studies = research_study_response.json().get('entry', [])

        # Return the titles
        return [research_study['resource']['title'] for research_study in research_studies]

    class Resources:

        @staticmethod
        def enrollment_flag(patient_id, status='proposed', start=None, end=None):

            data = {
                'resourceType': 'Flag',
                'status': 'active' if status == 'accepted' else 'inactive',
                'category': {
                    'coding': [{
                        'system': 'http://hl7.org/fhir/flag-category',
                        'code': 'admin',
                        'display': 'Admin',
                    }],
                    'text': 'Admin'
                },
                'code': {
                    'coding': [{
                        'system': 'https://peoplepoweredmedicine.org/enrollment-status',
                        'code': status,
                        'display': status.title(),
                    }],
                    'text': status.title(),
                },
                "subject": {
                    "reference": patient_id
                }
            }

            # Set dates if specified.
            if start:
                data['period'] = {
                    'start': start.isoformat()
                }
                if end:
                    data['period']['end'] = end.isoformat()

            return data

        def document(patient_id, description, data):

            data = {
                'resourceType': 'DocumentReference',
                "subject": {
                    "reference": "Patient/" + patient_id
                },
                "type": {
                    "text": description
                },
                "status": "current",
                "content": [{
                    "attachment": {
                        "contentType": "application/json",
                        "language": "en-US",
                        "data": data
                    }
                }]
            }

            return data

        @staticmethod
        def patient(email, first_name, last_name, street_address1, street_address2,
                    city, zip_code, state, phone, twitter=None):

            data = {
                'resourceType': 'Patient',
                'identifier': [
                    {
                        'system': 'http://schema.org/email',
                        'value': email,
                    },
                ],
                'name': [
                    {
                        'use': 'official',
                        'family': last_name,
                        'given': [first_name],
                    },
                ],
                'address': [
                    {
                        'line': [
                            street_address1,
                            street_address2,
                        ],
                        'city': city,
                        'postalCode': zip_code,
                        'state': state,
                    }
                ],
                'telecom': [
                    {
                        'system': 'phone',
                        'value': phone,
                    },
                ],
            }

            # Convert the twitter handle to a URL
            if twitter:
                data['telecom'].append({
                    'system': 'other',
                    'value': 'https://twitter.com/' + twitter,
                })

            return data

        @staticmethod
        def organization_list(item_ids, patient_id=None):

            data = {
                "resourceType": "List",
                "id": random.randint(10, 500),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "status": "current",
                "mode": "working",
                "code": {
                    "coding": [{
                        "system": "http://snomed.info/sct/900000000000207008",
                        "code": "SNOMED:43741000"
                    }]
                },
                "entry": [],
            }

            # Add the items.
            for item_id in item_ids:
                data['entry'].append({'item': {'reference': item_id}})

            # Check for patient.
            if patient_id:

                # Format it if necessary.
                if not 'Patient' in patient_id:
                    patient_id = 'Patient/{}'.format(patient_id)

                # Add it.
                data['subject']["reference"] = patient_id

            return data

        @staticmethod
        def contract(who, signature, guardian_id=None, questionnaire_id=random.randint(0, 500),
                     patient_id=random.randint(10, 500)):

            data = {
                "resourceType": "Contract",
                "id": random.randint(0, 500),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "status": "executed",
                "issued": datetime.now().strftime('%Y-%m-%d'),
                "signer": [
                    {
                        "type": {
                            "system": "http://hl7.org/fhir/ValueSet/contract-signer-type",
                            "code": "CONSENTER",
                            "display": "Consenter"
                        },
                        "party": {
                            "reference": "Patient/{}".format(patient_id),
                        },
                        "signature": [
                            {
                                "type": [
                                    {
                                        "system": "http://hl7.org/fhir/ValueSet/signature-type",
                                        "code": "1.2.840.10065.1.12.1.7",
                                        "display": "Consent Signature"
                                    }
                                ],
                                "when": datetime.now().isoformat(),
                                "whoReference": {
                                    "reference": "Patient/{}".format(patient_id),
                                    "display": who,
                                },
                                "contentType": "text/plain",
                                "blob": base64.b64encode(signature.encode('utf-8')).decode('utf-8'),
                            }
                        ]
                    }
                ],
                "bindingReference": {
                    "reference": "QuestionnaireResponse/{}".format(questionnaire_id)
                }
            }

            # Check for a guardian.
            if guardian_id:
                # Update the party.
                data['signer'][0]['party']['reference'] = 'RelatedPerson/{}'.format(guardian_id)

                # Update who.
                data['signer'][0]['signature'][0]['whoReference']['reference'] = 'RelatedPerson/{}'.format(guardian_id)

                # Add onBehalfOf
                data['signer'][0]['signature'][0]['onBehalfOfReference'] = {
                    "reference": "Patient/{}".format(patient_id),
                    "display": "Guardian Name",
                }

            return data

        @staticmethod
        def consent(patient_id=random.randint(10, 500)):

            data = {
                "resourceType": "Consent",
                "id": random.randint(0, 500),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "status": "proposed",
                "patient": {
                    "reference": "Patient/{}".format(patient_id)
                },
                "period": {
                    "start": datetime.now().strftime('%Y-%m-%d'),
                },
                "dateTime": datetime.now().strftime('%Y-%m-%d'),
                "purpose": [
                    {
                        "system": "http://hl7.org/fhir/v3/ActReason",
                        "code": "HRESCH",
                        "display": "healthcare research"
                    }
                ],
                "except": [
                    {
                        "type": "deny",
                        "code": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "225098009",
                                "display": "Collection of sample of saliva"
                            }
                        ]
                    },
                    {
                        "type": "deny",
                        "code": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "284036006",
                                "display": "Equipment monitoring"
                            }
                        ]
                    },
                    {
                        "type": "deny",
                        "code": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "702475000",
                                "display": "Referral to clinical trial"
                            }
                        ]
                    }
                ]
            }

            return data

        @staticmethod
        def composition(contract_ids, consent_ids, patient_id=random.randint(10, 500)):

            data = {
                "resourceType": "Composition",
                "id": random.randint(0, 500),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": "2017-06-26T18:36:57.000+00:00"
                },
                "status": "final",
                "type": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "83930-8",
                            "display": "Research Consent"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/{}".format(patient_id)
                },
                "date": "2017-06-26",
                "author": [
                    {
                        "reference": "Device/consent-app"
                    }
                ],
                "title": "Signature",
                "section": [
                    {
                        "text": {
                            "status": "additional",
                            "div": "{consent text}",
                        }
                    },
                ]
            }

            # Add consents.
            for consent_id in consent_ids:
                data['section'].append({
                    "entry": [
                        {
                            "reference": "Consent/{}".format(consent_id),
                        }
                    ]
                })

            # Add contracts.
            for contract_id in contract_ids:
                data['section'].append({
                    "entry": [
                        {
                            "reference": "Contract/{}".format(contract_id),
                        }
                    ]
                })

            return data

        @staticmethod
        def bundle(resources, url='http://localhost:8080/baseDstu3'):

            # Trim leading slash on URL.
            url = url.rstrip('/')

            data = {
                "resourceType": "Bundle",
                "id": uuid.uuid4(),
                "meta": {
                    "lastUpdated": datetime.now().isoformat(),
                },
                "type": "searchset",
                "total": len(resources),
                "link": [{
                    "relation": "self",
                    "url": url,
                }],
                "entry": [],
            }

            # Add the resources.
            for resource in resources:

                # Check if already from a bundle.
                if resource.get('resourceType'):

                    # Get the id.
                    item_id = '{}/{}'.format(resource['resourceType'], resource['id'])

                    # Wrap the resource.
                    formatted_resource = {
                        "fullUrl": url + '/' + item_id,
                        "resource": resource,
                        "search": {
                            "mode": "match",
                        }
                    }

                    # Add it.
                    data['entry'].append(formatted_resource)

                else:

                    # Just add it.
                    data['entry'].append(resource)

            return data