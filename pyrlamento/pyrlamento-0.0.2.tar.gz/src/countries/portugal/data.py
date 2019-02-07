import data
import datetime
from html2text import html2text
from . import dre


class Diploma(data.Diploma):
    def __init__(self, identifier: str, issuer: str, date: datetime.date, session, info=None):
        super().__init__(identifier)
        self.__date = date
        self.__issuer = issuer
        if info is None:
            self.__content = None
            self.__loaded = False
        else:
            self.__loaded = True
            self.__content = info['content']
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
            return f"Nº{self.info['number']}/{self.__date.year} " \
                f"Série {self.info['series'] * 'I'}-{self.info['supplement']}º suplemento "
        else:
            return f"Nº{self.info['number']}/{self.__date.year} " \
                f"Série {self.info['series'] * 'I'}"

    @property
    def date(self):
        return self.__date

    @property
    def diplomas(self):
        return self.__diplomas

    def __str__(self):
        return self.name + " - " + self.__date.isoformat()


class Reader(data.Reader):
    def __init__(self, session):
        super().__init__(session)

    def get_publications(self, date_start: datetime.date, date_end: datetime.date) -> [data.Publication]:
        delta = date_end - date_start
        assert delta.days >= 0
        publications_index = []
        for i in range(delta.days + 1):
            publications_index += dre.get_publications_index(self.session, date_start + datetime.timedelta(i))
        publications = []
        for identifier, _, _, _, _ in publications_index:
            publications.append(self.get_publication(identifier))
        return publications

    def get_publication(self, identifier) -> Publication:
        publication_date, availability_date, series, number, supplement, eli, pdf_id, diplomas \
            = dre.get_publication(self.session, identifier)
        info = {'availability': availability_date,
                'series': series,
                'number': number,
                'eli': eli,
                'pdf_id': pdf_id}
        if supplement is not None:
            info['supplement'] = supplement
        return Publication(identifier, publication_date,
                           diplomas=self.__instantiate_diplomas(diplomas, publication_date),
                           info=info)

    def get_diploma(self, identifier) -> data.Diploma:
        issuer, date, diploma_type, number, pages, eli, pdf_url, summary, raw_content \
            = dre.get_diploma(self.session, identifier)
        return Diploma(identifier, issuer, date, self.session,
                       info={'type': diploma_type,
                             'number': number,
                             'pages': pages,
                             'eli': eli,
                             'pdf_url': pdf_url,
                             'summary': summary,
                             'content': html2text(raw_content),
                             'raw_content': raw_content})

    def __instantiate_diplomas(self, diploma_info, date) -> [Diploma]:
        diplomas = []
        for diploma_id, issuer, summary in diploma_info:
            diplomas.append(Diploma(diploma_id, issuer, date, self.session))
            return diplomas
