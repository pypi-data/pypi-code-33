import data
import fetcher
import datetime
from . import dre


class Diploma(data.Diploma):
    def __init__(self, identifier: str, issuer: str, date: datetime.date, info=None):
        super().__init__(identifier)
        self.__date = date
        self.__content = None
        self.__issuer = issuer
        self.__loaded = info is not None
        self.info = info

    @property
    def name(self):
        return f"{self.info['type']} nº{self.info['number']}/{self.__date.year}"

    @property
    def date(self) -> datetime.date:
        return self.__date

    @property
    def content(self):
        if not self.__loaded:
            self.__load()
        return self.__content

    @property
    def issuer(self):
        return self.__issuer

    def __load(self):
        pass


class Publication(data.Publication):
    def __init__(self, identifier, date, diplomas, info):
        super().__init__(identifier)
        self.info = info
        self.__diplomas = diplomas
        self.__date = date

    @property
    def name(self):
        if 'supplement' in self.info:
            return f"Nº{self.info['number']}/{self.__date.year}, " \
                f"Série {self.info['series'] * 'I'}-{self.info['supplement']}º suplemento " \
                f"em {self.__date.isoformat()}"
        else:
            return f"Nº{self.info['number']}/{self.__date.year}, " \
                f"Série {self.info['series'] * 'I'} " \
                f"em {self.__date.isoformat()}"

    @property
    def date(self):
        return self.__date

    @property
    def diplomas(self):
        return self.__diplomas


class Reader(data.Reader):
    def __init__(self):
        super().__init__()
        self.session = fetcher.Session()

    def get_publications(self, date_start: datetime.date, date_end: datetime.date) -> [data.Publication]:
        delta = date_end - date_start
        assert delta.days >= 0
        publications_index = []
        for i in range(delta.days + 1):
            publications_index += dre.get_publications_index(self.session, date_start + datetime.timedelta(i))
        publications = []
        for identifier, title, number, date, supplement in publications_index:
            publication_date, availability_date, series, number, supplement, eli, pdf_id, diplomas \
                = dre.get_publication(self.session, identifier)
            info = {'availability': availability_date,
                    'series': series,
                    'number': number,
                    'eli': eli,
                    'pdf_id': pdf_id}
            if supplement is not None:
                info['supplement'] = supplement
            publications.append(Publication(
                identifier,
                date,
                diplomas=self.__instantiate_diplomas(diplomas, date),
                info=info))
        return publications

    def get_diploma(self, identifier) -> data.Diploma:
        issuer, date, diploma_type, number, pages, eli, pdf_url, summary, raw_content \
            = dre.get_diploma(self.session, identifier)
        return Diploma(identifier, issuer, date,
                       info={'type': diploma_type,
                             'number': number,
                             'pages': pages,
                             'eli': eli,
                             'pdf_url': pdf_url,
                             'summary': summary,
                             'raw': raw_content})

    @staticmethod
    def __instantiate_diplomas(diploma_info, date) -> [Diploma]:
        diplomas = []
        for diploma_id, issuer, summary in diploma_info:
            diplomas.append(Diploma(diploma_id, issuer, date))
            return diplomas
