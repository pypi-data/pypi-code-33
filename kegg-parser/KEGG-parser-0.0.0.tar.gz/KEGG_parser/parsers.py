"""Parsers"""


def split_entry(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split()[0]
    return current_dict

def split_name(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data.split(', ')
    return current_dict

def return_self(current_dict, current_entry_name, current_entry_data):
    current_dict[current_entry_name] = current_entry_data
    return current_dict

def split_and_append(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split()
    current_entry_pathway_id = split_current_entry_data[0]
    current_entry_pathway_name = ' '.join(split_current_entry_data[1:])

    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = list()

    current_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
    return current_dict

def add_class(current_dict, current_entry_name, current_entry_data):
    if current_entry_name in current_dict:
        current_dict[current_entry_name].append(current_entry_data)
    else:
        current_dict[current_entry_name] = [current_entry_data]
    return current_dict

def add_nested_dict(current_dict, current_entry_name, current_entry_data):
    split_current_entry_data = current_entry_data.split(': ')
    if current_entry_name not in current_dict:
        current_dict[current_entry_name] = dict()
    current_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
    return current_dict

PARSE_KO_BY_FIELD = {
    'ENTRY': split_entry, 'NAME': split_name, 'DEFINITION': return_self,
    'PATHWAY': split_and_append, 'MODULE': split_and_append, 'DISEASE': split_and_append,
    'CLASS': add_class, 'DBLINKS': add_nested_dict, 'GENES': add_nested_dict
}

NOT_CAPTURED_KO_FIELDS = ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL', 'SEQUENCE', 'BRITE')

def parse_ko(ko_raw_record):
    ko_dict = dict()
    past_entry = None
    for line in ko_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()

        if current_entry_name is '':
            current_entry_name = past_entry

        current_entry_data = line[12:].strip()

        if current_entry_name is not '':
            if current_entry_name in PARSE_KO_BY_FIELD:
                ko_dict = PARSE_KO_BY_FIELD[current_entry_name](ko_dict, current_entry_name, current_entry_data)

            elif current_entry_name not in NOT_CAPTURED_KO_FIELDS and current_entry_name not in PARSE_KO_BY_FIELD:
                raise ValueError('What is %s in %s?' % (current_entry_name, ko_dict['ENTRY']))

        past_entry = current_entry_name

    return ko_dict


def parse_rn(rn_raw_record):
    rn_dict = dict()
    past_entry = None
    for line in rn_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            rn_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name in ('NAME', 'DEFINITION', 'REMARK', 'COMMENT', 'ENZYME'):
            rn_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'RPAIR':
            rn_dict[current_entry_name] = current_entry_data.split()
        elif current_entry_name == 'DEFINITION' or current_entry_name == 'EQUATION':
            equation_split = current_entry_data.split(' <=> ')
            if len(equation_split) != 2:
                raise ValueError("Equation does not have two parts: %s" % current_entry_data)
            reactants = equation_split[0].strip().split(' + ')
            reactants = [reactant.strip().split()[-1][:6] for reactant in reactants]
            products = equation_split[1].strip().split(' + ')
            products = [product.strip().split()[-1][:6] for product in products]
            rn_dict[current_entry_name] = [reactants, products]
        elif current_entry_name in ('RCLASS', 'PATHWAY', 'ORTHOLOGY', 'MODULE'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in rn_dict:
                rn_dict[current_entry_name] = list()
            rn_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in rn_dict:
                rn_dict[current_entry_name] = dict()
                rn_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        else:
            raise ValueError('What is %s in %s?' % (current_entry_name, rn_dict['ENTRY']))
        past_entry = current_entry_name
    return rn_dict


def parse_co(co_raw_record):
    co_dict = dict()
    past_entry = None
    for line in co_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            co_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name == 'NAME':
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = current_entry_data
            else:
                co_dict[current_entry_name] += ' %s' % current_entry_data
        elif current_entry_name in ('FORMULA', 'EXACT_MASS', 'MOL_WEIGHT', 'REMARK', 'COMMENT', 'COMPOSITION', 'MASS'):
            co_dict[current_entry_name] = current_entry_data
        elif current_entry_name in ('REACTION', 'ENZYME'):
            if current_entry_name in co_dict:
                co_dict[current_entry_name] += current_entry_data.split()
            else:
                co_dict[current_entry_name] = current_entry_data.split()
        elif current_entry_name in ('PATHWAY', 'MODULE', 'ORTHOLOGY'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                co_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        # Structural information we are currently ignoring
        elif current_entry_name in ('BRITE', 'ATOM', 'BOND', 'BRACKET', 'ORIGINAL', 'REPEAT'):
            pass
        # Glycan structal information we are currently ignoring
        elif current_entry_name in ('NODE', 'EDGE'):
            pass
        # Protein information we are currently ignoring
        elif current_entry_name in ('SEQUENCE', 'GENE', 'ORGANISM', 'TYPE'):
            pass
        # Drug information we are currently ignoring
        elif current_entry_name in ('EFFICACY', 'PRODUCT', 'CLASS', 'DISEASE', 'TARGET', 'METABOLISM', 'INTERACTION',
                                    'STR_MAP'):
            pass
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in co_dict:
                co_dict[current_entry_name] = dict()
                co_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        # Reference information we are currently ignoring
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        else:
            raise ValueError('What is %s in %s?' % (current_entry_name, co_dict['ENTRY']))
        past_entry = current_entry_name
    return co_dict


def parse_pathway(pathway_raw_record):
    pathway_dict = dict()
    past_entry = None
    for line in pathway_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            pathway_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name in ('NAME', 'DESCRIPTION', 'KO_PATHWAY'):
            pathway_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'CLASS':
            pathway_dict[current_entry_name] = [(i[:5], i[6:]) for i in current_entry_data.split('; ')]
        elif current_entry_name in ('PATHWAY_MAP', 'MODULE', 'DISEASE', 'DRUG', 'ORTHOLOGY', 'COMPOUND', 'REL_PATHWAY',
                                    'REACTION', 'ENZYME'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in pathway_dict:
                pathway_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                pathway_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        # Protein information we are currently ignoring
        elif current_entry_name in ('GENE', 'ORGANISM'):
            pass
        elif current_entry_name == 'DBLINKS':
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in pathway_dict:
                pathway_dict[current_entry_name] = dict()
                pathway_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        elif current_entry_name in ('REFERENCE', 'AUTHORS', 'TITLE', 'JOURNAL'):
            pass
        elif current_entry_name != current_entry_name.upper():
            pass
        else:
            raise ValueError('What is %s in %s?' % (line, pathway_dict['ENTRY']))
        past_entry = current_entry_name
    return pathway_dict


def parse_organism(gene_raw_record):
    gene_dict = dict()
    past_entry = None
    for line in gene_raw_record.strip().split('\n'):
        current_entry_name = line[:12].strip()
        if current_entry_name == '':
            current_entry_name = past_entry
        current_entry_data = line[12:].strip()
        if current_entry_name == 'ENTRY':
            gene_dict[current_entry_name] = current_entry_data.split()[0]
        elif current_entry_name == 'NAME':
            gene_dict[current_entry_name] = current_entry_data.split(', ')
        elif current_entry_name in ('DEFINITION', 'POSITION'):
            gene_dict[current_entry_name] = current_entry_data
        elif current_entry_name == 'ORTHOLOGY':
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            gene_dict[current_entry_name] = (current_entry_pathway_id, current_entry_pathway_name)
        elif current_entry_name in ('PATHWAY', 'DISEASE'):
            split_current_entry_data = current_entry_data.split()
            current_entry_pathway_id = split_current_entry_data[0]
            current_entry_pathway_name = ' '.join(split_current_entry_data[1:])
            if current_entry_name not in gene_dict:
                gene_dict[current_entry_name] = [(current_entry_pathway_id, current_entry_pathway_name)]
            else:
                gene_dict[current_entry_name].append((current_entry_pathway_id, current_entry_pathway_name))
        elif current_entry_name == 'CLASS':
            if current_entry_name in gene_dict:
                gene_dict[current_entry_name].append(current_entry_data)
            else:
                gene_dict[current_entry_name] = [current_entry_data]
        elif current_entry_name in ('DRUG_TARGET', 'MOTIF', 'DBLINKS', 'STRUCTURE'):
            split_current_entry_data = current_entry_data.split(': ')
            if current_entry_name not in gene_dict:
                gene_dict[current_entry_name] = dict()
                gene_dict[current_entry_name][split_current_entry_data[0]] = split_current_entry_data[1].split()
        # Sequence information I am currently ignoring
        elif current_entry_name in ('AASEQ', 'NTSEQ'):
            pass
        elif current_entry_name != current_entry_name.upper():
            pass
        else:
            raise ValueError('What is %s in %s?' % (line, gene_dict['ENTRY']))
        past_entry = current_entry_name
    return gene_dict
