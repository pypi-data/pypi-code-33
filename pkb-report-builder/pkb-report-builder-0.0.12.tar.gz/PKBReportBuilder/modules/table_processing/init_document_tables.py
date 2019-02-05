import models.processing_tables.processing_table_models as processing_table_models
import logging


# init existing table
def init_existing_contracts_table(root):
    try:

        table_path = ['Result', 'Root', 'ExistingContracts', 'Contract']
        table = processing_table_models.ProcessingTable("Действующие договора", root, table_path,
                                                        hidden_columns_in_groups=["Name", "SubjectRole",
                                                                                  "FinancialInstitution"])

        # column Наименование Заемщика/гаранта/ созаемщика
        table.init_column("Наименование Заемщика/гаранта/созаемщика", "Name",
                          [
                              [
                                  ['Result', 'Root', 'Header', 'Surname'],
                                  ['Result', 'Root', 'Header', 'Name'],
                                  ['Result', 'Root', 'Header', 'FathersName']
                              ],
                              [
                                  ['Result', 'Root', 'Header', 'NameNative']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(1), True
                          )

        # column Роль Субъекта (гарант, созаемщик, заемщик)
        table.init_column("Роль субъекта", "SubjectRole",
                          [
                              [
                                  ['SubjectRole']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, True),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Наименование Банка
        table.init_column("Наименование Банка", "FinancialInstitution",
                          [
                              [
                                  ['FinancialInstitution'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Тип КЛ
        table.init_column("Тип КЛ", "TypeOfFoundingn",
                          [
                              [
                                  ['TypeOfFounding'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Номер договора
        table.init_column("Номер договора", "AgreementNumber",
                          [
                              [
                                  ['AgreementNumber'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Лимит/ Общая сумма кредита (тыс. тенге)
        table.init_column("Лимит/ Общая сумма кредита (тыс. тенге)", "TotalAmount",
                          [
                              [
                                  # ['CreditLimit'],
                                  ['TotalAmount']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Наименование Заемщика/гаранта/ созаемщика (тыс. тенге)
        table.init_column("Наименование Заемщика/гаранта/ созаемщика (тыс. тенге)", "OutstandingAmount",
                          [
                              [
                                  ['OutstandingAmount']

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False)

        # column Сумма ежемесячного платежа, тыс. тенге
        table.init_column("Сумма ежемесячного платежа, тыс. тенге", "MonthlyInstalmentAmount",
                          [
                              [
                                  ['MonthlyInstalmentAmount'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Дата открытия кредитной линии, ДД.ММ.ГГГГ
        table.init_column("Дата открытия кредитной линии, ДД.ММ.ГГГГ", "DateOfCreditStart",
                          [
                              [
                                  ['DateOfCreditStart'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Дата закрытия кредитной линии, ДД.ММ.ГГГГ
        table.init_column("Дата закрытия кредитной линии, ДД.ММ.ГГГГ", "DateOfCreditEnd",
                          [
                              [
                                  ['DateOfCreditEnd'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Период доступности ДД.ММ.ГГГГ
        table.init_column("Период доступности ДД.ММ.ГГГГ", "AvailableDate",
                          [
                              [
                                  ['AvailableDate'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Ставка вознаграждения (при наличии информации)
        table.init_column("Ставка вознаграждения (при наличии информации) ", "NominalRate",
                          [
                              [
                                  ['NominalRate'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Цель
        table.init_column("Цель", "CreditObject/PurposeOfCredit",
                          [
                              [
                                  ['CreditObject'],
                                  ['PurposeOfCredit']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, True),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Продолжительность просрочки, дней
        table.init_column("Продолжительность просрочки, дней", "OverdueAmountMaxCount",
                          [
                              [
                                  ['OverdueAmountMaxCount'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Максимальная длина одной просрочки (max)
        table.init_column("Максимальная длина одной просрочки (max)", "NumberOfOverdueInstalmentsMax",
                          [
                              [
                                  ['NumberOfOverdueInstalmentsMax'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Наличие текущей просрочки, в днях
        table.init_column("Наличие текущей просрочки, в днях", "NumberOfOverdueInstalments",
                          [
                              [
                                  ['NumberOfOverdueInstalments'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Просроченная сумма, тыс. Тенге (макс.)
        table.init_column("Просроченная сумма, тыс. Тенге (макс.)", "NumberOfOverdueInstalmentsMaxAmount",
                          [
                              [
                                  ['NumberOfOverdueInstalmentsMaxAmount'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Просроченная сумма, тыс. Тенге (макс.)
        table.init_column("Количество месяцев, в которых была зафиксирована просрочка", "MonthCountInstalments",
                          [
                              [
                                  ['-'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Количество просрочек более 30 дней
        table.init_column("Количество просрочек более 30 дней", "CountInstalmentsIn30Days",
                          [
                              [
                                  ['-'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Гаранты/созаемщики
        table.init_column("Гаранты/созаемщики", "Garants",
                          [
                              [
                                  ['-'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Вид обеспечения
        table.init_column("Вид обеспечения", "TypeOfGuarantee",
                          [
                              [
                                  ['Collateral', 'TypeOfGuarantee'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Стоимость обеспечения тыс. тенге
        table.init_column("Стоимость обеспечения тыс. тенге", "ValueOfGuarantee",
                          [
                              [
                                  ['Collateral', 'ValueOfGuarantee'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        return table
    except Exception as e:
        pass


# init exsisting table
def init_terminated_contracts_table(root):
    try:

        table_path = ['Result', 'Root', 'TerminatedContracts', 'Contract']
        table = processing_table_models.ProcessingTable("Завершенные договора", root, table_path,
                                                        hidden_columns_in_groups=["Name", "SubjectRole",
                                                                                  "FinancialInstitution"])

        # column Наименование Заемщика/гаранта/ созаемщика
        table.init_column("Наименование Заемщика/гаранта/созаемщика", "Name",
                          [
                              [
                                  ['Result', 'Root', 'Header', 'Surname'],
                                  ['Result', 'Root', 'Header', 'Name'],
                                  ['Result', 'Root', 'Header', 'FathersName']
                              ],
                              [
                                  ['Result', 'Root', 'Header', 'NameNative']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(1), True
                          )

        # column Роль Субъекта (гарант, созаемщик, заемщик)
        table.init_column("Роль субъекта", "SubjectRole",
                          [
                              [
                                  ['SubjectRole']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, True),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Наименование Банка
        table.init_column("Наименование Банка", "FinancialInstitution",
                          [
                              [
                                  ['FinancialInstitution'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Тип КЛ
        table.init_column("Тип КЛ", "TypeOfFoundingn",
                          [
                              [
                                  ['TypeOfFounding'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Номер договора
        table.init_column("Номер договора", "AgreementNumber",
                          [
                              [
                                  ['AgreementNumber'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Лимит/ Общая сумма кредита (тыс. тенге)
        table.init_column("Лимит/ Общая сумма кредита (тыс. тенге)", "TotalAmount",
                          [
                              [
                                  # ['CreditLimit'],
                                  ['TotalAmount']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )


        # column Дата открытия кредитной линии, ДД.ММ.ГГГГ
        table.init_column("Дата открытия кредитной линии, ДД.ММ.ГГГГ", "DateOfCreditStart",
                          [
                              [
                                  ['DateOfCreditStart'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Дата закрытия кредитной линии, ДД.ММ.ГГГГ
        table.init_column("Дата закрытия кредитной линии, ДД.ММ.ГГГГ", "DateOfCreditEnd",
                          [
                              [
                                  ['DateOfCreditEnd'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Период доступности ДД.ММ.ГГГГ
        table.init_column("Период доступности ДД.ММ.ГГГГ", "AvailableDate",
                          [
                              [
                                  ['AvailableDate'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # date format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         2),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Ставка вознаграждения (при наличии информации)
        table.init_column("Ставка вознаграждения (при наличии информации) ", "NominalRate",
                          [
                              [
                                  ['NominalRate'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(0), False
                          )

        # column Цель
        table.init_column("Цель", "CreditObject/PurposeOfCredit",
                          [
                              [
                                  ['CreditObject'],
                                  ['PurposeOfCredit']
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, True),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Продолжительность просрочки, дней
        table.init_column("Продолжительность просрочки, дней", "OverdueAmountMaxCount",
                          [
                              [
                                  ['OverdueAmountMaxCount'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Максимальная длина одной просрочки (max)
        table.init_column("Максимальная длина одной просрочки (max)", "NumberOfOverdueInstalmentsMax",
                          [
                              [
                                  ['NumberOfOverdueInstalmentsMax'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),

                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )


        # column Просроченная сумма, тыс. Тенге (макс.)
        table.init_column("Просроченная сумма, тыс. Тенге (макс.)", "NumberOfOverdueInstalmentsMaxAmount",
                          [
                              [
                                  ['NumberOfOverdueInstalmentsMaxAmount'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Просроченная сумма, тыс. Тенге (макс.)
        table.init_column("Количество месяцев, в которых была зафиксирована просрочка", "MonthCountInstalments",
                          [
                              [
                                  ['-'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Количество просрочек более 30 дней
        table.init_column("Количество просрочек более 30 дней", "CountInstalmentsIn30Days",
                          [
                              [
                                  ['-'],

                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Гаранты/созаемщики
        table.init_column("Гаранты/созаемщики", "Garants",
                          [
                              [
                                  ['-'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Вид обеспечения
        table.init_column("Вид обеспечения", "TypeOfGuarantee",
                          [
                              [
                                  ['Collateral', 'TypeOfGuarantee'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(0),
                                                                 None, None, None, False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        # column Стоимость обеспечения тыс. тенге
        table.init_column("Стоимость обеспечения тыс. тенге", "ValueOfGuarantee",
                          [
                              [
                                  ['Collateral', 'ValueOfGuarantee'],
                              ]

                          ], 'value',
                          processing_table_models.ConditionValue(None, None, None, 'value', None,
                                                                 processing_table_models.ConvertTypesCollection(1),
                                                                 None, None,
                                                                 [
                                                                     # only numbers
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         1),
                                                                     # money format
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         3),
                                                                     # thousand
                                                                     processing_table_models.OutputValueTypesCollection(
                                                                         4)
                                                                 ],
                                                                 False),
                          processing_table_models.ExtractValueTypesCollection(2), False
                          )

        return table
    except Exception as e:
        pass

# init document processing dtables
def init_document_tables(root):
    try:
        tables = []
        existing_contracts_table = init_existing_contracts_table(root)
        terminated_contracts_table = init_terminated_contracts_table(root)
        tables.append(existing_contracts_table)
        tables.append(terminated_contracts_table)
        return tables
    except Exception as e:
        logging.error("Error initialization. " + str(e))
