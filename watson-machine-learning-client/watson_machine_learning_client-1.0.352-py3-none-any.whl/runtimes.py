################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
import json
from watson_machine_learning_client.utils import INSTANCE_DETAILS_TYPE, RUNTIME_SPEC_DETAILS_TYPE, MODEL_DETAILS_TYPE, LIBRARY_DETAILS_TYPE, FUNCTION_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, get_type_of_details, docstring_parameter, str_type_conv, print_text_header_h2
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.metanames import RuntimeMetaNames, LibraryMetaNames
from repository_v3.mlrepositoryartifact import MLRepositoryArtifact
from repository_v3.mlrepository import MetaProps, MetaNames


def LibraryDefinition(name, version, filepath, description=None, platform=None):
    WMLResource._validate_type(name, 'name', STR_TYPE, True)
    WMLResource._validate_type(version, 'version', STR_TYPE, True)
    WMLResource._validate_type(platform, 'platform', dict, False)
    WMLResource._validate_type(description, 'description', STR_TYPE, False)
    WMLResource._validate_type(filepath, 'filepath', STR_TYPE, True)

    definition = {
        'name': name,
        'version': version,
        'filepath': filepath
    }

    if description is not None:
        definition['description'] = description

    if platform is not None:
        definition['platform'] = platform

    return definition


class Runtimes(WMLResource):
    """
        Creates Runtime Specs and associated Custom Libraries.
    """
    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Runtimes._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Runtimes._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self.ConfigurationMetaNames = RuntimeMetaNames()
        self.LibraryMetaNames = LibraryMetaNames()
        self._ICP = client.ICP

    def _create_library_from_definition(self, definition, runtime_definition):
        self._validate_meta_prop(definition, 'name', STR_TYPE, True)
        self._validate_meta_prop(definition, 'version', STR_TYPE, True)
        self._validate_meta_prop(definition, 'platform', dict, False)
        self._validate_meta_prop(definition, 'description', STR_TYPE, False)
        self._validate_meta_prop(definition, 'filepath', STR_TYPE, True)

        lib_metadata = {
            self.LibraryMetaNames.NAME: definition['name'],
            self.LibraryMetaNames.VERSION: definition['version'],
            self.LibraryMetaNames.PLATFORM:
                definition['platform']
                if 'platform' in definition and definition['platform'] is not None
                else {
                    "name": runtime_definition[self.ConfigurationMetaNames.PLATFORM]['name'],
                    "versions": [runtime_definition[self.ConfigurationMetaNames.PLATFORM]['version']]
                },
            self.LibraryMetaNames.FILEPATH: definition['filepath']
        }

        if 'description' in definition:
            lib_metadata[self.LibraryMetaNames.DESCRIPTION] = definition['description']

        details = self.store_library(lib_metadata)
        return self.get_library_uid(details)

    def store_library(self, meta_props):
        """
            Create custom library.

            :param meta_props: dictionary with parameters describing custom library. To see available meta names use:

               >>> client.runtimes.LibraryMetaNames.get()
            :type meta_props: dict

            :returns: details of created custom library
            :rtype: dict

            A way you might use me is:

             >>> library_details = client.runtimes.store_library({
                        self.client.runtimes.LibraryMetaNames.NAME: "libraries_custom",
                        self.client.runtimes.LibraryMetaNames.DESCRIPTION: "custom libraries for scoring",
                        self.client.runtimes.LibraryMetaNames.FILEPATH: custom_library_path,
                        self.client.runtimes.LibraryMetaNames.VERSION: "1.0",
                        self.client.runtimes.LibraryMetaNames.PLATFORM: {"name": "python", "versions": ["3.5"]}
                    })
         """
        self.LibraryMetaNames._validate(meta_props)

        lib_metadata = {
            MetaNames.LIBRARIES.NAME: meta_props[self.LibraryMetaNames.NAME],
            MetaNames.LIBRARIES.VERSION: meta_props[self.LibraryMetaNames.VERSION],
            MetaNames.LIBRARIES.PLATFORM: json.dumps(meta_props[self.LibraryMetaNames.PLATFORM])
        }

        if self.LibraryMetaNames.DESCRIPTION in meta_props:
            lib_metadata[MetaNames.LIBRARIES.DESCRIPTION] = meta_props[self.LibraryMetaNames.DESCRIPTION]

        try:
            libArtifact = MLRepositoryArtifact(meta_props['filepath'], meta_props=MetaProps(lib_metadata.copy()))
            lib_artifact = self._client.repository._ml_repository_client.libraries.save(libArtifact)
            return self.get_library_details(lib_artifact.uid)
        except Exception as e:
            raise WMLClientError('Failure during creation of library.', e)

    def _create_runtime_spec(self, custom_libs_list, meta_props):
        metadata = {
            MetaNames.RUNTIMES.NAME: meta_props[self.ConfigurationMetaNames.NAME],
            MetaNames.RUNTIMES.PLATFORM: json.dumps(meta_props[self.ConfigurationMetaNames.PLATFORM]),
        }

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            metadata[MetaNames.DESCRIPTION] = meta_props[self.ConfigurationMetaNames.DESCRIPTION]

        if custom_libs_list is not None:
            metadata[MetaNames.RUNTIMES.CUSTOM_LIBRARIES_URLS] = json.dumps({
                "urls": [self._href_definitions.get_custom_library_href(uid) for uid in custom_libs_list]
            })

        if self.ConfigurationMetaNames.CONFIGURATION_FILEPATH in meta_props:
            metadata[MetaNames.CONTENT_LOCATION] = meta_props[self.ConfigurationMetaNames.CONFIGURATION_FILEPATH]

        try:
            runtimeArtifact = MLRepositoryArtifact(meta_props=MetaProps(metadata.copy()))
            if self.ConfigurationMetaNames.CONFIGURATION_FILEPATH in meta_props:
                runtime_artifact = self._client.repository._ml_repository_client.runtimes.save(
                    runtimeArtifact,
                    meta_props[self.ConfigurationMetaNames.CONFIGURATION_FILEPATH]
                )
            else:
                runtime_artifact = self._client.repository._ml_repository_client.runtimes.save(runtimeArtifact)
            return runtime_artifact.uid
        except Exception as e:
            raise WMLClientError('Failure during creation of runtime.', e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, meta_props):
        """
            Create runtime.

            :param meta_props: dictionary with parameters describing runtime spec. To see available meta names use:

               >>> client.runtimes.DefinitionMetaNames.get()
            :type meta_props: dict

            :returns: details of created runtime
            :rtype: dict

            The simplest way you might use me is:

            >>> runtime_details = client.runtimes.store({
                client.runtimes.ConfigurationMetaNames.NAME: "test",
                client.runtimes.ConfigurationMetaNames.PLATFORM: {"name": "python", "version": "3.5"}
            })

            The most complex way to use me is:

            >>>
                # here library is created
                lib_meta = {
                    client.runtimes.LibraryMetaNames.NAME: "libraries_custom",
                    client.runtimes.LibraryMetaNames.DESCRIPTION: "custom libraries for scoring",
                    client.runtimes.LibraryMetaNames.FILEPATH: "/home/user/my_lib.zip",
                    client.runtimes.LibraryMetaNames.VERSION: "1.0",
                    client.runtimes.LibraryMetaNames.PLATFORM: {"name": "python", "versions": ["3.5"]}
                }
                custom_library_details = client.runtimes.store_library(lib_meta)
                custom_library_uid = client.runtimes.get_library_uid(custom_library_details)
                # now, metaprops for runtime spec are prepared
                meta = {
                    client.runtimes.ConfigurationMetaNames.NAME: "runtime_spec_python_3.5",
                    client.runtimes.ConfigurationMetaNames.DESCRIPTION: "test",
                    client.runtimes.ConfigurationMetaNames.PLATFORM: {
                        "name": "python",
                        "version": "3.5"
                    },
                    client.runtimes.ConfigurationMetaNames.LIBRARIES_DEFINITIONS: [ # here in the background are created additional two libraries
                        LibraryDefinition("my_lib_1", "1.0", "/home/user/my_lib_1.zip", description="t", platform={"name": "python", "versions": ["3.5"]}),
                        LibraryDefinition("my_lib_2", "1.1", "/home/user/my_lib_2.zip")
                    ],
                    client.runtimes.ConfigurationMetaNames.LIBRARIES_UIDS: [custom_library_uid] # already existing lib is linked here
                }
                # Now runtime spec is created. Note that during runtime spec creation also "my_lib_1" and "my_lib_2" will be created and "libraries_custom" will be linked.
                runtime_details = client.runtimes.store(meta)

         """
        self.ConfigurationMetaNames._validate(meta_props)

        custom_libs_list = []

        if self.ConfigurationMetaNames.LIBRARIES_DEFINITIONS in meta_props:
            custom_libs_list.extend(
                [self._create_library_from_definition(definition, meta_props) for definition in
                 meta_props[self.ConfigurationMetaNames.LIBRARIES_DEFINITIONS]]
            )

        if self.ConfigurationMetaNames.LIBRARIES_UIDS in meta_props:
            custom_libs_list.extend(meta_props[self.ConfigurationMetaNames.LIBRARIES_UIDS])

        runtime_uid = self._create_runtime_spec(custom_libs_list, meta_props)

        return self.get_details(runtime_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, runtime_uid=None, limit=None):
        """
           Get information about your runtime(s).

           :param runtime_uid:  Runtime UID (optional)
           :type runtime_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: metadata of runtime(s)
           :rtype: dict

           A way you might use me is:

            >>> runtime_details = client.runtimes.get_details(runtime_uid)
            >>> runtime_details = client.runtimes.get_details(runtime_uid=runtime_uid)
            >>> runtime_details = client.runtimes.get_details()
        """
        runtime_uid = str_type_conv(runtime_uid)
        Runtimes._validate_type(runtime_uid, u'runtime_uid', STR_TYPE, False)

        if runtime_uid is not None and not is_uid(runtime_uid):
            raise WMLClientError(u'\'runtime_uid\' is not an uid: \'{}\''.format(runtime_uid))

        url = self._href_definitions.get_runtimes_href()

        return self._get_artifact_details(url, runtime_uid, limit, 'runtime specs')

    def get_library_details(self, library_uid=None, limit=None):
        """
           Get information about your custom libraries(s).

           :param library_uid:  Library UID (optional)
           :type library_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: metadata of libraries(s)
           :rtype: dict

           A way you might use me is:

            >>> library_details = client.runtimes.get_library_details(library_uid)
            >>> library_details = client.runtimes.get_library_details(library_uid=library_uid)
            >>> library_details = client.runtimes.get_library_details()
        """
        library_uid = str_type_conv(library_uid)
        Runtimes._validate_type(library_uid, u'library_uid', STR_TYPE, False)

        if library_uid is not None and not is_uid(library_uid):
            raise WMLClientError(u'\'library_uid\' is not an uid: \'{}\''.format(library_uid))

        url = self._href_definitions.get_custom_libraries_href()

        return self._get_artifact_details(url, library_uid, limit, 'libraries')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_url(details):
        """
            Get runtime url from runtime details, or runtime url from model details.

            :param details: Created runtime or model details
            :type details: dict

            :returns: runtime url
            :rtype: {str_type}

            A way you might use me is:

             >>> runtime_url = client.runtimes.get_url(runtime_details)
        """
        Runtimes._validate_type(details, u'details', dict, True)
        Runtimes._validate_type_of_details(details, [RUNTIME_SPEC_DETAILS_TYPE, MODEL_DETAILS_TYPE, FUNCTION_DETAILS_TYPE])

        details_type = get_type_of_details(details)

        if details_type == RUNTIME_SPEC_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'runtime_details', ['metadata', 'url'])
        elif details_type == MODEL_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'model_details', ['entity', 'runtime', 'url'])
        elif details_type == FUNCTION_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'function_details', ['entity', 'runtime', 'url'])
        else:
            raise WMLClientError('Unexpected details type: {}'.format(details_type))

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(details):
        """
            Get runtime uid from runtime details, or runtime uid from model details.

            :param details: Created runtime or model details
            :type details: dict

            :returns: runtime uid
            :rtype: {str_type}

            A way you might use me is:

            >>> runtime_uid = client.runtimes.get_uid(runtime_details)
        """
        Runtimes._validate_type(details, u'details', dict, True)
        Runtimes._validate_type_of_details(details, [RUNTIME_SPEC_DETAILS_TYPE, MODEL_DETAILS_TYPE, FUNCTION_DETAILS_TYPE])

        details_type = get_type_of_details(details)

        if details_type == RUNTIME_SPEC_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'runtime_details', ['metadata', 'guid'])
        elif details_type == MODEL_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'model_details', ['entity', 'runtime', 'url']).split('/')[-1]
        elif details_type == FUNCTION_DETAILS_TYPE:
            return Runtimes._get_required_element_from_dict(details, 'function_details', ['entity', 'runtime', 'url']).split('/')[-1]
        else:
            raise WMLClientError('Unexpected details type: {}'.format(details_type))

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_library_url(library_details):
        """
            Get library url from library details.

            :param library_details: Created library details
            :type library_details: dict

            :returns: library url
            :rtype: {str_type}

            A way you might use me is:

             >>> library_url = client.runtimes.get_library_url(library_details)
        """
        Runtimes._validate_type(library_details, u'library_details', dict, True)
        Runtimes._validate_type_of_details(library_details, LIBRARY_DETAILS_TYPE)

        return Runtimes._get_required_element_from_dict(library_details, 'library_details', ['metadata', 'url'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_library_uid(library_details):
        """
            Get library uid from library details.

            :param library_details: Created library details
            :type library_details: dict

            :returns: library uid
            :rtype: {str_type}

            A way you might use me is:

            >>> library_uid = client.runtimes.get_library_uid(library_details)
        """
        Runtimes._validate_type(library_details, u'library_details', dict, True)
        Runtimes._validate_type_of_details(library_details, LIBRARY_DETAILS_TYPE)

        # TODO error handling
        return Runtimes._get_required_element_from_dict(library_details, 'library_details', ['metadata', 'guid'])

    def _get_runtimes_uids_for_lib(self, library_uid, runtime_details=None):
        if runtime_details is None:
            runtime_details = self.get_details()

        return list(map(
            lambda x: x['metadata']['guid'],
            filter(
                lambda x: any(
                    filter(
                        lambda y: library_uid in y['url'],
                        x['entity']['custom_libraries'] if 'custom_libraries' in x['entity'] else [])
                ),
                runtime_details['resources']
            )
        ))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, runtime_uid, with_libraries=False):
        """
            Delete runtime.

            :param runtime_uid: Runtime UID
            :type runtime_uid: {str_type}

            :param autoremove: if set to False, only runtime will be removed, if set to True, all libraries belonging only to it will be removed
            :type autoremove: bool

            A way you might use me is:

            >>> client.runtimes.delete(runtime_uid)
            >>> client.runtimes.delete(runtime_uid, with_libraries=True)
        """
        runtime_uid = str_type_conv(runtime_uid)
        Runtimes._validate_type(runtime_uid, u'runtime_uid', STR_TYPE, True)
        Runtimes._validate_type(with_libraries, u'autoremove', bool, True)

        if runtime_uid is not None and not is_uid(runtime_uid):
            raise WMLClientError(u'\'runtime_uid\' is not an uid: \'{}\''.format(runtime_uid))

        if with_libraries:
            runtime_details = self.get_details(runtime_uid)

        url = self._href_definitions.get_runtime_href(runtime_uid)

        if not self._ICP:
            response_delete = requests.delete(
                url,
                headers=self._client._get_headers())
        else:
            response_delete = requests.delete(
                url,
                headers=self._client._get_headers(),
                verify=False)

        self._handle_response(204, u'runtime deletion', response_delete, False)

        if with_libraries:
            if 'custom_libraries' in runtime_details['entity']:
                details = self.get_details()
                custom_libs_uids = map(lambda x: x['url'].split('/')[-1], runtime_details['entity']['custom_libraries'])
                custom_libs_to_remove = filter(
                    lambda x: len(self._get_runtimes_uids_for_lib(x, details)) == 0,
                    custom_libs_uids
                )

                for uid in custom_libs_to_remove:
                    print('Deleting orphaned library \'{}\' during autoremove delete.'.format(uid))
                    self.delete_library(uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _delete_orphaned_libraries(self):
        """
            Delete all custom libraries without runtime.

            A way you might use me is:

            >>> client.runtimes.delete_orphaned_libraries()
        """
        lib_details = self.get_library_details()
        details = self.get_details()
        for lib in lib_details['resources']:
            lib_uid = lib['metadata']['guid']
            if len(self._get_runtimes_uids_for_lib(lib_uid, details)) == 0:
                print('Deleting orphaned \'{}\' library... '.format(lib_uid), end="")
                library_endpoint = self._href_definitions.get_custom_library_href(lib_uid)
                if not self._ICP:
                    response_delete = requests.delete(library_endpoint, headers=self._client._get_headers())
                else:
                    response_delete = requests.delete(library_endpoint, headers=self._client._get_headers(), verify=False)

                try:
                    self._handle_response(204, u'library deletion', response_delete, False)
                    print('SUCCESS')
                except:
                    pass


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete_library(self, library_uid):
        """
            Delete custom library from repository.

            :param library_uid: stored custom library UID
            :type library_uid: {str_type}

            A way you might use me is:

            >>> client.runtimes.delete_library(library_uid)
        """
        Runtimes._validate_type(library_uid, u'library_uid', STR_TYPE, True)
        library_endpoint = self._href_definitions.get_custom_library_href(library_uid)
        if not self._ICP:
            response_delete = requests.delete(library_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(library_endpoint, headers=self._client._get_headers(), verify=False)

        self._handle_response(204, u'library deletion', response_delete, False)

    def list(self, limit=None):
        """
           List runtimes. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is:

           >>> client.runtimes.list()
        """
        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'platform']['name'] + '-' + m[u'entity'][u'platform']['version']) for m in resources]

        self._list(values, [u'GUID', u'NAME', u'CREATED', u'PLATFORM'], limit, 50)

    def _list_runtimes_for_libraries(self): # TODO make public when the time'll come
        """
           List runtimes uids for libraries.

           A way you might use me is:

           >>> client.runtimes.list_runtimes_for_libraries()
           >>> client.runtimes.list_runtimes_for_libraries(library_uid)
        """
        details = self.get_library_details()
        runtime_details = self.get_details()

        values = [
            (m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'entity'][u'version'],
             ', '.join(self._get_runtimes_uids_for_lib(m[u'metadata'][u'guid'], runtime_details))) for m in
            details['resources']]

        values = sorted(sorted(values, key=lambda x: x[2], reverse=True), key=lambda x: x[1])

        from tabulate import tabulate

        header = [u'GUID', u'NAME', u'VERSION', u'RUNTIME SPECS']
        table = tabulate([header] + values)

        print(table)

    def list_libraries(self, runtime_uid=None, limit=None):
        """
           List custom libraries. If limit is set to None there will be only first 50 records shown.

           :param runtime_uid: Runtime UID
           :type runtime_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is:

           >>> client.runtimes.list_libraries()
           >>> client.runtimes.list_libraries(runtime_uid)
        """
        runtime_uid = str_type_conv(runtime_uid)
        Runtimes._validate_type(runtime_uid, u'runtime_uid', STR_TYPE, False)

        if runtime_uid is None:
            details = self.get_library_details()

            resources = details[u'resources']
            values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'entity'][u'version'], m[u'metadata'][u'created_at'],
                       m[u'entity'][u'platform']['name'], m[u'entity'][u'platform'][u'versions']) for m in
                      resources]

            self._list(values, [u'GUID', u'NAME', u'VERSION', u'CREATED', u'PLATFORM NAME', u'PLATFORM VERSIONS'], limit, 50)
        else:
            details = self.get_details(runtime_uid)

            if 'custom_libraries' not in details['entity'] or len(details['entity']['custom_libraries']) == 0:
                print('No libraries found for this runtime.')
                return

            values = [(m[u'url'].split('/')[-1], m[u'name'], m['version']) for m in details['entity']['custom_libraries']]

            values = sorted(sorted(values, key=lambda x: x[2], reverse=True), key=lambda x: x[1])

            from tabulate import tabulate

            header = [u'GUID', u'NAME', u'VERSION']
            table = tabulate([header] + values)

            print(table)

    def download_configuration(self, runtime_uid, filename=None):
        """
            Downloads configuration file for runtime with specified UID.

            :param runtime_uid:  UID of runtime
            :type runtime_uid: {str_type}
            :param filename: filename of downloaded archive (optional)
            :type filename: {str_type}

            :returns: path to downloaded file
            :rtype: {str_type}

            A way you might use me is:

            >>> filename = client.runtimes.download_configuration(runtime_uid)
            >>> client.runtimes.download_configuration(runtime_uid, filename=filename)
        """

        runtime_uid = str_type_conv(runtime_uid)
        Runtimes._validate_type(runtime_uid, u'runtime_uid', STR_TYPE, True)

        if not is_uid(runtime_uid):
            raise WMLClientError(u'\'runtime_uid\' is not an uid: \'{}\''.format(runtime_uid))

        download_url = self._href_definitions.get_runtime_href(runtime_uid) + '/content'

        if not self._ICP:
            response_get = requests.get(
                download_url,
                headers=self._client._get_headers())
        else:
            response_get = requests.get(
                download_url,
                headers=self._client._get_headers(),
                verify=False)

        if filename is None:
            filename = 'runtime_configuration.yaml'

        if response_get.status_code == 200:
            with open(filename, "wb") as new_file:
                new_file.write(response_get.content)
                new_file.close()

                print_text_header_h2(
                    u'Successfully downloaded configuration file: ' + str(filename))

                return filename
        else:
            raise WMLClientError(u'Unable to download configuration content: ' + response_get.text)

    def download_library(self, library_uid, filename=None):
        """
            Downloads custom library content with specified UID.

            :param library_uid:  UID of library
            :type library_uid: {str_type}
            :param filename: filename of downloaded archive (optional)
            :type filename: {str_type}

            :returns: path to downloaded file
            :rtype: {str_type}

            A way you might use me is:

            >>> filename = client.runtimes.download_library(library_uid)
            >>> client.runtimes.download_library(library_uid, filename=filename)
        """

        library_uid = str_type_conv(library_uid)
        Runtimes._validate_type(library_uid, u'library_uid', STR_TYPE, True)

        if not is_uid(library_uid):
            raise WMLClientError(u'\'library_uid\' is not an uid: \'{}\''.format(library_uid))

        download_url = self._href_definitions.get_custom_library_href(library_uid) + '/content'

        if not self._ICP:
            response_get = requests.get(
                download_url,
                headers=self._client._get_headers())
        else:
            response_get = requests.get(
                download_url,
                headers=self._client._get_headers(),
                verify=False)

        if filename is None:
            details = self.get_library_details(library_uid)
            filename = '{}-{}.zip'.format(details['entity']['name'], details['entity']['version'])

        if response_get.status_code == 200:
            with open(filename, "wb") as new_file:
                new_file.write(response_get.content)
                new_file.close()

                print_text_header_h2(
                    u'Successfully downloaded library content: ' + str(filename))

                return filename
        else:
            raise WMLClientError(u'Unable to download library content: ' + response_get.text)