import logging
import models.export_models.export_document_elements as export_document_models
import models.tree_models.xml_navigator as xml_navigator
import models.export_models.export_styles as styles
# export  document
class ExportDocument():
    # constructor
    def __init__(self):
        try:
            # export elements
            self.export_elements = []
            self.xml_document_tables = []
            self.group_rows = []
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    # add export elements
    def add_export_element(self, params):
        try:
            type = params[0]
            name = params[1]
            navigate_params = params[2]
            element = export_document_models.ExportDocumentElement(type, name)

            if (type == 0):
                element.init_element_row(navigate_params)
            elif (type == 1):
                element.init_element_table(navigate_params)

            self.export_elements.append(element)
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    #init single field elements
    def init_document_field_elements(self):
        try:
            params = [
                # преступники
                [
                    0, 'MvdCriminalInvestigations', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'MvdCriminalInvestigations']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        ['Result', 'Root', 'PublicSources', 'MvdCriminalInvestigations', 'Status'],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # пропавшие без вести
                [
                    0, 'MvdMissingInvestigations', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'MvdMissingInvestigations']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'MvdMissingInvestigations', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # террористы
                [
                    0, 'TerrorList', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'TerrorList']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'TerrorList', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # задолженность > 6 месяцев
                [
                    0, 'Areears', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'Areears']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'Areears', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # лжепредпринимательская деятельность
                [
                    0, 'FalseBusi', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'FalseBusi']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'FalseBusi', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # банкроты
                [
                    0, 'Bankruptcy', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'Bankruptcy']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'Bankruptcy', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # гос закупки
                [
                    0, 'RNUGosZakup', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'RNUGosZakup']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'RNUGosZakup', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # преступники по правовой статистике
                [
                    0, 'QamqorList', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'QamqorList']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'QamqorList', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # преступники по алиментам
                [
                    0, 'QamqorAlimony', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'QamqorAlimony']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'QamqorAlimony', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ],
                # преступники по линии МФ РК
                [
                    0, 'KgdWanted', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'KgdWanted']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'KgdWanted', 'Status']
                        ]
                        ,
                        'value',
                        [0],
                        styles.row_value_style
                    )
                ]
                ]
            ]

            return params
        except Exception as e:
            logging.error("Error initialization. " + str(e))

    def init_document_table_elements(self):
        try:
            params =[
                # действующие договора
                [
                    1, 'ExistingContracts', [
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'ExistingContracts', 'Contract']
                        ],
                        'title',
                        [0],
                        styles.row_title_style
                    ),
                    xml_navigator.XmlNavigator(
                        [
                            ['Result', 'Root', 'PublicSources', 'KgdWanted', 'Status']
                        ],
                        'value',
                        [0],
                        styles.row_title_style
                    )
                ]
                ],
            ]
            pass
        except Exception as e:
            logging.error("Error initialization. " + str(e))


    # init document schemas elements
    def init_document_elements(self):
        try:
            #generate field params
            field_element_params =self.init_document_field_elements()
            for param in field_element_params:
                self.add_export_element(param)

        except Exception as e:
            logging.error("Error initialization. " + str(e))
