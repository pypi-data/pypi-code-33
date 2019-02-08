import os


NCBI_URL = 'http://www.ncbi.nlm.nih.gov'

EUTILS_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'


def build_article_url(id, source='pubmed'):
    if source.lower() == 'pmc':
        return os.path.join(NCBI_URL, source, 'articles', 'PMC{0}'.format(id))
    else:
        return os.path.join(NCBI_URL, source, str(id))


def build_efetch_url(id, source='pubmed', mode='xml'):
    params = '?db={0}&id={1}&retmode={2}'.format(source, str(id), mode)
    return os.path.join(EUTILS_URL, 'efetch.fcgi', params)


def build_esummary_url(id, source='pubmed', mode='json'):
    params = '?db={0}&id={1}&retmode={2}'.format(source, str(id), mode)
    return os.path.join(EUTILS_URL, 'esummary.fcgi', params)
