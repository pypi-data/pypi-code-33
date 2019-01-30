from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    # hgvs
    "chr": "chr",
    "start": "start",
    "ref": "ref",
    "alt": "alt",
    "build": "build",
    # info
    "CNT__int": "info.CNT",
    "gene": "info.GENE",
    "CDS__string": "info.CDS",
    "AA__string": "info.AA",
    "ID__string": "info.ID",
    "tissues__mstring": "info.TISSUES",
    "resistance_mutation__mstring": "info.RESISTANCE_MUTATION",
    "tissue_frequency__mstring": "info.TISSUE_FREQ",
}

register(
    input_type=DocType.CALL,
    output_type=DocType.COSMIC,
    transformer=compose(
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.COSMIC.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.COSMIC,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.COSMIC.value)),
    is_header=True,
)
