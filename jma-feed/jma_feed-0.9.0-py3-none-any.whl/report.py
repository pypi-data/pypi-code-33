from jma_feed.xml import XmlDocument


JMX_NS_MAP = {
    'jmx': 'http://xml.kishou.go.jp/jmaxml1/',
    'jmx_ib': 'http://xml.kishou.go.jp/jmaxml1/informationBasis1/',
    'jmx_eb': 'http://xml.kishou.go.jp/jmaxml1/elementBasis1/',
    'jmx_add': 'http://xml.kishou.go.jp/jmaxml1/addition1/',
    'jmx_mete': 'http://xml.kishou.go.jp/jmaxml1/body/meteorology1/',
    'jmx_seis': 'http://xml.kishou.go.jp/jmaxml1/body/seismology1/',
    'jmx_volc': 'http://xml.kishou.go.jp/jmaxml1/body/volcanology1/',
}


class Report(XmlDocument):
    """Model class which represents JMA report."""

    def __init__(self, target):
        super(Report, self).__init__(target, JMX_NS_MAP)

    @property
    def control(self):
        element = self._element('jmx:Control')
        return ReportControl(element)

    @property
    def head(self):
        element = self._element('jmx_ib:Head')
        return ReportHead(element)

    @property
    def body(self):
        xpath, element = self._find_element('jmx_mete:Body', 'jmx_seis:Body', 'jmx_volc:Body')
        if xpath == 'jmx_mete:Body':
            return ReportBodyMeteorology(element)
        if xpath == 'jmx_seis:Body':
            return ReportBodySeismology(element)
        if xpath == 'jmx_volc:Body':
            return ReportBodyVolcanology(element)
        return None


class ReportControl(XmlDocument):
    """Model class which represents JMA control part."""

    def __init__(self, target):
        super(ReportControl, self).__init__(target, JMX_NS_MAP)

    @property
    def title(self):
        return self._element_text('jmx:Title')

    @property
    def date_time(self):
        return self._element_text('jmx:DateTime')

    @property
    def status(self):
        return self._element_text('jmx:Status')

    @property
    def editorial_office(self):
        return self._element_text('jmx:EditorialOffice')

    @property
    def publishing_office(self):
        return self._element_text('jmx:PublishingOffice')


class ReportHead(XmlDocument):
    """Model class which represents JMA head part."""

    def __init__(self, target):
        super(ReportHead, self).__init__(target, JMX_NS_MAP)

    @property
    def title(self):
        return self._element_text('jmx_ib:Title')

    @property
    def report_date_time(self):
        return self._element_text('jmx_ib:ReportDateTime')

    @property
    def target_date_time(self):
        return self._element_text('jmx_ib:TargetDateTime')

    @property
    def event_id(self):
        return self._element_text('jmx_ib:EventID')

    @property
    def info_type(self):
        return self._element_text('jmx_ib:InfoType')

    @property
    def serial(self):
        return self._element_text('jmx_ib:Serial')

    @property
    def info_kind(self):
        return self._element_text('jmx_ib:InfoKind')

    @property
    def info_kind_version(self):
        return self._element_text('jmx_ib:InfoKindVersion')

    @property
    def headline_text(self):
        return self._element_text('jmx_ib:Headline/jmx_ib:Text')

    @property
    def headline_information_list(self):
        elements = self._elements('jmx_ib:Headline/jmx_ib:Information')
        return [HeadlineInformation(element) for element in elements]


class ReportBodyMeteorology(XmlDocument):
    """Model class which represents JMA meteorology body part."""

    def __init__(self, target):
        super(ReportBodyMeteorology, self).__init__(target, JMX_NS_MAP)

    @property
    def target_area(self):
        element = self._element('jmx_mete:TargetArea')
        if element == None:
            return None
        return MeteorologyArea(element)

    @property
    def comment(self):
        element = self._element('jmx_mete:Comment')
        if element == None:
            return None
        return MeteorologyComment(element)

    @property
    def notices(self):
        elements = self._elements('jmx_mete:Notice')
        return [element.text for element in elements]

    @property
    def warnings(self):
        elements = self._elements('jmx_mete:Warning')
        return [MeteorologyWarning(element) for element in elements]

    @property
    def meteorological_infos(self):
        elements = self._elements('jmx_mete:MeteorologicalInfos/jmx_mete:MeteorologicalInfo')
        return [MeteorologicalInfo(element) for element in elements]

    @property
    def time_series_infos(self):
        elements = self._elements('jmx_mete:MeteorologicalInfos/jmx_mete:TimeSeriesInfo')
        return [TimeSeriesInfo(element) for element in elements]


class ReportBodySeismology(XmlDocument):
    """Model class which represents JMA seismology body part."""

    def __init__(self, target):
        super(ReportBodySeismology, self).__init__(target, JMX_NS_MAP)

    @property
    def naming(self):
        return self._element_text('jmx_seis:Naming')

    @property
    def text(self):
        return self._element_text('jmx_seis:Text')

    @property
    def next_advisory(self):
        return self._element_text('jmx_seis:NextAdvisory')

    @property
    def comments(self):
        element = self._element('jmx_seis:Comments')
        if element == None:
            return None
        return SeismologyComment(element)

    @property
    def earthquakes(self):
        elements = self._elements('jmx_seis:Earthquake')
        return [Earthquake(element) for element in elements]

    @property
    def tsunami(self):
        element = self._element('jmx_seis:Tsunami')
        if element == None:
            return None
        return Tsunami(element)


class ReportBodyVolcanology(XmlDocument):
    """Model class which represents JMA volcanology body part."""

    def __init__(self, target):
        super(ReportBodyVolcanology, self).__init__(target, JMX_NS_MAP)

    @property
    def notice(self):
        return self._element_text('jmx_volc:Notice')

    @property
    def text(self):
        return self._element_text('jmx_volc:Text')

    @property
    def volcano_infos(self):
        elements = self._elements('jmx_volc:VolcanoInfo')
        return [VolcanoInfo(element) for element in elements]

    @property
    def ash_infos(self):
        elements = self._elements('jmx_volc:AshInfos/jmx_volc:AshInfo')
        return [AshInfo(element) for element in elements]


class HeadlineInformation(XmlDocument):
    def __init__(self, target):
        super(HeadlineInformation, self).__init__(target, JMX_NS_MAP)

    @property
    def type(self):
        return self._element_attr('.', 'type')

    @property
    def items(self):
        elements = self._elements('jmx_ib:Item')
        return [HeadlineInformationItem(element) for element in elements]


class HeadlineInformationItem(XmlDocument):
    def __init__(self, target):
        super(HeadlineInformationItem, self).__init__(target, JMX_NS_MAP)

    @property
    def kinds(self):
        elements = self._elements('jmx_ib:Kind')
        return [HeadlineInformationItemKind(element) for element in elements]

    @property
    def areas_code_type(self):
        return self._element_attr('jmx_ib:Areas', 'codeType')

    @property
    def areas(self):
        elements = self._elements('jmx_ib:Areas/jmx_ib:Area')
        return [HeadlineInformationItemArea(element) for element in elements]


class HeadlineInformationItemKind(XmlDocument):
    def __init__(self, target):
        super(HeadlineInformationItemKind, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_ib:Name')

    @property
    def code(self):
        return self._element_text('jmx_ib:Code')

    @property
    def condition(self):
        return self._element_text('jmx_ib:Condition')


class HeadlineInformationItemArea(XmlDocument):
    def __init__(self, target):
        super(HeadlineInformationItemArea, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_ib:Name')

    @property
    def code(self):
        return self._element_text('jmx_ib:Code')


class MeteorologyWarning(XmlDocument):
    def __init__(self, target):
        super(MeteorologyWarning, self).__init__(target, JMX_NS_MAP)

    @property
    def items(self):
        elements = self._elements('jmx_mete:Item')
        return [MeteorologyItem(element) for element in elements]


class MeteorologicalInfo(XmlDocument):
    def __init__(self, target):
        super(MeteorologicalInfo, self).__init__(target, JMX_NS_MAP)

    @property
    def items(self):
        elements = self._elements('jmx_mete:Item')
        return [MeteorologyItem(element) for element in elements]

    @property
    def date_time(self):
        return self._element_text('jmx_mete:DateTime')

    @property
    def duration(self):
        return self._element_text('jmx_mete:Duration')

    @property
    def name(self):
        return self._element_text('jmx_mete:Name')


class TimeSeriesInfo(XmlDocument):
    def __init__(self, target):
        super(TimeSeriesInfo, self).__init__(target, JMX_NS_MAP)

    @property
    def items(self):
        elements = self._elements('jmx_mete:Item')
        return [MeteorologyItem(element) for element in elements]

    @property
    def time_defines(self):
        elements = self._elements('jmx_mete:TimeDefines/jmx_mete:TimeDefine')
        return [TimeDefine(element) for element in elements]


class TimeDefine(XmlDocument):
    def __init__(self, target):
        super(TimeDefine, self).__init__(target, JMX_NS_MAP)

    @property
    def date_time(self):
        return self._element_text('jmx_mete:DateTime')

    @property
    def duration(self):
        return self._element_text('jmx_mete:Duration')

    @property
    def name(self):
        return self._element_text('jmx_mete:Name')


class MeteorologyComment(XmlDocument):
    def __init__(self, target):
        super(MeteorologyComment, self).__init__(target, JMX_NS_MAP)

    @property
    def texts(self):
        elements = self._elements('jmx_mete:Text')
        return [MeteorologyText(element) for element in elements]


class MeteorologyText(XmlDocument):
    def __init__(self, target):
        super(MeteorologyText, self).__init__(target, JMX_NS_MAP)

    @property
    def text(self):
        return self._element_text('.')

    @property
    def type(self):
        return self._element_attr('.', 'type')


class MeteorologyItem(XmlDocument):
    def __init__(self, target):
        super(MeteorologyItem, self).__init__(target, JMX_NS_MAP)

    @property
    def kinds(self):
        elements = self._elements('jmx_mete:Kind')
        return [MeteorologyKind(element) for element in elements]

    @property
    def area(self):
        element = self._element('jmx_mete:Area')
        if element == None:
            return None
        return MeteorologyArea(element)

    @property
    def change_status(self):
        return self._element_text('jmx_mete:ChangeStatus')

    @property
    def full_status(self):
        return self._element_text('jmx_mete:FullStatus')

    @property
    def editing_mark(self):
        return self._element_text('jmx_mete:EditingMark')


class MeteorologyKind(XmlDocument):
    def __init__(self, target):
        super(MeteorologyKind, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_mete:Name')

    @property
    def code(self):
        return self._element_text('jmx_mete:Code')

    @property
    def status(self):
        return self._element_text('jmx_mete:Status')

    @property
    def condition(self):
        return self._element_text('jmx_mete:Condition')


class MeteorologyArea(XmlDocument):
    def __init__(self, target):
        super(MeteorologyArea, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_mete:Name')

    @property
    def code(self):
        return self._element_text('jmx_mete:Code')


class Earthquake(XmlDocument):
    def __init__(self, target):
        super(Earthquake, self).__init__(target, JMX_NS_MAP)

    @property
    def origin_time(self):
        return self._element_text('jmx_seis:OriginTime')

    @property
    def arrival_time(self):
        return self._element_text('jmx_seis:ArrivalTime')

    @property
    def condition(self):
        return self._element_text('jmx_seis:Condition')

    @property
    def hypocenter(self):
        element = self._element('jmx_seis:Hypocenter')
        if element == None:
            return None
        return Hypocenter(element)

    @property
    def magnitudes(self):
        elements = self._elements('jmx_eb:Magnitude')
        return [element.text for element in elements]


class Hypocenter(XmlDocument):
    def __init__(self, target):
        super(Hypocenter, self).__init__(target, JMX_NS_MAP)

    @property
    def source(self):
        return self._element_text('jmx_seis:Source')

    @property
    def area(self):
        element = self._element('jmx_seis:Area')
        if element == None:
            return None
        return HypoArea(element)


class HypoArea(XmlDocument):
    def __init__(self, target):
        super(HypoArea, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_seis:Name')

    @property
    def code(self):
        return self._element_text('jmx_seis:Code')

    @property
    def coordinate(self):
        return self._element_text('jmx_eb:Coordinate')


class Tsunami(XmlDocument):
    def __init__(self, target):
        super(Tsunami, self).__init__(target, JMX_NS_MAP)

    @property
    def release(self):
        return self._element_text('jmx_eb:Release')

    @property
    def observation(self):
        element = self._element('jmx_seis:Observation')
        if element == None:
            return None
        return TsunamiDetail(element)

    @property
    def estimation(self):
        element = self._element('jmx_seis:Estimation')
        if element == None:
            return None
        return TsunamiDetail(element)

    @property
    def forecast(self):
        element = self._element('jmx_seis:Forecast')
        if element == None:
            return None
        return TsunamiDetail(element)


class TsunamiDetail(XmlDocument):
    def __init__(self, target):
        super(TsunamiDetail, self).__init__(target, JMX_NS_MAP)

    @property
    def items(self):
        elements = self._elements('jmx_seis:Item')
        return [TsunamiItem(element) for element in elements]


class TsunamiItem(XmlDocument):
    def __init__(self, target):
        super(TsunamiItem, self).__init__(target, JMX_NS_MAP)


class SeismologyComment(XmlDocument):
    def __init__(self, target):
        super(SeismologyComment, self).__init__(target, JMX_NS_MAP)

    @property
    def warning_comment(self):
        element = self._element('jmx_seis:WarningComment')
        if element == None:
            return None
        return SeismologyCommentForm(element)

    @property
    def forecast_comment(self):
        element = self._element('jmx_seis:ForecastComment')
        if element == None:
            return None
        return SeismologyCommentForm(element)

    @property
    def observation_comment(self):
        element = self._element('jmx_seis:ObservationComment')
        if element == None:
            return None
        return SeismologyCommentForm(element)

    @property
    def var_comment(self):
        element = self._element('jmx_seis:VarComment')
        if element == None:
            return None
        return SeismologyCommentForm(element)

    @property
    def free_form_comment(self):
        return self._element_text('jmx_seis:FreeFormComment')


class SeismologyCommentForm(XmlDocument):
    def __init__(self, target):
        super(SeismologyCommentForm, self).__init__(target, JMX_NS_MAP)

    @property
    def text(self):
        return self._element_text('jmx_seis:Text')

    @property
    def code(self):
        return self._element_text('jmx_seis:Code')

    @property
    def code_type(self):
        return self._element_attr('.', 'codeType')


class VolcanoInfo(XmlDocument):
    def __init__(self, target):
        super(VolcanoInfo, self).__init__(target, JMX_NS_MAP)

    @property
    def items(self):
        elements = self._elements('jmx_volc:Item')
        return [VolcanologyItem(element) for element in elements]


class AshInfo(XmlDocument):
    def __init__(self, target):
        super(AshInfo, self).__init__(target, JMX_NS_MAP)

    @property
    def start_time(self):
        return self._element_text('jmx_volc:StartTime')

    @property
    def end_time(self):
        return self._element_text('jmx_volc:EndTime')

    @property
    def items(self):
        elements = self._elements('jmx_volc:Item')
        return [VolcanologyItem(element) for element in elements]


class VolcanologyItem(XmlDocument):
    def __init__(self, target):
        super(VolcanologyItem, self).__init__(target, JMX_NS_MAP)

    @property
    def kind(self):
        element = self._element('jmx_volc:Kind')
        if element == None:
            return None
        return VolcanologyKind(element)

    @property
    def areas(self):
        elements = self._elements('jmx_volc:Areas/jmx_volc:Area')
        return [VolcanologyArea(element) for element in elements]


class VolcanologyKind(XmlDocument):
    def __init__(self, target):
        super(VolcanologyKind, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_volc:Name')

    @property
    def formal_name(self):
        return self._element_text('jmx_volc:FormalName')

    @property
    def code(self):
        return self._element_text('jmx_volc:Code')

    @property
    def condition(self):
        return self._element_text('jmx_volc:Condition')


class VolcanologyArea(XmlDocument):
    def __init__(self, target):
        super(VolcanologyArea, self).__init__(target, JMX_NS_MAP)

    @property
    def name(self):
        return self._element_text('jmx_volc:Name')

    @property
    def code(self):
        return self._element_text('jmx_volc:Code')

    @property
    def coordinate(self):
        return self._element_text('jmx_eb:Coordinate')
