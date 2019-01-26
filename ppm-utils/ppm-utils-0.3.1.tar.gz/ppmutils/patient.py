from enum import Enum
import requests
import json
from furl import furl
import base64
import collections
from datetime import datetime

from django.utils.safestring import mark_safe

from fhirclient.models.bundle import Bundle
from fhirclient.models.list import List
from fhirclient.models.period import Period
from fhirclient.models.fhirdate import FHIRDate

from ppmutils.ppm import PPM

import logging
logger = logging.getLogger(__name__)


class Patient:

    bundle = None
    fhir_url = None
    email = None
    project = None
    includes = None
    request = None

    # Set the types of consent possible
    class Consent(Enum):
        Individual = 'individual'
        Guardian = 'guardian'

    def __init__(self, fhir_url, email, project, includes=[], request=None):

        # Retain the request
        self.fhir_url = fhir_url
        self.email = email
        self.project = project
        self.request = request
        self.includes = includes

        # Ensure project is valid
        try:
            self.project = PPM.Project(project)
        except ValueError:
            raise Patient.InvalidProjectError

        # Make the query
        self._query(includes)

    @classmethod
    def from_request(cls, fhir_url, request, includes=[]):

        # Retain the request
        return cls(fhir_url=fhir_url,
                   email=request.user.email,
                   project=request.user.participant.project,
                   includes=includes,
                   request=request)

    def _query(self, includes):

        # Set the url
        patient_url = furl(self.fhir_url)
        patient_url.path.segments.append('Patient')
        patient_url.query.params.add('identifier', 'http://schema.org/email|' + self.email)

        # Include needed resources
        url = self._include_queries(patient_url, includes)

        try:
            # Get it
            response = requests.get(url.url)
            response.raise_for_status()

            # Retain response and build bundle
            self.bundle_json = response.json()
            self.bundle = Bundle(self.bundle_json)

            # Check for empty
            if self.bundle.total == 0:
                raise Patient.MissingError

        except requests.HTTPError:
            raise Patient.ServerError

    def __str__(self):

        # Return the FHIR ID
        return self.ppm_id

    class ServerError(Exception):
        pass

    class MissingError(Exception):
        pass

    class ResourceMissingError(Exception):
        pass

    class InvalidProjectError(Exception):
        pass

    @staticmethod
    def _include_queries(url, includes):
        '''
        Accepts a list of FHIR resources and updates the URL to include them
        in the query.
        :param url: The Patient query furl object
        :param includes: A list of FHIR resource types
        :return: furl
        '''

        # Add resource inclusions
        for include in includes:

            # Check the include and format the query
            if include == '*':
                url.query.params.add('_include', '*')
                url.query.params.add('_revinclude', '*')

            elif include == 'Flag':
                url.query.params.add('_revinclude', 'Flag:patient')

            elif include == 'QuestionnaireResponse':
                url.query.params.add('_revinclude', 'QuestionnaireResponse:source')

            elif include == 'Questionnaire':
                # TODO: Figure this out
                pass

            elif include == 'Questionnaire':
                # TODO: Figure this out
                pass

            elif include == 'Questionnaire':
                # TODO: Figure this out
                pass

            else:
                logger.error('Patient error: Unhandled include: {}'.format(include),
                             extra={'includes': includes})

        return url

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

    def _query_resource(self, resource_type, query={}):
        """
        This method will fetch a resource for a given type.
        :param resource: FHIR resource type
        :type resource: str
        :param query: A dict of key value pairs for searching resources
        :type query: dict
        :return: A FHIR Bundle of the results
        :rtype: Bundle
        """

        # Build the URL.
        url_builder = furl(self.fhir_url)
        url_builder.path.add(resource_type)

        # Add queries
        for key, value in query.items():
            url_builder.query.params.add(key, value)

        # Make the request.
        response = requests.get(url_builder.url)
        response.raise_for_status()

        return Bundle(response.json())

    def output_all(self):

        # Get general
        patient = self.output_patient()
        patient['project'] = self.project.value
        patient['date_registered'] = self.request.user.date_joined.strftime('%m/%d/%Y')

        # Add enrollment
        patient['enrollment'] = self.output_enrollment().get('enrollment')
        patient['enrollment_accepted_date'] = self.output_enrollment().get('start', '')

        # Add composition
        patient['composition'] = self.output_composition()

        # Add consent quiz is ASD
        if self.project is PPM.Project.ASD:

            patient['consent_quiz'] = self.output_questionnaire_response(self.get_consent_questionnaire_id())

        # Add consent
        patient['questionnaire'] = self.output_questionnaire_response(self.get_questionnaire_id())

        # Add points of care
        patient['points_of_care'] = self.output_points_of_care()

        # Add research studies
        patient['research_studies'] = self.output_research_studies()

        return patient

    def get_id(self):

        # Get the patient
        resource = next(resource['resource'] for resource in self.bundle_json['entry']
                        if resource['resource']['resourceType'] == 'Patient')

        if not resource:
            raise Patient.MissingError

        # Return the FHIR ID
        return resource.get('id')

    @property
    def ppm_id(self):
        return self.get_id()

    def get_patient(self):
        '''
        Finds the Patient resource and returns it. Throws ResourceMissingError if not found.
        :return: Patient
        '''

        # Get the patient
        resource = self._find_first_resource('Patient')
        if not resource:
            raise Patient.MissingError

        return resource

    def output_patient(self):
        '''
        Returns a dict of primary properties of the Patient e.g. first name, last name, address, etc
        :return: dict
        '''

        # Get the patient as a JSON dict
        try:
            patient = self.get_patient().as_json()

            # Collect properties
            output = dict()

            # Get email and FHIR ID
            output["email"] = self._get_or(patient, ['identifier', 0, 'value'])
            output["fhir_id"] = patient['id']
            if not output['email']:
                logger.error('Patient email could not be found: {}'.format(patient['id']))
                return {}

            # Get the remaining optional properties
            output["firstname"] = self._get_or(patient, ['name', 0, 'given', 0], '')
            output["lastname"] = self._get_or(patient, ['name', 0, 'family'], '')
            output["street_address1"] = self._get_or(patient, ['address', 0, 'line', 0], '')
            output["street_address2"] = self._get_or(patient, ['address', 0, 'line', 1], '')
            output["city"] = self._get_or(patient, ['address', 0, 'city'], '')
            output["state"] = self._get_or(patient, ['address', 0, 'state'], '')
            output["zip"] = self._get_or(patient, ['address', 0, 'postalCode'], '')
            output["phone"] = self._get_or(patient, ['telecom', 0, 'postalCode'], '')

            # Parse telecom properties
            output['phone'] = next((telecom.get('value', '') for telecom in patient.get('telecom', [])
                                    if telecom.get('system') == 'phone'), '')
            output['twitter_handle'] = next((telecom.get('value', '') for telecom in patient.get('telecom', [])
                                             if telecom.get('system') == 'other'), '')
            output['contact_email'] = next((telecom.get('value', '') for telecom in patient.get('telecom', [])
                                            if telecom.get('system') == 'email'), '')

            # Get how they heard about PPM
            output['how_did_you_hear_about_us'] = next((extension.get('valueString', '') for extension in
                                                        patient.get('extension', []) if 'how-did-you-hear-about-us'
                                                        in extension.get('url')), '')

            # Get their Twitter usage flag, assume they're using it unless we've saved an extension saying otherwise
            output['uses_twitter'] = next((extension.get('valueBoolean', False) for extension in
                                           patient.get('extension', []) if 'uses-twitter'
                                           in extension.get('url')), True)

            return output

        except Patient.MissingError:
            logger.debug('Patient not found')

        except Exception as e:
            logger.exception('Patient error: {}'.format(e), exc_info=True, extra={'ppm_id': self.ppm_id})

        return None

    def get_enrollment(self):
        '''
        Finds and returns the enrollment Flag resource. Raises ResourceMissingError if not found.
        :return: Flag
        '''

        # Get the patient
        resource = self._find_first_resource('Flag')
        if not resource:
            raise Patient.ResourceMissingError

        return resource

    def output_enrollment(self):
        '''
        Returns a dict of primary enrollment information
        :return: dict
        '''

        # Get the flag
        try:
            flag = self.get_enrollment().as_json()

            # Get the resource.
            output = dict()

            # Try and get the values
            output['enrollment'] = self._get_or(flag, ['code', 'coding', 0, 'code'])
            output['status'] = self._get_or(flag, ['status'])
            output['start'] = self._get_or(flag, ['period', 'start'])
            output['end'] = self._get_or(flag, ['period', 'end'])

            return output

        except Patient.ResourceMissingError:
            logger.debug('Flag not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return {}

    def get_consent(self):
        '''
        Finds and returns the Consent resource. Raises ResourceMissingError if not found.
        :return: Consent
        '''

        # Get the patient
        resource = self._find_first_resource('Consent')
        if not resource:
            raise Patient.ResourceMissingError

        return resource

    def output_consent(self):

        # Get consents
        try:
            consent = self.get_consent()

            # Output the date signed
            output = {'date': consent.dateTime.origval}

            return output

        except Patient.ResourceMissingError:
            logger.debug('Consent not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return {}

    def get_contracts(self):
        '''
        Finds and returns the Contract resources. Raises ResourceMissingError if not found.
        :return: Contract
        '''

        # Get the patient
        resources = self._find_resources('Contract')
        if not resources:
            raise Patient.ResourceMissingError

        return resources

    def get_contract(self, keys, value):
        '''
        Finds the Contract resource and returns the one matching the query. Raises ResourceMissingError if not found.
        :param keys: A list of keys/indices for path to the value to compare to
        :param value: The value to compare
        :return: Contract
        '''

        contracts = self._find_resources('Contract')
        if not contracts:
            raise Patient.ResourceMissingError

        # Compare them
        for contract in contracts:

            # Get the value
            contract_value = self._get_or(contract.as_json(), keys)

            # Compare and return
            if contract_value == value:

                return contract

        # Return None if none found
        return None

    def output_contracts(self):
        '''
        Returns a list of dicts of primary Contract information
        :return: list
        '''

        # Get contract
        try:
            contracts = self.get_contracts()

            # Collect dicts of properties
            output = list()

            # Loop through contracts
            for contract in contracts:

                # Output the date issued
                output.append({
                    'date': contract.issued.origval
                })

            return output

        except Patient.ResourceMissingError:
            logger.debug('Contracts not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return []

    def get_composition(self, keys, value):
        '''
        Finds the Composition resource and returns the one matching the query. Raises ResourceMissingError if not found.
        :param keys: A list of keys/indices for path to the value to compare to
        :param value: The value to compare
        :return: Composition
        '''

        compositions = self._find_resources('Composition')
        if not compositions:
            raise Patient.ResourceMissingError

        # Compare them
        for composition in compositions:

            # Get the value
            composition_value = self._get_or(composition.as_json(), keys)

            # Compare and return
            if composition_value == value:

                return composition

        # Return None if none found
        return None

    def get_compositions(self):
        '''
        Finds the Composition resources and returns all of them. Raises ResourceMissingError if not found.
        :return: [Composition]
        '''

        compositions = self._find_resources('Composition')
        if not compositions:
            raise Patient.ResourceMissingError

        return compositions

    def output_composition(self):
        '''
        Returns a dict of primary consent composition information
        :return: dict
        '''

        # Get composition(s)
        try:
            compositions = self.get_compositions()

            # Get the consent type
            consent_type = self.get_consent_type()
            if consent_type == Patient.Consent.Individual:

                # We only care about one composition
                composition = next(iter(compositions))

                # Get consent
                consent = self.get_consent()

                # Find the contract, composition and signature questionnaire response
                contract = next(iter(self.get_contracts()))

                # Get the signature questionnaire ID
                questionnaire_id = self.get_signature_questionnaire_id()

                # Get the consent text from the composition
                text = next(section.text.div for section in composition.section if section.text is not None)

                # Get exceptions
                exceptions = self.output_consent_exceptions(questionnaire_id)

                # Return the dict
                record = {
                    'type': consent_type.value.upper(),
                    'date_signed': consent.dateTime.origval,
                    'signer_signature': base64.b64decode(contract.signer[0].signature[0].blob),
                    'participant_name': contract.signer[0].signature[0].whoReference.display,
                    'consent_text': text,
                    'exceptions': exceptions,
                    'consent_questionnaires': [{
                        'template': 'dashboard/consent/{}.html'.format(questionnaire_id),
                        'questions': self.output_signature_questionnaire_response(questionnaire_id),
                    }]
                }

                return record

            elif consent_type == Patient.Consent.Guardian:

                # Get consent
                consent = next(iter(self._find_resources('Consent')), None)
                if not consent:
                    logger.exception('Patient error: No composition in bundle', extra={'ppm_id': self.ppm_id})
                    raise Patient.ResourceMissingError

                # Find the contracts, composition and signature questionnaire response
                contracts = self._find_resources('Contract')
                if not contracts:
                    raise Patient.ResourceMissingError

                # Get the guardian signature response
                guardian_questionnaire_response = next(qr for qr in self._find_resources('QuestionnaireResponse')
                                                       if qr.questionnaire.reference ==
                                                       'Questionnaire/guardian-signature-part-1')

                # Get the ward's signature response
                ward_questionnaire_response = next(qr for qr in self._find_resources('QuestionnaireResponse')
                                                   if qr.questionnaire.reference ==
                                                   'Questionnaire/guardian-signature-part-3')

                # Get the explained reason questionnaire
                explained_questionnaire_response = next(qr for qr in self._find_resources('QuestionnaireResponse')
                                                        if qr.questionnaire.reference ==
                                                        'Questionnaire/guardian-signature-part-2')
                explained = next(item.answer[0].valueString for item in explained_questionnaire_response.item
                                 if item.linkId == 'question-1').title()
                explained_reason = next((item.answer[0].valueString for item in explained_questionnaire_response.item
                                        if item.linkId == 'question-1-1'), None)

                # Get the explained contract
                explained_contract = next(contract for contract in self._find_resources('Contract')
                                          if contract.bindingReference.reference == 'QuestionnaireResponse/{}'
                                          .format(explained_questionnaire_response.id))
                # Split them out
                signer_contract = next(contract for contract in contracts if contract.bindingReference.reference ==
                                       'QuestionnaireResponse/{}'.format(guardian_questionnaire_response.id))
                assent_contract = next(contract for contract in contracts if contract.bindingReference.reference ==
                                       'QuestionnaireResponse/{}'.format(ward_questionnaire_response.id))

                # Find the contracts, composition and signature questionnaire response
                signer = next(iter(self._find_resources('RelatedPerson')), None)
                if not signer:
                    raise Patient.ResourceMissingError

                compositions = self._find_resources('Composition')
                if not compositions:
                    raise Patient.ResourceMissingError

                # Determine comps
                signer_composition = next(composition for composition in compositions if len(composition.section) > 2)
                assent_composition = next(composition for composition in compositions if len(composition.section) == 2)

                # Get the consent and assent text from the composition
                consent_text = next(section.text.div for section in signer_composition.section if section.text is not None)
                assent_text = next(section.text.div for section in assent_composition.section if section.text is not None)

                # Return the dict
                record = {
                    'type': consent_type.value.upper(),
                    'date_signed': consent.dateTime.origval,
                    'signer_name': signer.name[0].text,
                    'signer_signature': base64.b64decode(signer_contract.signer[0].signature[0].blob),
                    'participant_name': signer_contract.signer[0].signature[0].onBehalfOfReference.display,
                    'consent_text': consent_text,
                    'exceptions': self.output_consent_exceptions('guardian-signature-part-1'),
                    'signer_relationship': signer.relationship.text,
                    'participant_acknowledgement': explained,
                    'participant_acknowledgement_reason': explained_reason,
                    'explained_signature': base64.b64decode(explained_contract.signer[0].signature[0].blob),
                    'assent_signature': base64.b64decode(assent_contract.signer[0].signature[0].blob),
                    'assent_date': assent_contract.issued.origval,
                    'assent_exceptions': self.output_consent_exceptions('guardian-signature-part-3'),
                    'assent_text': assent_text,
                    'consent_questionnaires': [
                        {
                            'template': 'dashboard/consent/guardian-signature-part-1.html',
                            'questions': self.output_signature_questionnaire_response('guardian-signature-part-1'),
                        },
                        {
                            'template': 'dashboard/consent/guardian-signature-part-2.html',
                            'questions': self.output_signature_questionnaire_response('guardian-signature-part-2'),
                        }
                    ],
                    'assent_questionnaires': [
                        {
                            'template': 'dashboard/consent/guardian-signature-part-3.html',
                            'questions': self.output_signature_questionnaire_response('guardian-signature-part-3'),
                        }
                    ],
                }

                return record

        except Patient.ResourceMissingError:
            logger.debug('Composition not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return {}

    def output_consent_exceptions(self, questionnaire_id):
        '''
        Parses the QuestionnaireResponse for the given Consent Questionnaire and
        returns a list of the formatted exceptions
        :param questionnaire_id: Questionnaire ID
        :return: list
        '''

        try:
            # Get the questionnaire and questionnaire response
            questionnaire = self.get_questionnaire(questionnaire_id)
            questionnaire_response = self.get_questionnaire_response(questionnaire_id)

            # Process items
            exceptions = []
            for item in questionnaire_response.item:

                # Check if this exception was toggled
                if item.answer[0].valueBoolean:

                    # Get the question text from the Questionnaire and format it
                    question = next(question for question in questionnaire.item if question.linkId == item.linkId)
                    exceptions.append(self._format_consent_exception(question.text))

            return exceptions

        except Patient.ResourceMissingError:
            logger.debug('Consent exceptions not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return []

    def output_signature_questionnaire_response(self, questionnaire_id):
        '''
        Parses the QuestionnaireResponse for the given Questionnaire and
        returns a list of the questions and answers
        :param questionnaire_id: Questionnaire ID
        :return: list
        '''

        try:
            # Get the questionnaire and questionnaire response
            questionnaire = self.get_questionnaire(questionnaire_id)
            questionnaire_response = self.get_questionnaire_response(questionnaire_id)

            # Process items
            questions = []
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

                                # At this point it is assumed this is the explained question
                                question_object['yes'] = item.text

                                # We have to hardcode this as it's not specified in the FHIR resource
                                question_object['no'] = 'I was not able to explain this study to my child or ' \
                                                        'individual in my care who will be participating'
                                question_object['answer'] = response.answer[0].valueString is 'yes'

                # Add it.
                questions.append(question_object)

            return questions

        except Patient.ResourceMissingError:
            logger.debug('Composition not found')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return []

    def get_questionnaire(self, questionnaire_id):
        '''
        Returns the Questionnaire resource
        :return:
        '''

        # Ensure the bundle isn't empty
        if self.bundle.total == 0:
            raise Patient.MissingError

        # Pick out the questionnaire and return it
        return next((entry.resource for entry in self.bundle.entry if entry.resource.id == questionnaire_id), None)

    def get_questionnaire_response(self, questionnaire_id):
        '''
        Returns a QuestionnaireResponse resource
        :return:
        '''

        # Ensure the bundle isn't empty
        if self.bundle.total == 0:
            raise Patient.MissingError

        # Pick out the questionnaire and its response
        questionnaire_response = next((entry.resource for entry in self.bundle.entry if
                                       entry.resource.resource_type == 'QuestionnaireResponse' and
                                       entry.resource.questionnaire.reference ==
                                       'Questionnaire/{}'.format(questionnaire_id)), None)

        # Check for missing
        if not questionnaire_response:
            raise Patient.ResourceMissingError

        return questionnaire_response

    def output_questionnaire_response(self, questionnaire_id):
        '''
        Returns a dict of questions and the Patient's responses
        :return:
        '''

        try:
            # Pick out the questionnaire and its response
            questionnaire = self.get_questionnaire(questionnaire_id)
            questionnaire_response = self.get_questionnaire_response(questionnaire_id)

            # Get questions and answers
            questions = self._questions(questionnaire.item)
            answers = self._answers(questionnaire_response.item)

            # Process sub-questions first
            for linkId, condition in {linkId: condition for linkId, condition in questions.items() if type(condition) is dict}.items():

                try:
                    # Assume only one condition, fetch the parent question linkId
                    parent = next(iter(condition), None)
                    if not parent:
                        logger.warning('Patient Error: Subquestion not properly specified: {}:{}'.format(linkId, condition),
                                       extra={'questionnaire': questionnaire_id, 'ppm_id': questionnaire_response.source,
                                              'questionnaire_response': questionnaire_response.id})
                        continue

                    if len(condition) > 1:
                        logger.warning('Patient Error: Subquestion has multiple conditions: {}:{}'.format(linkId, condition),
                                       extra={'questionnaire': questionnaire_id, 'ppm_id': questionnaire_response.source,
                                              'questionnaire_response': questionnaire_response.id})

                    # Ensure they've answered this one
                    if not condition[parent] in answers.get(parent):
                        continue

                    # Get the question and answer item
                    answer = answers[parent]
                    index = answer.index(condition[parent])

                    # Check for commas
                    sub_answers = answers[linkId]
                    if ',' in next(iter(sub_answers), None):

                        # Split it
                        sub_answers = [sub.strip() for sub in next(iter(sub_answers)).split(',')]

                    # Format them
                    value = '{} <span class="label label-primary">{}</span>'.format(
                        answer[index], '</span>&nbsp;<span class="label label-primary">'.join(sub_answers))

                    # Append the value
                    answer[index] = mark_safe(value)

                except Exception as e:
                    logger.exception('Patient error: {}'.format(e), exc_info=True,
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
                    logger.warning(f'Patient Error: No answer found for {linkId}',
                                   extra={'questionnaire': questionnaire_id, 'link_id': linkId,
                                          'ppm_id': questionnaire_response.source})
                    continue

                # Format the question text
                text = '{}. {}'.format(len(response.keys()) + 1, question)

                # Add the answer
                response[text] = answer

            return response

        except Patient.ResourceMissingError:
            logger.debug('Questionnaire response missing: {}'.format(questionnaire_id))

        except Patient.MissingError:
            logger.debug('Patient missing')

        return {}

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
                sub_questions = Patient._questions(item.item)

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
                    sub_questions = Patient._questions(item.item)

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
                logger.error('Patient questionnaire error: Missing items for question', extra={'link_id': item.linkId})
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
                sub_answers = Patient._answers(item.item)

                # Add them
                responses[item.linkId].extend(sub_answers)

        return responses

    def get_signature_questionnaire_id(self):
        '''
        Returns the questionnaire ID for the current Patient
        :return: str
        '''

        # Check project
        if self.project == PPM.Project.NEER:
            return 'neer-signature'
        elif self.project == PPM.Project.ASD and self.get_consent_type() == Patient.Consent.Individual:
            return 'individual-signature-part-1'
        elif self.project == PPM.Project.ASD and self.get_consent_type() == Patient.Consent.Guardian:
            return 'guardian-signature-part-1'
        else:
            raise Patient.InvalidProjectError

    def get_questionnaire_id(self):
        '''
        Returns the questionnaire ID for the current Patient
        :return: str
        '''

        # Check project
        if self.project == PPM.Project.NEER:
            return 'ppm-neer-registration-questionnaire'
        elif self.project == PPM.Project.ASD:
            return 'ppm-asd-questionnaire'
        else:
            raise Patient.InvalidProjectError

    def get_consent_questionnaire_id(self):
        '''
        Returns the consent quiz questionnaire ID for the current Patient
        :return: str
        '''

        # Check project
        if self.project == PPM.Project.NEER:
            return None

        elif self.project == PPM.Project.ASD:

            # Get the consent type
            consent_type = self.get_consent_type()

            # Check it
            if consent_type == Patient.Consent.Individual:
                return 'ppm-asd-consent-individual-quiz'
            elif consent_type == Patient.Consent.Guardian:
                return 'ppm-asd-consent-guardian-quiz'

    def get_consent_type(self):
        '''
        Returns the type of consent this Patient submitted
        :return: Patient.Consent
        '''

        # Check project
        if self.project == PPM.Project.NEER:
            return Patient.Consent.Individual

        elif self.project == PPM.Project.ASD:

            # Check the type of patient, individuals have one comp, dependents have two
            compositions = len([entry.resource for entry in self.bundle.entry
                            if entry.resource.resource_type == 'Composition'])
            # Not yet consented, we don't know
            if compositions == 0:
                return None
            # Individual
            elif compositions == 1:
                return Patient.Consent.Individual
            else:
                return Patient.Consent.Guardian

    @staticmethod
    def _format_consent_exception(display):

        # Check the various exception display values
        if 'equipment monitoring' in display.lower() or 'fitbit' in display.lower():
            return mark_safe('Fitbit monitoring')

        elif 'referral to clinical trial' in display.lower() or 'additional questionnaires' in display.lower():
            return mark_safe('Future contact/questionnaires')

        elif 'saliva' in display.lower():
            return mark_safe('Saliva sample')

        elif 'blood sample' in display.lower():
            return mark_safe('Blood sample')

        elif 'stool sample' in display.lower():
            return mark_safe('Stool sample')

        elif 'tumor' in display.lower():
            return mark_safe('Tumor tissue samples')

        else:
            logger.warning('Could not format exception: {}'.format(display))
            return display

    def _find_resource(self, resource_type, id):
        '''
        Searches through a bundle for the resource matching the given resourceType and ID
        :return FHIR Resource object
        '''

        # Get matching resources
        resources = [entry.resource for entry in self.bundle.entry if entry.resource.resource_type == resource_type]

        # Match
        for resource in resources:

            # Check ID
            if resource.id == id:
                return resource

        return None

    def _find_resources(self, resource_type):
        '''
        Searches through a bundle for the resources matching the given resourceType
        :return list
        '''

        # Get matching resources
        return [entry.resource for entry in self.bundle.entry if entry.resource.resource_type == resource_type]

    def _find_first_resource(self, resource_type):
        '''
        Searches through a bundle for the resources matching the given resourceType and returns the first one
        :return FHIRResource
        '''

        # Get matching resources
        return next((entry.resource for entry in self.bundle.entry
                     if entry.resource.resource_type == resource_type), None)

    def _get_list(self, resource_type):
        '''
        Finds the List resource for the given resource type. Raises ResourceMissing error if none found.
        :param resource_type: The FHIR resource too referenced by the List
        :type resource_type: str
        :return: The FHIR List resource
        :rtype: List
        '''

        # Get lists
        lists = [entry.resource for entry in self.bundle.entry if entry.resource.resource_type == 'List']
        if not lists:
            raise Patient.ResourceMissingError

        # Check each list's reference resources
        for resource_list in lists:

            # Compare the type
            for item in [entry.item for entry in resource_list.entry]:

                # Check for a reference
                if item.reference and resource_type == item.reference.split('/')[0]:

                    return resource_list

        else:
            logger.error('Unhandled list resource type: {}'.format(resource_type))
            raise Patient.ResourceMissingError

    def update_enrollment(self):
        '''
        Assesses the current Patient's state and checks if an enrollment status update is needed. If so,
        the Patient's Flag resource is updated.
        '''

        # Get enrollment
        enrollment = PPM.Enrollment(self.output_enrollment().get('enrollment'))

        # Compare states
        if enrollment is PPM.Enrollment.Registered and self.has_completed(PPM.Enrollment.Consented):

            # Update
            self._update_flag(PPM.Enrollment.Consented)

        elif enrollment is PPM.Enrollment.Consented and self.has_completed(PPM.Enrollment.Proposed):

            # Update
            self._update_flag(PPM.Enrollment.Proposed)

        elif enrollment is PPM.Enrollment.Proposed and self.has_completed(PPM.Enrollment.Accepted):

            # Update
            self._update_flag(PPM.Enrollment.Accepted)

    def _update_flag(self, enrollment):
        '''
        Updates the Patient's enrollment flag with the given status
        :param enrollment: The enrollment status
        :type enrollment: PPM.Enrollment
        :return: None
        '''
        # Get the flag
        flag = next(iter(self._find_resources('Flag')), None)
        if not flag:
            logger.warning('FHIR Error: Flag does not already exist for Patient/{}'.format(self.ppm_id),
                           extra={'enrollment': enrollment})
            raise Patient.ResourceMissingError

        content = None
        try:
            # Get the status value
            status = enrollment.value
            logger.debug("Patient: {}, Status: {}".format(self, status))

            # Get the first and only flag.
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
            flag_url = furl(self.fhir_url)
            flag_url.path.segments.extend(['Flag', flag.id])

            logger.debug('Updating Flag "{}" with code: "{}"'.format(flag_url.url, status))

            # Post it.
            response = requests.put(flag_url.url, json=flag.as_json())
            content = response.content
            response.raise_for_status()

            return flag

        except requests.HTTPError as e:
            logger.exception('FHIR Connection Error: {}'.format(e), exc_info=True,
                             extra={'response': content, 'ppm_id': self.ppm_id, 'status': enrollment.value})
            raise

        except Exception as e:
            logger.exception('FHIR error: {}'.format(e), exc_info=True, extra={'ppm_id': self.ppm_id})
            raise

    def has_completed(self, status):
        '''
        Checks the current participant to see if they've completed the steps necessary for the given enrollment
        status. Returns yes or not depending.
        :param status: The enrollment status
        :type status: PPM.Enrollment
        :return: True or False
        :rtype: bool
        '''

        # Check enrollment status
        if status is PPM.Enrollment.Registered:

            # If this Patient object exists, they've registered
            return True

        elif status is PPM.Enrollment.Consented:

            # Check for a consent object
            try:
                consent = self.get_consent()
                return consent is not None

            except Patient.ResourceMissingError:
                return False

        elif status is PPM.Enrollment.Proposed:

            try:
                # Check project
                if self.project is PPM.Project.NEER:

                    # Check for a questionnaire response
                    try:
                        questionnaire_response = self.get_questionnaire_response(self.get_questionnaire_id())
                        return questionnaire_response is not None

                    except Patient.ResourceMissingError:
                        return False

                elif self.project is PPM.Project.ASD:

                    # Check for points of care
                    try:
                        points_of_care = self.get_points_of_care()
                        return points_of_care is not None

                    except Patient.ResourceMissingError:
                        return False

            except Patient.ResourceMissingError:
                return False

        elif status is PPM.Enrollment.Accepted:

            # Get the flag and check
            flag = self.output_enrollment()
            return flag and flag.get('enrollment') == PPM.Enrollment.Accepted.value

        elif status is PPM.Enrollment.Ineligible:

            # Get the flag and check
            flag = self.output_enrollment()
            return flag and flag.get('enrollment') == PPM.Enrollment.Ineligible.value

    def get_points_of_care(self):
        '''
        Returns the list of Organization names, if any, submitted by the user as their points of care
        :return: List of points of care
        :rtype: list
        '''

        # Get the list
        points_of_care_list = self._get_list('Organization')

        # Get the references
        references = [entry.item.reference for entry in points_of_care_list.entry if entry.item.reference]

        # Find it in the bundle
        resources = [entry.resource for entry in self.bundle.entry if '{}/{}'.format('Organization', entry.resource.id)
                     in references]
        if not resources:
            raise Patient.ResourceMissingError

        # Return Organization names
        return resources

    def output_points_of_care(self):
        '''
        Returns the list of Organization names, if any, submitted by the user as their points of care
        :return: List of str
        :rtype: list
        '''

        try:
            # Get the list
            points_of_care = self.get_points_of_care()

            # Return Organization names
            return [organization.name for organization in points_of_care]

        except Patient.ResourceMissingError:
            logger.debug('Points of care missing')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return []

    def get_research_subjects(self):
        '''
        Returns the list of Research Study references, if any, submitted by the user as their clinical trials
        :return: List of research studies
        :rtype: list
        '''

        # Return the list of ResearchSubjects
        return self._find_resources('ResearchSubject')

    def get_research_studies(self):
        '''
        Returns the list of Research Study references, if any, submitted by the user as their clinical trials
        :return: List of research studies
        :rtype: list
        '''

        # Get the subject list
        research_subjects = self.get_research_subjects()
        if not research_subjects:
            raise Patient.ResourceMissingError

        # Build a query
        ids = [subject.study.reference.split('/')[-1] for subject in research_subjects]

        # Query the studies
        bundle = self._query_resource('ResearchStudy', query={'_id': ','.join(ids)})

        return bundle.entry

    def output_research_studies(self):
        '''
        Returns the list of Research Study titles, if any, submitted by the user as their clinical trials
        :return: List of research studies
        :rtype: list
        '''

        try:
            # Get the subject list
            research_studies = self.get_research_studies()

            # Get their titles
            titles = [research_study.resource.title for research_study in research_studies]

            # Return the list of Organizations
            return titles

        except Patient.ResourceMissingError:
            logger.debug('Research studies missing')

        except Patient.MissingError:
            logger.debug('Patient missing')

        return []

    def has_registered(self):
        '''
        A safe method simply to check for registration
        :return: True or False
        :rtype: bool
        '''

        # This is automatically assumed if this object exists
        return True

    def has_points_of_care(self):
        '''
        A safe method simply to check for the existence of points of care
        :return: True or False
        :rtype: bool
        '''

        try:
            points_of_care = self.get_points_of_care()

            return len(points_of_care) > 0

        except Patient.ResourceMissingError:
            return False

    def has_research_studies(self):
        '''
        A safe method simply to check for the existence of research studies
        :return: True or False
        :rtype: bool
        '''

        try:
            # Presence of research subject resources indicates existence of research studies
            research_subjects = self.get_research_subjects()

            return len(research_subjects) > 0

        except Patient.ResourceMissingError:
            return False

    def has_consent(self):
        '''
        A safe method simply to check for the existence of a consent
        :return: True or False
        :rtype: bool
        '''

        try:
            consent = self.output_consent()

            return consent and consent.get('date') is not None

        except Patient.ResourceMissingError:
            return False

    def has_questionnaire_response(self):
        '''
        A safe method simply to check for the existence of a questionnaire response
        :return: True or False
        :rtype: bool
        '''

        try:
            # Get the response for the Questionnaire dependent on project
            questionnaire_response = self.get_questionnaire_response(self.get_questionnaire_id())

            return questionnaire_response is not None

        except Patient.ResourceMissingError:
            return False


    ####################################################################################################
    ####################################################################################################
    ## Updates
    ####################################################################################################
    ####################################################################################################

    @staticmethod
    def set_twitter(fhir_url, email, handle=None):
        logger.debug('Twitter handle: {}'.format(handle))

        try:
            # Fetch the Patient.
            url = furl(fhir_url)
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
                # Add an extension indicating no Twitter
                extension = {
                        'url': 'https://p2m2.dbmi.hms.harvard.edu/fhir/StructureDefinition/uses-twitter',
                        'valueBoolean': False
                    }

                # Add it to their extensions
                patient.setdefault('extension', []).append(extension)

            # Save
            url.query.params.clear()
            url.path.segments.append(patient['id'])
            response = requests.put(url.url, data=json.dumps(patient))
            response.raise_for_status()

            return response.ok

        except Exception as e:
            logger.error('FHIR Error: {}'.format(e), extra={'ppm_id': patient.get('id'), 'email': email})

        return False


    ####################################################################################################
    ####################################################################################################
    ## Deletes
    ####################################################################################################
    ####################################################################################################

    def delete_consent(self):
        logger.debug('Deleting consents: Patient/{}'.format(self))

        # Build the transaction
        transaction = {
            'resourceType': 'Bundle',
            'type': 'transaction',
            'entry': []
        }

        # Add the composition delete
        transaction['entry'].append({
            'request': {
                'url': 'Composition?subject=Patient/{}'.format(self.ppm_id),
                'method': 'DELETE',
            }
        })

        # Add the consent delete
        transaction['entry'].append({
            'request': {
                'url': 'Consent?patient=Patient/{}'.format(self.ppm_id),
                'method': 'DELETE',
            }
        })

        # Add the contract delete
        transaction['entry'].append({
            'request': {
                'url': 'Contract?signer=Patient/{}'.format(self.ppm_id),
                'method': 'DELETE',
            }
        })

        # Check project
        if self.project == PPM.Project.ASD:

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
                            .format(questionnaire_id, self.ppm_id),
                        'method': 'DELETE',
                    }
                })

            # Add the contract delete
            transaction['entry'].append({
                'request': {
                    'url': 'Contract?signer.patient={}'.format(self.ppm_id),
                    'method': 'DELETE',
                }
            })

            # Remove related persons
            transaction['entry'].append({
                'request': {
                    'url': 'RelatedPerson?patient=Patient/{}'.format(self.ppm_id),
                    'method': 'DELETE',
                }
            })

        elif self.project == PPM.Project.NEER:

            # Delete questionnaire responses
            questionnaire_id = 'neer-signature'
            transaction['entry'].append({
                'request': {
                    'url': 'QuestionnaireResponse?questionnaire=Questionnaire/{}&source=Patient/{}'
                        .format(questionnaire_id, self.ppm_id),
                    'method': 'DELETE',
                }
            })

        else:
            logger.error('Unsupported project: {}'.format(self.project), extra={'ppm_id': self.ppm_id})

        # Make the FHIR request.
        response = requests.post(self.fhir_url, headers={'content-type': 'application/json'},
                                 data=json.dumps(transaction))
        response.raise_for_status()