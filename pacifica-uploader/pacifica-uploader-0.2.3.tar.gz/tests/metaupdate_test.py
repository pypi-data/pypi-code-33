#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module used to test the MetaUpdate module."""
from unittest import TestCase
from pacifica.uploader.metadata.metaupdate import MetaUpdate
from pacifica.uploader.metadata.metadata import MetaObj


class TestMetaUpdate(TestCase):
    """Test the MetaUpdate class."""

    def test_update_parents_nil_result(self):
        """Test the MetaUpdate update_parents method with no results."""
        md_update = MetaUpdate('bjohn')
        md_update.append(
            MetaObj(
                destinationTable='Transactions.submitter',
                displayFormat='%(first_name)s %(last_name)s',
                displayTitle='Currently Logged On',
                displayType='logged_on',
                metaID='logon',
                queryDependency={'network_id': 'logon'},
                queryFields=['first_name', 'last_name', '_id'],
                sourceTable='users',
                value='bjohn',
                valueField='_id'
            )
        )
        md_update.append(
            MetaObj(
                destinationTable='Transactions.instrument',
                displayFormat='%(_id)s %(name_short)s - %(display_name)s',
                displayTitle='Instrument',
                displayType='select',
                metaID='instrumentByID',
                queryDependency={},
                queryFields=['display_name', 'name_short', '_id'],
                sourceTable='instruments',
                value=None,
                valueField='_id'
            )
        )
        md_update.update_parents('instrumentByID')
        self.assertFalse(md_update[1].value)

    def test_auth_accessor(self):
        """Get the auth from the md_update to verify defaults."""
        md_update = MetaUpdate('bjohn')
        self.assertEqual(md_update.get_auth(), {})

    def test_update_parents(self):
        """Test the MetaUpdate update_parents method."""
        md_update = MetaUpdate('dmlb2001')
        md_update.append(
            MetaObj(
                destinationTable='Transactions.submitter',
                displayFormat='%(first_name)s %(last_name)s',
                displayTitle='Currently Logged On',
                displayType='logged_on',
                metaID='logon',
                queryDependency={'network_id': 'logon'},
                queryFields=['first_name', 'last_name', '_id'],
                sourceTable='users',
                value='dmlb2001',
                valueField='_id'
            )
        )
        md_update.append(
            MetaObj(
                destinationTable='Transactions.instrument',
                displayFormat='%(_id)s %(name_short)s - %(display_name)s',
                displayTitle='Instrument',
                displayType='select',
                metaID='instrumentByID',
                queryDependency={'_id': 'instrumentByID'},
                queryFields=['display_name', 'name_short', '_id'],
                sourceTable='instruments',
                value=54,
                valueField='_id'
            )
        )
        md_update.append(
            MetaObj(
                destinationTable='Transactions.proposal',
                displayFormat='%(_id)s %(title)s',
                displayTitle='Proposal',
                displayType='select',
                metaID='ProposalByInstrument',
                queryDependency={'instrument_id': 'instrumentByID'},
                queryFields=['title', '_id'],
                sourceTable='proposals',
                value=None,
                valueField='_id'
            )
        )
        md_update.append(
            MetaObj(
                displayFormat=u'Proposal ID {_id}',
                directoryOrder=0,
                displayType='directoryTree',
                metaID='ProposalIDDirectory',
                queryDependency={'_id': 'ProposalByInstrument'},
                queryFields=['_id'],
                sourceTable='proposals',
                value=None,
                valueField='_id'
            )
        )
        md_update.append(
            MetaObj(
                displayFormat=u'Proposal Title ({title})',
                directoryOrder=1,
                displayType='directoryTree',
                metaID='ProposalTitleDirectory',
                queryDependency={'_id': 'ProposalByInstrument'},
                queryFields=['_id', 'title'],
                sourceTable='proposals',
                value=None,
                valueField='_id'
            )
        )
        md_update.update_parents('ProposalIDDirectory')
        md_update.update_parents('ProposalTitleDirectory')
        self.assertTrue(md_update['ProposalByInstrument'].value)
        self.assertEqual(md_update['ProposalIDDirectory'].value, u'1234a')
        self.assertEqual(
            md_update.directory_prefix(),
            u'Proposal ID 1234a/Proposal Title (Pacifica D\xe9velopment (active no close))'
        )
        self.assertTrue(md_update.is_valid())
