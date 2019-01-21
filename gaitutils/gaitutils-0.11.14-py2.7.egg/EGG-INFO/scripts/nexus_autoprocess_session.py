#!python
# -*- coding: utf-8 -*-
"""
Autoprocess all trials in current Nexus session directory. See autoproc
section in config for options.

1st pass (all trials):
-preprocess
-get fp context + strike/toeoff velocities etc.

2nd pass:
-automark (using velocity stats from previous step)
-run models + save

-write Eclipse info

GAP HANDLING:
    If cfg.autoproc.fail_on_gaps is set, the processing will fail on ANY gaps.
    Otherwise, a ROI (region of interest) will be determined based on
    cfg.autoproc.events_range. Gaps outside the ROI will not affect processing.
    However the tracking markers (cfg.autoproc.track_markers) are used to
    determine the ROI and they may not have any gaps anywhere.

@author: Jussi (jnu@iki.fi)
"""

from builtins import zip
import os
import os.path as op
import numpy as np
import argparse
import time
import logging


from gaitutils import (nexus, eclipse, utils, GaitDataError, sessionutils,
                       read_data)
from gaitutils.config import cfg


logger = logging.getLogger(__name__)


def _do_autoproc(enffiles, update_eclipse=True):
    """ Do autoprocessing for all trials listed in enffiles (list of
    paths to .enf files).
    """

    def _run_pipelines(plines):
        """Run given Nexus pipeline(s)"""
        if type(plines) != list:
            plines = [plines]
        for pipeline in plines:
            logger.debug('running pipeline: %s' % pipeline)
            result = vicon.Client.RunPipeline(pipeline.encode('utf-8'), '',
                                              cfg.autoproc.nexus_timeout)
            if result.Error():
                logger.warning('error while trying to run Nexus pipeline: %s'
                               % pipeline)

    def _save_trial():
        """Save trial in Nexus"""
        logger.debug('saving trial')
        vicon.SaveTrial(cfg.autoproc.nexus_timeout)

    def _context_desc(fpev):
        """Get Eclipse description string for given forceplate events dict"""
        s = ""
        nr = len(fpev['R_strikes'])
        if nr:
            s += '%dR' % nr
        nl = len(fpev['L_strikes'])
        if nr and nl:
            s += '/'
        if nl:
            s += '%dL' % nl
        return s or cfg.autoproc.enf_descriptions['context_none']

    def _fail(trial, reason):
        """Abort processing: mark and save trial"""
        fail_desc = (cfg.autoproc.enf_descriptions[reason] if reason in
                     cfg.autoproc.enf_descriptions else reason)
        logger.debug('preprocessing failed: %s' % fail_desc)
        trial['recon_ok'] = False
        trial['description'] = fail_desc
        _save_trial()

    def _range_to_roi(subj_pos, gait_dim, mov_range):
        """Try to determine ROI (in frames) from movement range"""
        subj_pos1 = subj_pos[:, [gait_dim]]
        # find non-gap frames where we are inside movement range
        dist_ok = np.where((subj_pos1 >= mov_range[0]) &
                           (subj_pos1 <= mov_range[1]) &
                           (subj_pos1 != 0.0))[0]
        return min(dist_ok), max(dist_ok)

    # used to store stats about foot velocity
    foot_vel = {'L_strike': np.array([]), 'R_strike': np.array([]),
                'L_toeoff': np.array([]), 'R_toeoff': np.array([])}
    # 1st pass
    logger.debug('\n1st pass - processing %d trial(s)\n' % len(enffiles))

    vicon = nexus.viconnexus()
    nexus_ver = nexus.true_ver()
    trials = dict()

    # close trial to prevent 'Save trial?' dialog on first open
    if nexus_ver >= 2.8:
        logger.debug('force closing open trial')
        vicon.CloseTrial(5000)  # timeout in ms

    for enffile in enffiles:
        filepath = enffile[:enffile.find('.Trial')]  # rm .TrialXXX and .enf
        filename = os.path.split(filepath)[1]
        trial = dict()
        trials[filepath] = trial
        logger.debug('loading in Nexus: %s' % filename)
        vicon.OpenTrial(filepath, cfg.autoproc.nexus_timeout)
        try:
            subjectname = nexus.get_metadata(vicon)['name']
        except GaitDataError:
            # may indicate broken or video-only trial
            logger.warning('cannot read metadata')
            trial['recon_ok'] = False
            trial['description'] = 'skipped'
            continue
        allmarkers = vicon.GetMarkerNames(subjectname)
        edata = eclipse.get_eclipse_keys(enffile, return_empty=True)
        logger.debug('type: %s' % edata['TYPE'])
        logger.debug('description: %s' % edata['DESCRIPTION'])
        logger.debug('notes: %s' % edata['NOTES'])
        eclipse_str = ''

        # check whether to skip trial
        if edata['TYPE'] in cfg.autoproc.type_skip:
            logger.debug('skipping based on type: %s' % edata['TYPE'])
            trial['recon_ok'] = False
            trial['description'] = 'skipped'
            continue
        skip = [s.upper() for s in cfg.autoproc.eclipse_skip]
        if (any([s in edata['DESCRIPTION'].upper() for s in skip]) or
           any([s in edata['NOTES'].upper() for s in skip])):
                logger.debug('skipping based on description/notes')
                # run preprocessing + save even for skipped trials, to mark
                # them as processed - mostly so that Eclipse export to Polygon
                # will work
                _run_pipelines(cfg.autoproc.pre_pipelines)
                _save_trial()
                trial['recon_ok'] = False
                trial['description'] = 'skipped'
                continue

        # try to run preprocessing pipelines
        _run_pipelines(cfg.autoproc.pre_pipelines)

        # check trial length
        trange = vicon.GetTrialRange()
        if (trange[1] - trange[0]) < cfg.autoproc.min_trial_duration:
            _fail(trial, 'short')
            continue

        # check for valid marker data
        try:
            mkrdata = read_data.get_marker_data(vicon, allmarkers,
                                                ignore_missing=True)
        except GaitDataError:
            logger.debug('get_marker_data failed')
            _fail(trial, 'label_failure')
            continue

        # fail on any gaps in trial (off by default)
        gaps_found = False
        if cfg.autoproc.fail_on_gaps:
            for marker in set(allmarkers) - set(cfg.autoproc.ignore_markers):
                gaps = mkrdata[marker + '_gaps']
                if gaps.size > 0:
                    gaps_found = True
                    break
            if gaps_found:
                _fail(trial, 'gaps')
                continue

        # plug-in gait checks
        if not utils.is_plugingait_set(mkrdata):
            logger.warning('marker set does not correspond to Plug-in Gait')
            _fail(trial, 'label_failure')
            continue
        elif not utils.check_plugingait_set(mkrdata):
                logger.debug('Plug-in Gait marker sanity checks failed')
                _fail(trial, 'label_failure')
                continue

        # get subject position by tracking markers
        try:
            subj_pos = utils.avg_markerdata(mkrdata,
                                            cfg.autoproc.track_markers)
        except GaitDataError:
            logger.debug('gaps in tracking markers')
            _fail(trial, 'label_failure')
            continue
        gait_dim = utils.principal_movement_direction(subj_pos)
        # our roi according to events_range
        # this is not the same as Nexus ROI, which is unset at this point
        roi = _range_to_roi(subj_pos, gait_dim, cfg.autoproc.events_range)
        logger.debug('events range corresponds to frames %d-%d' % roi)

        # check forceplate data
        fp_info = (eclipse.eclipse_fp_keys(edata) if
                   cfg.autoproc.use_eclipse_fp_info else None)
        try:
            fpev = utils.detect_forceplate_events(vicon, mkrdata,
                                                  fp_info=fp_info, roi=roi)
        except GaitDataError:
            logger.warning('cannot determine forceplate events, possibly due '
                           'to gaps')
            _fail(trial, 'gaps')
            continue
        # get foot velocity info for all events (do not reduce to median)
        try:
            vel = utils.get_foot_contact_velocity(mkrdata, fpev, medians=False,
                                                  roi=roi)
        except GaitDataError:
            logger.warning('cannot determine foot velocity, possibly due to '
                           'gaps')
            _fail(trial, 'gaps')
            continue

        # preprocessing looks ok at this stage
        trial['recon_ok'] = True
        trial['mkrdata'] = mkrdata

        eclipse_str += _context_desc(fpev)
        valid = fpev['valid']
        trial['valid'] = valid
        trial['fpev'] = fpev

        # save velocity data
        for context in valid:
            nv = np.append(foot_vel[context+'_strike'], vel[context+'_strike'])
            foot_vel[context+'_strike'] = nv
            nv = np.append(foot_vel[context+'_toeoff'], vel[context+'_toeoff'])
            foot_vel[context+'_toeoff'] = nv
        eclipse_str += ','

        # main direction in lab frame (1,2,3 for x,y,z)
        inds_ok = np.where(np.any(subj_pos, axis=1))  # ignore gaps
        subj_pos_ = subj_pos[inds_ok]
        # +1/-1 for forward/backward (coord increase / decrease)
        gait_dir = np.median(np.diff(subj_pos_, axis=0), axis=0)[gait_dim]
        # write Eclipse key for direction
        if ('dir_forward' in cfg.autoproc.enf_descriptions and 'dir_backward'
           in cfg.autoproc.enf_descriptions):
            dir_str = 'dir_forward' if gait_dir > 0 else 'dir_backward'
            dir_desc = cfg.autoproc.enf_descriptions[dir_str]
            eclipse_str += '%s,' % dir_desc

        # compute gait velocity
        median_vel = utils._trial_median_velocity(vicon)
        logger.debug('median forward velocity: %.2f m/s' % median_vel)
        eclipse_str += '%.2f m/s' % median_vel

        _save_trial()
        trial['description'] = eclipse_str

        # write Eclipse fp values according to our detection
        fp_info = fpev['our_fp_info']
        if cfg.autoproc.write_eclipse_fp_info is True:
            logger.debug('writing detected forceplate info into Eclipse')
            eclipse.set_eclipse_keys(enffile, fp_info,
                                     update_existing=True)
        elif cfg.autoproc.write_eclipse_fp_info == 'reset':
            logger.debug('resetting Eclipse forceplate info')
            fp_info_auto = {k: 'Auto' for k, v in fp_info.items()}
            eclipse.set_eclipse_keys(enffile, fp_info_auto,
                                     update_existing=True)

    # all preprocessing done
    # compute velocity thresholds using all trials
    vel_th = {key: (np.median(x) if x.size > 0 else None) for key, x in
              foot_vel.items()}

    # 2nd pass
    sel_trials = {filepath: trial for filepath, trial in trials.items()
                  if trial['recon_ok']}
    logger.debug('\n2nd pass - processing %d trials\n' % len(sel_trials))

    for filepath, trial in sel_trials.items():
        filename = os.path.split(filepath)[1]
        logger.debug('loading in Nexus: %s' % filename)
        vicon.OpenTrial(filepath, cfg.autoproc.nexus_timeout)
        enf_file = filepath + '.Trial.enf'

        # automark using global velocity thresholds
        try:
            vicon.ClearAllEvents()
            utils.automark_events(vicon, vel_thresholds=vel_th,
                                  mkrdata=trial['mkrdata'],
                                  fp_events=trial['fpev'], plot=False,
                                  events_range=cfg.autoproc.events_range,
                                  start_on_forceplate=cfg.autoproc.
                                  start_on_forceplate, roi=roi)
        except GaitDataError:  # cannot automark
            eclipse_str = '%s,%s' % (trial['description'],
                                     cfg.autoproc.enf_descriptions
                                     ['automark_failure'])
            logger.debug('automark failed')
            _save_trial()
            trial['description'] = eclipse_str
            continue  # next trial

        # events ok
        # crop trial
        if nexus_ver >= 2.5:
            evs = vicon.GetEvents(subjectname, "Left", "Foot Strike")[0]
            evs += vicon.GetEvents(subjectname, "Right", "Foot Strike")[0]
            evs += vicon.GetEvents(subjectname, "Left", "Foot Off")[0]
            evs += vicon.GetEvents(subjectname, "Right", "Foot Off")[0]

            if evs:
                # when setting roi, do not go beyond trial range
                minfr, maxfr = vicon.GetTrialRange()
                roistart = max(min(evs) - cfg.autoproc.crop_margin, minfr)
                roiend = min(max(evs) + cfg.autoproc.crop_margin, maxfr)
                vicon.SetTrialRegionOfInterest(roistart, roiend)

        # run model pipeline and save
        eclipse_str = '%s,%s' % (cfg.autoproc.enf_descriptions['ok'],
                                 trial['description'])
        _run_pipelines(cfg.autoproc.model_pipelines)
        _save_trial()
        trial['description'] = eclipse_str

    # all done; update Eclipse descriptions
    if cfg.autoproc.eclipse_write_key and update_eclipse:
        # try to avoid a possible race condition where Nexus is still
        # holding the .enf file open
        time.sleep(.5)
        for filepath, trial in trials.items():
            enf_file = filepath + '.Trial.enf'
            try:
                eclipse.set_eclipse_keys(enf_file,
                                         {cfg.autoproc.eclipse_write_key:
                                          trial['description']},
                                         update_existing=True)
            except IOError:
                logger.warning('Could not write Eclipse description to %s' %
                               enf_file)
    else:
        logger.debug('not updating Eclipse data')

    # print stats
    logger.debug('Complete')
    logger.debug('Trials opened: %d' % len(trials))
    logger.debug('Trials with recon ok: %d' % len(sel_trials))


def _delete_c3ds(enffiles):
    """ c3d files need to be deleted before processing. Otherwise Nexus will
    load analog data from existing c3d files which are affected by previous
    crop operations, e.g. forceplate data might be clipped """
    logger.debug('deleting previous c3d files')
    c3dfiles = [sessionutils._enf2other(enffile, 'c3d') for enffile in
                enffiles]
    for enffile, c3dfile in zip(enffiles, c3dfiles):
        if not op.isfile(c3dfile):
            continue
        edata = eclipse.get_eclipse_keys(enffile, return_empty=True)
        # do not delete static .c3d files (needed for dynamic processing)
        if edata['TYPE'] == 'Static':
            logger.debug('keeping static c3d file %s' % c3dfile)
            continue

        # to prevent data loss, do not delete c3d if original
        # x1d and x2d do not exist
        x1dfile = sessionutils._enf2other(enffile, 'x1d')
        x2dfile = sessionutils._enf2other(enffile, 'x2d')
        if (op.isfile(x1dfile) and op.isfile(x2dfile)):
            logger.debug('deleting existing c3d file %s' % c3dfile)
            os.remove(c3dfile)
        else:
            logger.debug('refusing to delete c3d file %s since original '
                         'data files .(x1d and .x2d) do not exist' % c3dfile)


def autoproc_session(patterns=None, update_eclipse=True):

    sessionpath = nexus.get_sessionpath()
    enffiles = sessionutils.get_session_enfs(sessionpath)

    if not enffiles:
        raise GaitDataError('No trials found (no .enf files in session)')

    _delete_c3ds(enffiles)

    if patterns:
        # filter trial names according to patterns
        enffiles = [s for s in enffiles if any([p in s for p in patterns])]
    if enffiles:
        _do_autoproc(enffiles, update_eclipse=update_eclipse)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--include', metavar='p', type=str, nargs='+',
                        help='strings that must appear in trial name')
    parser.add_argument('--no_eclipse', action='store_true',
                        help='disable writing of Eclipse entries')

    args = parser.parse_args()
    autoproc_session(args.include, update_eclipse=not args.no_eclipse)
