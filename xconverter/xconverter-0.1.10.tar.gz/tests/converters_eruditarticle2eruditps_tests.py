import unittest
import os

from lxml import etree

from converter import converters

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class TestEruditArticle2EruditPS(unittest.TestCase):

    def setUp(self):

        self.conv = converters.EruditArticle2EruditPS(
            source=APP_PATH + '/fixtures/eruditarticle/document_eruditarticle.xml'
        )

        self.xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

    def test_article_issue_id(self):

        seq = self.xml.find('front/article-meta/issue-id').text
        self.assertEqual(seq, 'approchesind01463')

    def test_article_issue_seq_1(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <volume>1</volume>
                <nonumero>1</nonumero>
                ...
            </numero>
            ...
        """

        seq = self.xml.find('front/article-meta/issue').get('seq')
        self.assertEqual(seq, '6')

        seq = self.xml.find('front/article-meta/volume').get('seq')
        self.assertEqual(seq, None)

    def test_article_issue_seq_2(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <volume>1</volume>
                ...
            </numero>
            ...
        """
        num = self.conv.source_etree.find("admin/numero/nonumero")
        num.getparent().remove(num)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        seq = custom_xml.find('front/article-meta/volume').get('seq')

        self.assertEqual(seq, '6')

    def test_article_issue_seq_3(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <nonumero>1</nonumero>
                ...
            </numero>
            ...
        """
        num = self.conv.source_etree.find("admin/numero/volume")
        num.getparent().remove(num)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        seq = custom_xml.find('front/article-meta/issue').get('seq')

        self.assertEqual(seq, '6')

    def test_article_element_attributes(self):

        typeart = self.xml.find('.').get('article-type')
        self.assertEqual(typeart, 'research-article')

        lang = self.xml.find('.').get('{http://www.w3.org/XML/1998/namespace}lang')
        self.assertEqual(lang, 'fr')

    def test_journal_id_erudit(self):

        result = self.xml.find("front/journal-meta/journal-id[@journal-id-type='publisher-id']").text

        self.assertEqual(result, 'approchesind0522')

    def test_journal_title(self):

        result = self.xml.find("front/journal-meta/journal-title-group/journal-title").text

        self.assertEqual(result, 'Approches inductives')

    def test_journal_subtitle(self):

        result = self.xml.find("front/journal-meta/journal-title-group/journal-subtitle").text

        self.assertEqual(result, 'Travail intellectuel et construction des connaissances')

    def test_abbrev_journal_title(self):

        result = self.xml.find("front/journal-meta/journal-title-group/abbrev-journal-title").text

        self.assertEqual(result, 'approchesind')

    def test_issns(self):

        result = ';'.join(
            sorted(['%s-%s' % (i.get('pub-type'), i.text) for i in self.xml.xpath("front/journal-meta//issn")])
        )

        self.assertEqual(result, 'epub-2292-0005')

    def test_issns_ppub_epub(self):

        self.conv.source_etree.find("admin/revue").append(etree.Element('idissn'))
        self.conv.source_etree.find("admin/revue/idissn").text = '1234-4321'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = ';'.join(
            sorted(['%s-%s' % (i.get('pub-type'), i.text) for i in custom_xml.xpath("front/journal-meta//issn")])
        )

        self.assertEqual(result, 'epub-2292-0005;ppub-1234-4321')

    def test_journal_contrib_group_manager(self):

        result = self.xml.xpath("front/journal-meta/contrib-group[@content-type='manager']")

        result_surname = [i.text for i in result[0].xpath('.//surname')]
        result_givennames = [i.text for i in result[0].xpath('.//given-names')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_journal_contrib_group_editeur(self):

        result = self.xml.xpath("front/journal-meta/contrib-group[@content-type='editor']")

        result_surname = [i.text for i in result[0].xpath('.//surname')]
        result_givennames = [i.text for i in result[0].xpath('.//given-names')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_publisher_name(self):

        result = self.xml.find("front/journal-meta/publisher/publisher-name").text

        self.assertEqual(result, 'Université du Québec à Trois-Rivières')

    def test_article_meta_article_id_doi(self):

        result = ['%s-%s' % (i.get('pub-id-type'), i.text) for i in self.xml.xpath("front/article-meta/article-id")]

        self.assertEqual(result, ['doi-10.7202/1025748ar', 'publisher-id-1025748ar'])

    def test_article_meta_article_id_publisher(self):

        result = self.xml.find("front/article-meta/article-id[@pub-id-type='publisher-id']").text

        self.assertEqual(result, '1025748ar')

    def test_article_meta_title_group_article_categories_level_1(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group/subject").text

        self.assertEqual(
            result,
            'Articles'
        )

    def test_article_meta_title_group_article_categories_level_2(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group/subj-group/subject").text

        self.assertEqual(
            result,
            'Review Articles'
        )

    def test_article_meta_title_group_article_categories_level_3(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group/subj-group/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Report'
        )

    def test_article_meta_title_group_article_categories_trans_level_1(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subject").text

        self.assertEqual(
            result,
            'Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_2(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Review Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_3(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subj-group/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Report english'
        )

    def test_article_meta_title_group_title(self):

        result = self.xml.find("front/article-meta/title-group/article-title[@{http://www.w3.org/XML/1998/namespace}lang='fr']")
        self.maxDiff = None
        expected = '<article-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">« Chantez au Seigneur un chant nouveau… » (Ps.95.1) : le portrait de la musique <italic>rock</italic> chrétienne</article-title>'
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_subtitle(self):

        result = self.xml.find(
            "front/article-meta/title-group/subtitle[@{http://www.w3.org/XML/1998/namespace}lang='fr']"
        )

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            '<subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">Article <italic>Subtitle</italic></subtitle>'
        )

    def test_article_meta_title_group_title_1(self):
        """
        parsing Érudit Article without title and with trefbiblio
        titre: absent
        trefbiblio: present
        """

        # Customizing Érudit Article XML
        titre = self.conv.source_etree.find("liminaire/grtitre/titre")
        self.conv.source_etree.find("liminaire/grtitre").remove(titre)
        trefbiblio = etree.Element('trefbiblio')
        trefbiblio.text = 'Titre Ref Biblio'
        self.conv.source_etree.find("liminaire/grtitre").append(trefbiblio)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        self.maxDiff = None
        result = custom_xml.find("front/article-meta/title-group/article-title[@{http://www.w3.org/XML/1998/namespace}lang='fr']")

        expected = '<article-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">Titre Ref Biblio</article-title>'
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_title_2(self):
        """
        parsing Érudit Article without title and with trefbiblio
        titre: present
        trefbiblio: present
        """

        # Customizing Érudit Article XML
        trefbiblio = etree.Element('trefbiblio')
        trefbiblio.text = 'Titre Ref Biblio'
        self.conv.source_etree.find("liminaire/grtitre").append(trefbiblio)
        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)
        result = custom_xml.find("front/article-meta/title-group/article-title[@{http://www.w3.org/XML/1998/namespace}lang='fr']")
        expected = '<article-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">« Chantez au Seigneur un chant nouveau… » (Ps.95.1) : le portrait de la musique <italic>rock</italic> chrétienne (Titre Ref Biblio)</article-title>'
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_translated_title(self):

        result = self.xml.findall("front/article-meta/title-group//trans-title-group/trans-title")

        result = [etree.tostring(i) for i in result]

        expected = [
            b"""<trans-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated title in <italic>english</italic></trans-title>""",
            b"""<trans-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated title in <italic>portuguese</italic></trans-title>"""
        ]

        self.assertEqual(
            sorted(result),
            sorted(expected)
        )

    def test_article_meta_title_group_translated_subtitle(self):

        result = self.xml.findall(
            "front/article-meta/title-group//trans-title-group/trans-subtitle"
        )

        result = [etree.tostring(i) for i in result]
        expected = [
            b"""<trans-subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated subtitle in <italic>english</italic></trans-subtitle>""",
            b"""<trans-subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated subtitle in <italic>portuguese</italic></trans-subtitle>"""
        ]
        self.assertEqual(
            sorted(result),
            sorted(expected)
        )

    def test_article_meta_contrib_group_num_authors(self):

        result = len(self.xml.xpath("front/article-meta/contrib-group/contrib"))

        self.assertEqual(result, 5)

    def test_article_meta_contrib_group_content(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group//contrib/name/surname")]

        self.assertEqual(result, ['Falardeau', 'Perreault', 'François', 'Marine', 'Joseph'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group//contrib/name/given-names")]

        self.assertEqual(result, ['Marie-Chantal', 'Stéphane Marie', 'Rémy', 'Alexandre', 'Joseph'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/name/suffix")]

        self.assertEqual(result, ['Jr.'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/name/prefix")]

        self.assertEqual(result, ['Sr.'])

    def test_article_meta_contrib_group_contrib_author_alias(self):
        """
        Testing author having a alias.

        Input:
        <auteur id="au1">
            <nompers typenompers="usage">
                <prenom>Kurt</prenom>
                <nomfamille>Tucholsky</nomfamille>
            </nompers>
            <nompers typenompers="pseudonyme">
                <prenom>Peter Panter</prenom>
            </nompers>
        </auteur>
        """

        nompers = etree.Element('nompers', typenompers="pseudonyme")
        prenom = etree.Element('prenom')
        prenom.text = "Peter Panter"
        nomfamille = etree.Element('nomfamille')
        nomfamille.text = "The Peter"
        nompers.append(prenom)
        nompers.append(nomfamille)
        item = self.conv.source_etree.find("liminaire/grauteur/auteur[@id='au1']")
        item.append(nompers)
        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find(
            "front/article-meta/contrib-group/contrib/[@id='au1']/string-name[@content-type='alias']"
        ).text


        self.assertEqual(result, "Peter Panter The Peter")

    def test_article_meta_contrib_group_contrib_xref(self):

        result = [i.get('rid') for i in self.xml.xpath("front/article-meta/contrib-group//xref")]

        self.assertEqual(result, ['aff1', 'aff2', 'aff2', 'aff2'])

    def test_article_meta_contrib_email(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/email")]

        self.assertEqual(result, ['falardeau_fake@email.com'])

    def test_article_meta_contrib_ext_link(self):

        result = [i.get('{http://www.w3.org/1999/xlink}href') for i in self.xml.xpath("front/article-meta/contrib-group/contrib/ext-link")]

        self.assertEqual(result, ['http://mysite.fake.com'])

    def test_article_meta_contrib_id(self):

        result = [i.get('id') for i in self.xml.xpath("front/article-meta/contrib-group/contrib")]

        self.assertEqual(result, ['au1', 'au2', 'au3', 'au4', 'au5'])

    def test_article_meta_contrib_bio(self):

        result = self.xml.xpath("front/article-meta/contrib-group/contrib[@id='au1']/bio")

        expected = b"""<bio xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr"><title>Auteur Bio</title><p><bold><sc>Nancy R. Lange </sc></bold>a publi&#233; quatre recueils de po&#233;sie aux &#201;crits des Forges : <italic>Annabah&#233;bec, Femelle Faucon</italic>, <italic>Reviens chanter rossignol </italic>et <italic>Au seuil du bleu </italic>(voir p. 95). Elle a publi&#233; des po&#232;mes dans des collectifs (<italic>Ch&#226;teau Bizarre</italic>; voir p. 104) et en revue (<italic>Br&#232;ves litt&#233;raires </italic>79, 80<italic>, Exit, Arcade, Estuaire, Moebius</italic>). Elle a collabor&#233; &#224; <italic>Macadam tribu</italic> et &#224; des spectacles multim&#233;dia, dont <italic>Au seuil du bleu</italic> (JMLDA et Sainte-Rose en Bleu 2009, des productions de la SLL; <italic>Br&#232;ves litt&#233;raires</italic> 80). Elle a particip&#233; &#224; deux autres activit&#233;s de la SLL en 2010 : Journ&#233;es de la culture (voir p. 36) et Sainte-Rose en Bleu (voir p. 15).\n        </p></bio>"""

        self.assertEqual(etree.tostring(result[0]), expected)

    def test_article_meta_aff(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/aff/institution")]

        self.assertEqual(result, ['Université du Québec à Trois-Rivières', 'Test Affiliation'])

    def test_article_pub_date(self):

        result = []
        for item in self.xml.xpath("front/article-meta/pub-date[@date-type='pub']"):

            dat = '-'.join([
                item.find('year').text or '',
                item.find('month').text or '',
                item.find('day').text or '',
            ])
            result.append(dat)

        self.assertEqual(result, ['2014-06-26'])

    def test_article_pub_date_publication_format(self):

        item = self.conv.source_etree.find("admin/numero/pubnum/date")
        item.set('typedate', 'pubpapier')

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/pub-date[@date-type='pub']").get('publication-format')

        self.assertEqual(result, 'ppub')

    def test_article_pub_date_without_publication_format(self):

        item = self.conv.source_etree.find("admin/numero/pubnum/date")
        del item.attrib['typedate']
        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/pub-date[@date-type='pub']")

        self.assertTrue('publication-format' not in result.attrib)

    def test_article_issue_volume(self):

        result = self.xml.find("front/article-meta/volume").text

        self.assertEqual(result, '1')

    def test_article_issue_number(self):

        result = self.xml.find("front/article-meta/issue").text

        self.assertEqual(result, '1')

    def test_article_issue_title(self):

        result = self.xml.find("front/article-meta/issue-title").text

        self.assertEqual(result, 'Approches inductives en communication sociale')

    def test_article_fpage(self):

        result = self.xml.find("front/article-meta/fpage").text

        self.assertEqual(result, '125')

    def test_article_lpage(self):

        result = self.xml.find("front/article-meta/lpage").text

        self.assertEqual(result, '148')

    def test_permissions_copyright_statement_1(self):

        inputxml = """
            <admin>
                <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, 2014</droitsauteur>
                <droitsauteur>
                    <liensimple xmlns:xlink="http://www.w3.org/1999/xlink" id="ls1" xlink:href="http://creativecommons.org/licenses/by-sa/3.0/" xlink:actuate="onRequest" xlink:show="replace" xlink:type="simple">
                        <objetmedia flot="ligne">
                            <image typeimage="forme" xlink:href="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" xlink:actuate="onLoad" xlink:show="embed" xlink:type="simple"/>
                        </objetmedia>
                    </liensimple>
                </droitsauteur>
            </admin>"""

        """<copyright-statement>Tous droits réservés © Approches Inductives, 2014</copyright-statement>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © Approches inductives , 2014</declaration>"
        )

    def test_permissions_copyright_statement_2(self):

        inputxml = """
            <admin>
                <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, 2014</droitsauteur>
            </admin>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © Approches inductives , 2014</declaration>"
        )

    def test_permissions_copyright_statement_3(self):

        inputxml = """
            <admin>
                <droitsauteur>
                    <declaration>Tous droits réservés ©</declaration>
                    <annee>2014</annee>
                    <nomorg>Approches inductives</nomorg>
                </droitsauteur>
            </admin>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © 2014 Approches inductives</declaration>"
        )

    def test_permissions_copyright_holder(self):

        result = self.xml.find("front/article-meta/permissions/copyright-holder").text

        self.assertEqual(result, "Approches inductives")

    def test_permissions_copyright_year(self):

        result = self.xml.find("front/article-meta/permissions/copyright-year").text

        self.assertEqual(result, "2014")

    def test_permissions_copyright_license_link(self):

        result = self.xml.find("front/article-meta/permissions/license").get('{http://www.w3.org/1999/xlink}href')

        self.assertEqual(result, "http://creativecommons.org/licenses/by-sa/3.0/")

    def test_permissions_copyright_license_link_image(self):

        result = self.xml.find("front/article-meta/permissions/license/license-p/graphic").get('{http://www.w3.org/1999/xlink}href')

        self.assertEqual(result, "http://i.creativecommons.org/l/by-sa/3.0/88x31.png")

    def test_abstract(self):

        result = self.xml.find("front/article-meta/abstract[@{http://www.w3.org/XML/1998/namespace}lang='fr']")

        expected = b"""<abstract xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr"><title>Resume</title><p>Le but de cet article est de pr&#233;senter les raisons du choix d&#8217;une approche inductive, plut&#244;t qu&#8217;une approche d&#233;ductive, afin d&#8217;&#233;tudier la musique rock chr&#233;tienne. Cette &#233;tude dresse un portrait des chansons les plus populaires de la musique rock chr&#233;tienne tout en d&#233;crivant quantitativement les &#233;l&#233;ments structurels de ces derni&#232;res. Afin de r&#233;aliser ce projet, nous avons r&#233;pertori&#233; tous les num&#233;ros un du palmar&#232;s am&#233;ricain <italic>Christian Songs</italic> depuis sa cr&#233;ation en 2003&#160;jusqu&#8217;&#224; la fin de l&#8217;ann&#233;e 2011, soit 65&#160;chansons. Le portrait de la musique rock chr&#233;tienne se d&#233;cline en onze cat&#233;gories dont les plus r&#233;currentes sont la d&#233;votion, la pr&#233;sence de Dieu et l&#8217;espoir. Cette musique est aussi chant&#233;e majoritairement par des hommes et se caract&#233;rise par un rythme lent.</p></abstract>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_trans_abstract(self):

        result = self.xml.find("front/article-meta/trans-abstract[@{http://www.w3.org/XML/1998/namespace}lang='en']")

        expected = b"""<trans-abstract xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="en"><title>Abstract</title><p>Abstract translation sample.</p></trans-abstract>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_keywords(self):

        result = self.xml.findall("front/article-meta/kwd-group[@{http://www.w3.org/XML/1998/namespace}lang='fr']/kwd")

        result = ';'.join([i.text for i in result])

        expected = "Étude mixte;méthodologie inductive;musique rock chrétienne;analyse de contenu"

        self.assertEqual(result, expected)

    def test_ref_count(self):

        result = self.xml.find("front/article-meta/counts/ref-count").get('count')

        self.assertEqual(result, '61')

    def test_table_count(self):

        result = self.xml.find("front/article-meta/counts/table-count").get('count')

        self.assertEqual(result, '6')

    def test_fig_count(self):

        result = self.xml.find("front/article-meta/counts/fig-count").get('count')

        self.assertEqual(result, '3')

    def test_equation_count(self):

        result = self.xml.find("front/article-meta/counts/equation-count").get('count')

        self.assertEqual(result, '3')

    def test_page_count_ppage_absent(self):
        pagination = self.conv.source_etree.find("admin/infoarticle/pagination")
        ppage = pagination.find('ppage')
        pagination.remove(ppage)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_dpage_absent(self):
        pagination = self.conv.source_etree.find("admin/infoarticle/pagination")
        dpage = pagination.find('dpage')
        pagination.remove(dpage)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_ppage_bigger_dpage_absent(self):
        ppage = self.conv.source_etree.find("admin/infoarticle/pagination/ppage")
        dpage = self.conv.source_etree.find("admin/infoarticle/pagination/dpage")
        ppage.text = '120'
        dpage.text = '100'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_ppage_not_number(self):
        ppage = self.conv.source_etree.find("admin/infoarticle/pagination/ppage")
        ppage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_dpage_not_number(self):
        dpage = self.conv.source_etree.find("admin/infoarticle/pagination/dpage")
        dpage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_paragraph_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='paragraph']").get('count')

        self.assertEqual(result, '32')

    def test_notes_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='note']").get('count')

        self.assertEqual(result, '6')

    def test_words_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='word']").get('count')

        self.assertEqual(result, '4952')

    def test_videos_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='video']").get('count')

        self.assertEqual(result, '0')

    def test_audios_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='audio']").get('count')

        self.assertEqual(result, '0')

    def test_media_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='media']").get('count')

        self.assertEqual(result, '8')

    def test_image_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='image']").get('count')

        self.assertEqual(result, '8')

    def test_ack(self):

        result = self.xml.find("back/ack")

        self.assertEqual(result.find('title').text, 'Merci')

        expected = b"""<ack xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><title>Merci</title><p>Cet <italic>article</italic> est une version modifi&#233;e d&#8217;un texte pr&#233;sent&#233; au s&#233;minaire HPES du CLERSE (Universit&#233; Lille I). Nous remercions Vincent Duwicquet, Jordan Melmi&#232;s et Jonathan Marie pour leurs commentaires, Malika Riboudt pour l&#8217;assistance technique sur Maple, Marc Lavoie et Louis-Philippe Rochon pour leurs conseils. Nous tenons &#233;galement &#224; faire part de notre gratitude aux rapporteurs de la revue pour leurs remarques pertinentes. N&#233;anmoins, nous demeurons seuls responsables des erreurs pouvant subsister.</p></ack>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_xref_fn(self):

        result = ['-'.join([i.get('ref-type'), i.get('rid'), i.text]) for i in self.xml.findall("body//xref[@ref-type='fn']")]

        expected = ['fn-no1-1', 'fn-no2-2', 'fn-no3-3', 'fn-no4-4', 'fn-no5-5', 'fn-no6-6']

        self.assertEqual(result, expected)

    def test_table_wrap_label(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('label').text.strip(), 'Tableau 1')

    def test_table_wrap_caption(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('caption/title').text.strip(), 'Synthèse des analyses de contenu aux États-Unis, 1969-2006')

    def test_table_wrap_alt_text(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('alt-text').text.strip(), 'Sample of table notes')

    def test_table_wrap_with_text_table(self):

        result = self.xml.find("body//table-wrap[@id='ta6']")

        expected = b'<table-wrap xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" id="ta6"><label>Tableau 4</label><caption xml:lang="fr"><title>Statistiques des &#233;difices et de leur destruction &#224; Lamaria</title></caption><table><colgroup><col align="left" valign="middle"/><col align="center"/><col align="center"/><col align="center"/></colgroup><thead><tr><th align="center" valign="middle">Maisons</th><th align="center">Secteur urbain</th><th align="center">Secteur rural</th><th align="center">Total</th></tr></thead><tfoot><tr><td align="right" valign="middle">Total</td><td align="right">4834</td><td align="right">2686</td><td align="right">7520</td></tr></tfoot><tbody><tr><td align="left" valign="middle">D&#233;truites</td><td align="center">1888</td><td align="center">1198</td><td align="center">3086</td></tr><tr><td align="left" valign="middle">Endommag&#233;es</td><td align="center">1342</td><td align="center">297</td><td align="center">1639</td></tr><tr><td align="left" valign="middle">Sous-total</td><td align="center">3230</td><td align="center">1495</td><td align="center">4725</td></tr><tr><td align="left" valign="middle">Intactes</td><td align="center">1604</td><td align="center">1191</td><td align="center">2795</td></tr></tbody></table></table-wrap>'

        self.maxDiff = None

        self.assertSequenceEqual(etree.tostring(result), expected)

    def test_table_wrap_attrib(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('attrib').text.strip(), 'Sample of source data')

    def test_table_wrap_graphic(self):

        result = self.xml.find("body//table-wrap[@id='ta1']/graphic")

        self.assertEqual(result.get('position').strip(), 'float')

        self.assertEqual(result.get('content-type').strip(), 'table')

        self.assertEqual(result.get('{http://www.w3.org/1999/xlink}href').strip(), 'image_tableau_1.png')

    def test_figure_label(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('label').text.strip(), 'Figure 1')

    def test_figure_caption(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('caption/title').text.strip(), 'Modèle des valeurs de Schwartz (1992)')

    def test_figure_alt_text(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('alt-text').text.strip(), 'Sample of figure notes')

    def test_figure_attrib(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('attrib').text.strip(), 'Sample of source data')

    def test_fig_graphic(self):

        result = self.xml.find("body//fig[@id='fi1']/graphic")

        self.assertEqual(result.get('position').strip(), 'float')

        self.assertEqual(result.get('content-type').strip(), 'figure')

        self.assertEqual(result.get('{http://www.w3.org/1999/xlink}href').strip(), 'image_figure_1.png')
