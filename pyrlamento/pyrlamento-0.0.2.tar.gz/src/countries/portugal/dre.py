import datetime
import re
from bs4 import BeautifulSoup

DATE_FORMAT = "%Y-%m-%d"

DRE_DATE_PUBLICATIONS = 'https://dre.pt/web/guest/pesquisa-avancada/-/asearch/advanced/maximized' \
                        '?types=DR&dataPublicacao={date}&perPage=1000'

DRE_YEAR_PUBLICATIONS = 'https://dre.pt/web/guest/pesquisa-avancada/-/asearch/advanced/maximized' \
                        '?types=DR&ano={year}&perPage=10000'

DRE_PUBLICATION = 'https://dre.pt/web/guest/home/-/dre/{identifier}/details/maximized'
RE_DRE_DATE_PUBLICATIONS = re.compile(r'dre.pt/web/guest/pesquisa-avancada/-/asearch/(?P<id>\d+)/details/maximized')
RE_PUBLICATION_TITLE = re.compile(r"Diário da República n.º (?P<number>\d+)/20\d{2},"
                                  r"(?: (?P<supplement>\d+)º Suplemento,)? "
                                  r"Série (?P<serie>[I]{1,2}) de (?P<date>[\d-]+).")
DRE_PDF = 'https://dre.pt/application/conteudo/{identifier}'
RE_DRE_PDF = re.compile('/application/conteudo/(?P<id>\\d+)')

# European law identifier
RE_ELI = re.compile('data.dre.pt/eli/')

def get_publications_index(session, date):
    page = __get_page(session, DRE_DATE_PUBLICATIONS.format(date=date))
    publication_index = []
    for link in page.find_all(href=RE_DRE_DATE_PUBLICATIONS):
        title = RE_PUBLICATION_TITLE.findall(link.attrs['title'])
        assert len(title) == 1
        number, supplement, series, date = title[0]
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
        publication_index.append(
            (RE_DRE_DATE_PUBLICATIONS.findall(link.attrs['href'])[0],
             link.attrs['title'],
             number,
             date,
             None if supplement == '' else supplement))
    return publication_index


def get_publication(session, identifier):
    page = __get_page(session, DRE_PUBLICATION.format(identifier=identifier))
    __strip_icons(page)
    publication_date = datetime.datetime.strptime(
        page.find('li', class_='dataPublicacao').text,
        DATE_FORMAT)
    availability_date = datetime.datetime.strptime(
        page.find('li', class_='formatedDataDisponibilizacao').text,
        DATE_FORMAT)
    series = page.find('li', class_='serie.nome').text
    assert series.strip('I') == ''
    series = len(series)
    number_in_series = int(page.find('li', class_='formatedNumero').text)
    supplement = page.find('li', class_='suplemento')
    supplement = int(supplement.text) if supplement is not None else None
    eli = __get_page_eli(page)
    pdf_id = __get_page_pdf_url(page)

    diplomas = []
    for diploma_link in page.find_all('a', title='Ver detalhes'):
        siblings = list(diploma_link.parent.children)
        assert len(siblings) in (7, 9)
        diploma_id = int(diploma_link.find('span', class_='rgba').text)
        author = siblings[3].text.strip()
        summary = siblings[5].text.strip()
        diplomas.append((diploma_id, author, summary))
    return publication_date, availability_date, series, number_in_series, supplement, eli, pdf_id, diplomas


def get_diploma(session, identifier):
    page = __get_page(session, DRE_PUBLICATION.format(identifier=identifier))
    __strip_icons(page)

    issuer = page.find('li', class_='emissor.designacao').text
    diploma_type = page.find('li', class_='tipoDiploma.tipo').text
    number = page.find('li', class_='numero').text
    pages = page.find('li', class_='paginas').text
    date = page.find('div', class_='dr-subtitle').text.split()[-1]
    assert '' not in (issuer, diploma_type, number, pages)
    number = number.split('/')[0]
    pages = pages.split('-')
    pages = int(pages[0]), int(pages[1])
    date = datetime.datetime.strptime(date, DATE_FORMAT)

    eli = __get_page_eli(page)
    pdf_url = __get_page_pdf_url(page)
    summary_elem = list(page.find('li', class_='formatedSumarioWithLinks').children)[1]
    assert summary_elem.name == 'p'
    summary = summary_elem.text

    text_elem = list(page.find('li', class_='formatedTextoWithLinks').children)[3]
    assert text_elem.name == 'div'
    raw_content = str(text_elem)
    return issuer, date, diploma_type, number, pages, eli, pdf_url, summary, raw_content


def __get_page(session, url):
    response = session.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def __strip_icons(page):
    for element in page.find_all('i', class_='fa'):
        parent = element.parent
        if parent.name == 'span':
            parent.decompose()


def __get_page_eli(page):
    element = page.find('a', href=RE_ELI)
    if element is not None:
        return element.text


def __get_page_pdf_url(page):
    return page.find('a', href=RE_DRE_PDF).attrs['href']
