import xmltodict


def parse_efetch(efetch, esummary, identifier):
    """Parses XML response from eutils efetch API

    Arguments:
        efetch (str): XML from efetch
        esummary (dict): JSON from esummary
        identifier (int): eutils identifier

    Returns:
        dict: Python dict with details of article
    """

    efetch = xmltodict.parse(efetch)
    esummary = esummary.get('result', {}).get(str(identifier), {})

    title = esummary.get('title')
    journal = esummary.get('source')
    date = esummary.get('pubdate')
    first_author = esummary.get('sortfirstauthor')

    authors = []
    for author in esummary.get('authors', []):
        authors.append(author.get('name'))

    abstract_obj = efetch \
        .get('PubmedArticleSet', {}) \
        .get('PubmedArticle', {}) \
        .get('MedlineCitation', {}) \
        .get('Article', {}) \
        .get('Abstract', {})

    abstract = ''
    for key, value in abstract_obj.items():
        if key == 'AbstractText':
            if type(value) == str:
                abstract += '{0} '.format(value)

            if type(value) == list:
                for item in value:
                    for text_key, text in item.items():
                        if text_key in ['@Label', '#text']:
                            abstract += '{0} '.format(text)

    return {
        'title': title,
        'journal': journal,
        'date': date,
        'first_author': first_author,
        'authors': authors,
        'abstract': abstract,
    }
