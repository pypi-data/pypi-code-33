# coding: utf-8
from __future__ import unicode_literals

from spacy.vocab import Vocab
from spacy.tokens import Doc
import pytest

from ..util import get_doc


def test_spans_merge_tokens(en_tokenizer):
    text = "Los Angeles start."
    heads = [1, 1, 0, -1]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert len(doc) == 4
    assert doc[0].head.text == "Angeles"
    assert doc[1].head.text == "start"
    doc.merge(0, len("Los Angeles"), tag="NNP", lemma="Los Angeles", ent_type="GPE")
    assert len(doc) == 3
    assert doc[0].text == "Los Angeles"
    assert doc[0].head.text == "start"

    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert len(doc) == 4
    assert doc[0].head.text == "Angeles"
    assert doc[1].head.text == "start"
    doc.merge(0, len("Los Angeles"), tag="NNP", lemma="Los Angeles", label="GPE")

    assert len(doc) == 3
    assert doc[0].text == "Los Angeles"
    assert doc[0].head.text == "start"
    assert doc[0].ent_type_ == "GPE"


def test_spans_merge_heads(en_tokenizer):
    text = "I found a pilates class near work."
    heads = [1, 0, 2, 1, -3, -1, -1, -6]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert len(doc) == 8
    with doc.retokenize() as retokenizer:
        attrs = {"tag": doc[4].tag_, "lemma": "pilates class", "ent_type": "O"}
        retokenizer.merge(doc[3:5], attrs=attrs)
    assert len(doc) == 7
    assert doc[0].head.i == 1
    assert doc[1].head.i == 1
    assert doc[2].head.i == 3
    assert doc[3].head.i == 1
    assert doc[4].head.i in [1, 3]
    assert doc[5].head.i == 4


def test_spans_merge_non_disjoint(en_tokenizer):
    text = "Los Angeles start."
    doc = en_tokenizer(text)
    with pytest.raises(ValueError):
        with doc.retokenize() as retokenizer:
            retokenizer.merge(
                doc[0:2],
                attrs={"tag": "NNP", "lemma": "Los Angeles", "ent_type": "GPE"},
            )
            retokenizer.merge(
                doc[0:1],
                attrs={"tag": "NNP", "lemma": "Los Angeles", "ent_type": "GPE"},
            )


def test_span_np_merges(en_tokenizer):
    text = "displaCy is a parse tool built with Javascript"
    heads = [1, 0, 2, 1, -3, -1, -1, -1]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)

    assert doc[4].head.i == 1
    doc.merge(
        doc[2].idx, doc[4].idx + len(doc[4]), tag="NP", lemma="tool", ent_type="O"
    )
    assert doc[2].head.i == 1

    text = "displaCy is a lightweight and modern dependency parse tree visualization tool built with CSS3 and JavaScript."
    heads = [1, 0, 8, 3, -1, -2, 4, 3, 1, 1, -9, -1, -1, -1, -1, -2, -15]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)

    ents = [(e[0].idx, e[-1].idx + len(e[-1]), e.label_, e.lemma_) for e in doc.ents]
    for start, end, label, lemma in ents:
        merged = doc.merge(start, end, tag=label, lemma=lemma, ent_type=label)
        assert merged is not None, (start, end, label, lemma)

    text = "One test with entities like New York City so the ents list is not void"
    heads = [1, 11, -1, -1, -1, 1, 1, -3, 4, 2, 1, 1, 0, -1, -2]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    for span in doc.ents:
        merged = doc.merge()
        assert merged is not None, (span.start, span.end, span.label_, span.lemma_)


def test_spans_entity_merge(en_tokenizer):
    # fmt: off
    text = "Stewart Lee is a stand up comedian who lives in England and loves Joe Pasquale.\n"
    heads = [1, 1, 0, 1, 2, -1, -4, 1, -2, -1, -1, -3, -10, 1, -2, -13, -1]
    tags = ["NNP", "NNP", "VBZ", "DT", "VB", "RP", "NN", "WP", "VBZ", "IN", "NNP", "CC", "VBZ", "NNP", "NNP", ".", "SP"]
    ents = [(0, 2, "PERSON"), (10, 11, "GPE"), (13, 15, "PERSON")]
    # fmt: on
    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab, words=[t.text for t in tokens], heads=heads, tags=tags, ents=ents
    )
    assert len(doc) == 17
    for ent in doc.ents:
        label, lemma, type_ = (
            ent.root.tag_,
            ent.root.lemma_,
            max(w.ent_type_ for w in ent),
        )
        ent.merge(label=label, lemma=lemma, ent_type=type_)
    # check looping is ok
    assert len(doc) == 15


def test_spans_entity_merge_iob():
    # Test entity IOB stays consistent after merging
    words = ["a", "b", "c", "d", "e"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [
        (doc.vocab.strings.add("ent-abc"), 0, 3),
        (doc.vocab.strings.add("ent-d"), 3, 4),
    ]
    assert doc[0].ent_iob_ == "B"
    assert doc[1].ent_iob_ == "I"
    assert doc[2].ent_iob_ == "I"
    assert doc[3].ent_iob_ == "B"
    doc[0:1].merge()
    assert doc[0].ent_iob_ == "B"
    assert doc[1].ent_iob_ == "I"

    words = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [
        (doc.vocab.strings.add("ent-de"), 3, 5),
        (doc.vocab.strings.add("ent-fg"), 5, 7),
    ]
    assert doc[3].ent_iob_ == "B"
    assert doc[4].ent_iob_ == "I"
    assert doc[5].ent_iob_ == "B"
    assert doc[6].ent_iob_ == "I"
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[2:4])
        retokenizer.merge(doc[4:6])
        retokenizer.merge(doc[7:9])
    for token in doc:
        print(token)
        print(token.ent_iob)
    assert len(doc) == 6
    assert doc[3].ent_iob_ == "B"
    assert doc[4].ent_iob_ == "I"


def test_spans_sentence_update_after_merge(en_tokenizer):
    # fmt: off
    text = "Stewart Lee is a stand up comedian. He lives in England and loves Joe Pasquale."
    heads = [1, 1, 0, 1, 2, -1, -4, -5, 1, 0, -1, -1, -3, -4, 1, -2, -7]
    deps = ['compound', 'nsubj', 'ROOT', 'det', 'amod', 'prt', 'attr',
            'punct', 'nsubj', 'ROOT', 'prep', 'pobj', 'cc', 'conj',
            'compound', 'dobj', 'punct']
    # fmt: on

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)
    sent1, sent2 = list(doc.sents)
    init_len = len(sent1)
    init_len2 = len(sent2)
    doc[0:2].merge(label="none", lemma="none", ent_type="none")
    doc[-2:].merge(label="none", lemma="none", ent_type="none")
    assert len(sent1) == init_len - 1
    assert len(sent2) == init_len2 - 1


def test_spans_subtree_size_check(en_tokenizer):
    # fmt: off
    text = "Stewart Lee is a stand up comedian who lives in England and loves Joe Pasquale"
    heads = [1, 1, 0, 1, 2, -1, -4, 1, -2, -1, -1, -3, -10, 1, -2]
    deps = ["compound", "nsubj", "ROOT", "det", "amod", "prt", "attr",
            "nsubj", "relcl", "prep", "pobj", "cc", "conj", "compound",
            "dobj"]
    # fmt: on

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)
    sent1 = list(doc.sents)[0]
    init_len = len(list(sent1.root.subtree))
    doc[0:2].merge(label="none", lemma="none", ent_type="none")
    assert len(list(sent1.root.subtree)) == init_len - 1
