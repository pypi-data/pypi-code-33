###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that interfaces to the Installer class

:author: Ben Couturier
'''
import datetime
import os
import shutil
import subprocess
import tempfile
import urllib

from lbCVMFSscheduler.lbCVMFSexecutor.MonitoringGW import MonitoringGW


class CVMFSStats(object):

    volpath = "/var/spool/cvmfs/%s/"

    def __init__(self, volumename, with_gateway=False,
                 logger=None, log_filename=None):
        self.logger = logger
        self.with_gateway = with_gateway
        self.volpath = self.volpath % volumename
        self.volumename = volumename
        log_folder = os.environ.get('LOGDIR', os.environ.get('HOME', ''))
        self.log_filename = "%s/%s" % (log_folder, log_filename)

    def _inodeStats(self, path=None):
        if path is None:
            path = self.volpath
        p = subprocess.Popen(["df", "-i", path], stdout=subprocess.PIPE)
        output = p.communicate()[0]
        # df returns
        # Filesystem               Inodes   IUsed      IFree IUse% Mounted on
        # lhcbdev.cern.ch/data 1787870382 6103238 1781767144    1%
        # /var/spool/cvmfs/lhcbdev.cern.ch
        # so we keep the second line
        (fs, inodes_total, inodes_used, inodes_free, peruse, mountpoint) = \
            output.splitlines()[1].split()
        return (inodes_total, inodes_used, inodes_free)

    def _blockStats(self, path=None):
        if path is None:
            path = self.volpath
        p = subprocess.Popen(["df",  path], stdout=subprocess.PIPE)
        output = p.communicate()[0]
        # df returns
        # Filesystem            1K-blocks      Used Available Use% Mounted on
        # lhcbdev.cern.ch/data 1751685120 860828672 890856448  50% /
        # var/spool/cvmfs/lhcbdev.cern.ch
        # so we keep the second line
        (fs, blocks_total, blocks_used, blocks_free, peruse, mountpoint) = \
            output.splitlines()[1].split()
        return (blocks_total, blocks_used, blocks_free)

    def _getRootHash(self):
        p = subprocess.Popen(
            ["attr",
             "-g",
             "root_hash",
             "%s/rdonly/" % self.volpath],
            stdout=subprocess.PIPE)
        output = p.communicate()[0]
        res = output.splitlines()[1]
        return res

    def _getGWUrl(self):
        conf_file = '/etc/cvmfs/repositories.d/%s/client.conf' % \
                    self.volumename
        with open(conf_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('CVMFS_SERVER_URL='):
                    return line.replace('CVMFS_SERVER_URL=', '')
        return ''

    def _getRootCatalogURL(self):
        h = self._getRootHash()
        if self.with_gateway:
            gw_url = self._getGWUrl()
            prefix = "%s/data" % gw_url.replace('\n', '')
        else:
            prefix = "http://localhost/cvmfs/%s/data" % self.volumename
        topdir = h[:2]
        fname = h[2:] + "C"
        return (fname, "/".join([prefix, topdir, fname]))

    def _downloadRootCatalog(self, tmpdir):
        (fname, url) = self._getRootCatalogURL()
        tgtfile = os.path.join(tmpdir, fname)
        catalog = os.path.join(tmpdir, "root_catalog.sqlite")
        urllib.urlretrieve(url, tgtfile)
        with open(tgtfile, "r") as fin:
            with open(catalog, "w") as fout:
                p = subprocess.Popen(["cvmfs_swissknife", "zpipe", "-d"],
                                     stdout=fout,
                                     stdin=fin)
                output = p.communicate()[0]
        return catalog

    def _getRootCatalogStats(self, catalog):
        import sqlite3
        conn = sqlite3.connect(catalog)
        stats = dict()
        for row in conn.execute('SELECT * FROM statistics'):
            stats[row[0]] = row[1]
        return stats

    def _write_to_output(self, string):
        with open(self.log_filename, 'a+') as f:
            f.write(string + "\n")
            f.close()

    def run(self):
        try:
            self.gateway = MonitoringGW('cvmfs-lhcbdev', logger=self.logger)
            # First getting the disk stats
            (inodes_total, inodes_used, inodes_free) = self._inodeStats()
            (blocks_total, blocks_used, blocks_free) = self._blockStats()

            res = [inodes_total, inodes_used, inodes_free] + [blocks_total,
                                                              blocks_used,
                                                              blocks_free]

            # Then the CVMFS stats
            tmpdir = tempfile.mkdtemp()
            catalog = self._downloadRootCatalog(tmpdir)
            stats = self._getRootCatalogStats(catalog)
            cvmfs_size = stats['self_file_size'] + stats['subtree_file_size']
            cvmfs_filecount = stats['self_regular'] + stats['subtree_regular']
            cvmfs_dircount = stats['self_dir'] + stats['subtree_dir']
            m = 1024.0 * 1024.0
            g = m * 1024.0
            res.append(cvmfs_size)
            res.append(cvmfs_filecount)
            res.append(cvmfs_dircount)

            # Now printing the results
            datestr = str(datetime.datetime.now())

            output_str = " ".join([str(r) for r in [datestr] + res])
            self._write_to_output(output_str)

            stat_data = [
                {
                    'name': 'inodes_total',
                    'value': inodes_total,
                    'desc': 'Inodes total'
                },
                {
                    'name': 'inodes_used',
                    'value': inodes_used,
                    'desc': 'Inodes used'
                },
                {
                    'name': 'percentages_inodes',
                    'value': float(inodes_used) * 100 / float(inodes_total),
                    'desc': 'Percentages of inodes'
                },
                {
                    'name': 'inodes_free',
                    'value': inodes_free,
                    'desc': 'Inodes free'
                },
                {
                    'name': 'blocks_total',
                    'value': float(blocks_total) / m,
                    'desc': 'Blocks total'
                },
                {
                    'name': 'blocks_used',
                    'value': float(blocks_used) / m,
                    'desc': 'Blocks used'
                },
                {
                    'name': 'percentages_blocks',
                    'value': float(blocks_used) * 100 / float(blocks_total),
                    'desc': 'Blocks percentage'
                },
                {
                    'name': 'blocks_free',
                    'value': blocks_free,
                    'desc': 'Blocks free'
                },
                {
                    'name': 'cvmfs_size',
                    'value': float(cvmfs_size) / g,
                    'desc': 'CVMFS Size'
                },
                {
                    'name': 'duplication_efficacy',
                    'value': float(cvmfs_size) / (float(blocks_used) * 1024.0),
                    'desc': 'duplication_efficacy'
                },
                {
                    'name': 'cvmfs_filecount',
                    'value': cvmfs_filecount,
                    'desc': 'CVMFS files count'
                },
                {
                    'name': 'cvmfs_dircount',
                    'value': cvmfs_dircount,
                    'desc': 'CVMFS dirs count'
                },
                {
                    'name': 'cvmfs_ration',
                    'value': float(cvmfs_filecount + cvmfs_dircount) / (
                        float(inodes_used)),
                    'desc': 'cvmfs_ration'
                },
                ]

            # And cleanup
            if tmpdir.startswith("/tmp"):
                shutil.rmtree(tmpdir)

            self.gateway.sendMetrics(stat_data)
        except:
            pass
