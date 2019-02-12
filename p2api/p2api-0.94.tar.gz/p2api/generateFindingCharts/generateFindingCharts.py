#! /usr/bin/env python

# $Id: p2api_generateFindingCharts.py 1165 2019-02-01 12:47:26Z jpritcha $
from __future__ import print_function

_VERSION_ = "$Revision: 1165 $"

import sys                            # interaction with Python interpreter
import os, os.path                    # operating system services
from optparse import OptionParser     # for parsing command line arguments
from optparse import OptionGroup
import logging

import getpass
import keyring
import datetime
import time
import warnings
import json

import p2api

################################################################################

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
def get_attrs(klass):
  return [k for k in klass.__dict__.keys()
            if not k.startswith('__')
            and not k.endswith('__')]

################################################################################
class get_options:
  "get command line options"

  def __init__(self, vers="0.0"):
    # define options and arguments
    parser = OptionParser(version = "%prog " + vers)

    group = OptionGroup(parser, "Input OB(s)")
    group.add_option("-i", "--ids", dest="ids", metavar="Ids", help="List of OB IDs [required]", default=None)
    group.add_option("--bk_image", dest="bk_image", metavar="BK_IMAGE", help="A custom background image to use [optional]", default=None)
    group.add_option("--obsdate", dest="obsdate", metavar="OBS_DATE", help="Set the obsdate [optional]", default=None)
    group.add_option("--pmax", dest="pmax", metavar="PMAX", help="pmax to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--pmin", dest="pmin", metavar="PMIN", help="pmin to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--stretch", dest="stretch", metavar="STRETCH", help="Stretch to apply to the display of first FC [optional]", default=None)
    group.add_option("--survey", dest="survey", metavar="SURVEY", help="An alternative SkyView survey to use [optional]", default=None)
    parser.add_option_group(group)

    group = OptionGroup(parser, "p2 server selection, options and password management")
    group.add_option("--env", dest="env", help="Use the production|demo environment [optional], default = production", default='production')
    group.add_option("-u", "--user", dest="user", metavar="USER", help="the User Portal account of the user to use, e.g. ASMITHSONIAN [required for production (not required for demo)]", default=None)
    group.add_option("-S", "--PWstore", dest="pwstore", metavar="PWSTORE", help="Store the password in the keyring, default=False", action="store_true", default=False)
    group.add_option("-R", "--PWreenter", dest="pwreenter", metavar="PWREENTER", help="Reenter the password, thus overriding any PW in the keyring, default=False", action="store_true", default=False)
    group.add_option("-Z", "--PWremove", dest="pwremove", metavar="PWREMOVE", help="Remove any password from the keyring, default=False", action="store_true", default=False)
    parser.add_option_group(group)

    group = OptionGroup(parser, "Verbosity...",
                    "All optional")
    group.add_option("-D", "--debug", dest="debug", help="Write out debugging info [optional]", action="store_true", default=False)
    group.add_option("-v", "--verbose", dest="vbose", help="Write out verbose info [optional]", action="store_true", default=False)
    group.add_option("-q", "--quiet", dest="quiet", help="Write out minimal info [optional]", action="store_true", default=False)
    parser.add_option_group(group)

    # parse arguments
    (options, args) = parser.parse_args()

    if not options.ids:
        parser.print_help()
        sys.exit(2)

    self.env = options.env
    self.ids = options.ids
    self.obsdate = options.obsdate
    self.bk_image = options.bk_image
    self.survey = options.survey
    self.stretch = options.stretch
    self.pmin = options.pmin
    self.pmax = options.pmax

    self.user = options.user
    self.pwstore = options.pwstore
    self.pwreenter = options.pwreenter
    self.pwremove = options.pwremove

    self.debug = options.debug
    self.vbose = options.vbose
    self.quiet = options.quiet

    logFMT = "%(asctime)s %(module)15s[%(process)5d] [%(levelname)s] %(message)s"
    logLVL=logging.INFO
    if options.vbose:
      logLVL=logging.INFO
    if options.debug:
      logLVL=logging.DEBUG
    if options.quiet:
      logLVL=logging.WARN
    logging.basicConfig(level=logLVL, format=logFMT)

options = get_options(_VERSION_)

################################################################################
def rgetFolderIds( api, cIds ):

    ids = []
    for cId in cIds :
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'Folder' :
                logging.debug('Adding %d to folder list' %(r['containerId']))
                ids.extend([r['containerId'],])
                ids.extend(rgetFolderIds(api, [r['containerId'],]))
    return ids
################################################################################
def rgetContainerIds( api, cIds, status=None ):
    ids = []
    for cId in cIds :
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'TimeLink' or r['itemType'] == 'Group' or r['itemType'] == 'Concatenation' :
                if status is None or r['containerStatus'] in list(status) :
                    logging.debug('Adding %d to container list' %(r['containerId']))
                    ids.extend([r['containerId'],])
    return ids

################################################################################
def rgetOBIds( api, cIds, status=None ):
    ids = []
    for cId in cIds :
        logging.debug('Checking container %d' %(cId))
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'OB' or  r['itemType'] == 'CB' :
                if status is None or r['obStatus'] in list(status) :
                    logging.debug('Adding %d to OB list' %(r['obId']))
                    ids.extend([r['obId'],])
    return ids

################################################################################
# ------------------------------------------------------------------------------
def oneOB( api, obId ) :
    try :
        OB, _  = api.getOB(obId)
    except p2api.P2Error as e :
        ## Looks like this ID is not an OB...
        logging.error('OB %d could not be found...' %(obId))
        return
    except:
        raise
    
    if OB['itemType'] not in ['OB',] :
        logging.warning('OB %d is not a science OB' %(obId))
        return

    if OB['obStatus'] not in ['P','-'] :
        logging.warning('OB status is %s, OB not modifiable' %(OB['obstatus']))
        return

    runId, _ = api.getRun(OB['runId'])
    ob_url=api.apiUrl+'/obsBlocks/'+str(obId)
    oneOB_sdt=datetime.datetime.now()
    logging.info("Creating finding charts for OBid = %d, OBname = '%s' @ %s..." % (OB['obId'],OB['name'],OB['instrument']))
    data, etag = api.generateFindingChart(
        obId,
        obs_date=options.obsdate,
        survey=options.survey,
        bk_image=options.bk_image,
        stretch=options.stretch,
        pmin=options.pmin,
        pmax=options.pmax,
    )
    oneOB_edt=datetime.datetime.now()
    logging.info("Finding chart for OBid = %d, OBname = '%s' @ %s done in %s." % (obId, OB['name'], OB['instrument'], str(oneOB_edt-oneOB_sdt)))
    if data is not None :
        try :
            jwarn=json.loads(r.content.decode('utf-8'))
            if 'warnings' in jwarn.keys() :
                logging.warning(jwarn['warnings'])
        except :
            pass
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def main():

    ################################################################################
    # remove passowrd from keyring...
    if options.pwremove and options.user is not None :
        keyring.delete_password('usd_p2api_interactive:www.eso.org', options.user)
        sys.exit(0)
    
    password_from_keyring = None
    # Login...
    if options.env in ['demo',]:
        user='52052'
        pwstream='tutorial'
    else:
        user=options.user
        ## from astroquery.eso
        # Get password from keyring or prompt
        if options.pwreenter is False:
            password_from_keyring = keyring.get_password(
                "usd_p2api_interactive:www.eso.org", user)

        if password_from_keyring is None:
            #if system_tools.in_ipynb():
            #    log.warning("You may be using an ipython notebook:"
            #                " the password form will appear in your terminal.")
            # see https://pymotw.com/2/getpass/
            if sys.stdin.isatty():
                pwstream = getpass.getpass(user+"@<"+options.env+"> password : ", stream=sys.stderr)
            else:
                pwstream = sys.stdin.readline().rstrip()
        else:
            pwstream = password_from_keyring

    #login to the API
    i=0
    api = None
    while api is None and i < 10 :
        try:
            api = p2api.ApiConnection(options.env, user, pwstream)
        except p2api.P2Error :
            logging.error(p2api.P2Error)
            time.sleep(2)
        except :
            pass
        i+=1
    if i == 10 :
        logging.error('Ooops, login failed...')
        sys.exit(1)
    
    ## from astroquery.eso
    # When authenticated, save password in keyring if needed
    if options.env not in ['demo','defidev7',] and password_from_keyring is None and options.pwstore:
        keyring.set_password("usd_p2api_interactive:www.eso.org", user, pwstream)

    obIds=[]
    for ID in options.ids.split(',') :
        nID=int(ID)
        logging.info("Processing OB/Container ID = %d" %(nID))
        # The containes and OBs
        try:
            container, containerVersion = api.getContainer(nID)
            fIds = [nID,]
            fIds.extend(rgetFolderIds(api, [nID,]))
            logging.info('================================================================================')
            cIds=rgetContainerIds(api, fIds )
            fcIds = fIds+cIds
            if cIds is not None :
                logging.info("containerId list = %s" %(str(cIds)))
            else :
                logging.error("No containers found")
            logging.info('================================================================================')
            obIds=obIds+rgetOBIds(api, fcIds )
            logging.info("obId list = %s" %(str(obIds)))
            if obIds is None :
                logging.error("No OBs found")

        except p2api.P2Error as e :
            ## Looks like this ID is not a container, assume it is an OB, below...
            obIds.append(nID)
        except:
            raise

    if len(obIds) > 0 :
        if len(obIds) > 1 :
            sdt=datetime.datetime.now()
            logging.warning('Submitting %d OBs for FC generation...' %( len(obIds) ))
        for obId in obIds :
            oneOB(api, obId)
        if len(obIds) > 1 :
            edt=datetime.datetime.now()
            logging.info('Total elapsed time to process %d finding charts %s...' %(len(obIds),str(edt-sdt)))
    else :
        logging.error('No OBs found.')

if __name__ == '__main__' :
    main()
