
```python
def example_stage(locus_data):
    """
    A fake stage for demonstrating the `run_stage` function.
    """
    # Get a dict of all properties on the new alert.
    print('locus_data.get_properties()')
    print('-->')
    print(locus_data.get_properties())
    print()
    # Get a numpy array of values for particular properties.
    # Rows for 'alert_id' and 'mjd' are always included at the top of the array.
    # For example, in the following examples, the rows of the array will be:
    # - alert_id
    # - mjd
    # - ra
    # - dec
    # - ztf_fid
    # - ztf_magpsf
    print("locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf')")
    print('-->')
    print(locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf'))
    print()
    # In the following example, we specify only to include columns where ztf_fid == 1.
    print("locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf', filters={'ztf_fid': 1})")
    print('-->')
    print(locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf', filters={'ztf_fid': 1}))

    # get_astro_object_matches() returns a datastructure like so:
    # {catalog_name1: [match1, match2, ...],
    #  catalog_name2: [...],
    #  ...}
    print()
    print('locus_data.get_astro_object_matches()')
    print('-->')
    astro_objects = locus_data.get_astro_object_matches()
    print(astro_objects)
    print()
    print('found catalog matches from catalogs: {}'.format(list(astro_objects.keys())))
    for catalog_name, objects in astro_objects.items():
        print()
        print(catalog_name)
        for obj in objects:
            print(obj)

    locus_data.set_property('x', 500)
    locus_data.set_property('y', 3.14)
    locus_data.set_property('z', 'hello')

    locus_data.send_to_stream('my_stream')
```


locus_data.get_properties()
-->
{'alert_id': 2918382, 'ra': 303.5818872, 'dec': 23.5717776, 'mjd': 58372.2575463001, 'ztf_fid': 1, 'ztf_pid': 618257540115, 'ztf_programid': 1, 'ztf_candid': 618257540115015045, 'ztf_tblid': 45, 'ztf_nid': 618, 'ztf_rcid': 1, 'ztf_field': 640, 'ztf_nneg': 2, 'ztf_nbad': 0, 'ztf_ndethist': 49, 'ztf_ncovhist': 168, 'ztf_tooflag': 0, 'ztf_objectidps1': 136283035818076672, 'ztf_objectidps2': 136283035824775298, 'ztf_objectidps3': 136283035808395168, 'ztf_nmtchps': 39, 'ztf_rfid': 640120101, 'ztf_nframesref': 15, 'ztf_nmatches': 1874, 'ztf_jd': 2458372.7575463, 'ztf_diffmaglim': 20.8937587738037, 'ztf_xpos': 650.796203613281, 'ztf_ypos': 1885.75085449219, 'ztf_ra': 303.5818872, 'ztf_dec': 23.5717776, 'ztf_magpsf': 19.2778835296631, 'ztf_sigmapsf': 0.14529325067997, 'ztf_chipsf': 2.11574459075928, 'ztf_magap': 19.5790996551514, 'ztf_sigmagap': 0.126900002360344, 'ztf_distnr': 0.177698463201523, 'ztf_magnr': 17.1259994506836, 'ztf_sigmagnr': 0.0299999993294477, 'ztf_chinr': 2.17300009727478, 'ztf_sharpnr': 0.096000000834465, 'ztf_sky': 0.628498911857605, 'ztf_magdiff': 0.30121698975563, 'ztf_fwhm': 2.5, 'ztf_classtar': 0.986999988555908, 'ztf_mindtoedge': 650.796203613281, 'ztf_magfromlim': 1.31465876102448, 'ztf_seeratio': 1.09842014312744, 'ztf_aimage': 0.663999974727631, 'ztf_bimage': 0.600000023841858, 'ztf_aimagerat': 0.265599995851517, 'ztf_bimagerat': 0.239999994635582, 'ztf_elong': 1.1066666841507, 'ztf_rb': 0.823333323001862, 'ztf_ssdistnr': -999.0, 'ztf_ssmagnr': -999.0, 'ztf_sumrat': 0.980031669139862, 'ztf_magapbig': 19.5974006652832, 'ztf_sigmagapbig': 0.155900001525879, 'ztf_ranr': 303.5818365, 'ztf_decnr': 23.5717976, 'ztf_sgmag1': 17.3465995788574, 'ztf_srmag1': 16.451000213623, 'ztf_simag1': 16.2105007171631, 'ztf_szmag1': 15.8101997375488, 'ztf_sgscore1': 0.316213995218277, 'ztf_distpsnr1': 0.0994756147265434, 'ztf_jdstarthist': 2458275.9583333, 'ztf_jdendhist': 2458372.7575463, 'ztf_scorr': 8.02565670013428, 'ztf_sgmag2': -999.0, 'ztf_srmag2': 21.3794994354248, 'ztf_simag2': 21.3019008636475, 'ztf_szmag2': -999.0, 'ztf_sgscore2': 0.0345833003520966, 'ztf_distpsnr2': 4.64565563201904, 'ztf_sgmag3': 21.4265003204346, 'ztf_srmag3': 20.4165992736816, 'ztf_simag3': 19.828800201416, 'ztf_szmag3': 19.6401996612549, 'ztf_sgscore3': 0.760167002677917, 'ztf_distpsnr3': 5.79269504547119, 'ztf_jdstartref': 2458204.007396, 'ztf_jdendref': 2458255.921319, 'ztf_dsnrms': 23.6567478179932, 'ztf_ssnrms': 39.0163345336914, 'ztf_dsdiff': -15.3595867156982, 'ztf_magzpsci': 26.3358821868896, 'ztf_magzpsciunc': 2.72769989351218e-06, 'ztf_magzpscirms': 0.0197480004280806, 'ztf_clrcoeff': -0.0529600009322166, 'ztf_clrcounc': 4.45859996034415e-06, 'ztf_zpclrcov': -3.39000007443246e-06, 'ztf_zpmed': 26.2970008850098, 'ztf_clrmed': 0.709999978542328, 'ztf_clrrms': 0.186937004327774, 'ztf_neargaia': 0.17473541200161, 'ztf_neargaiabright': -999.0, 'ztf_maggaia': 16.6103096008301, 'ztf_maggaiabright': -999.0, 'ztf_pdiffimfilename': 'ztf_20180911257419_000640_zg_c01_o_q2_scimrefdiffimg.fits', 'ztf_programpi': 'Kulkarni', 'ztf_isdiffpos': 't', 'ztf_ssnamenr': 'null', 'ztf_rbversion': 't8_f5_c3'}

locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf')
-->
[[50628 76964 83220 101280 131368 210180 343972 409192 640237 755152
  893450 1140978 1462313 1561104 1566501 1731769 1907015 2146976 2184489
  2455729 2612737 2607451 2760548 2918382]
 [58275.4583333 58277.3702778001 58277.3936573998 58278.4133333
 58279.3699536999 58282.4010068998 58286.4203471998 58288.4130902998
 58299.3970255 58305.3770833001 58316.3791898 58321.4013657002
 58342.3261806001 58345.3099884 58345.3198147998 58350.3624073998
 58357.2070138999 58363.1932406998 58363.2334027998 58366.2684259
 58368.2530439999 58368.2777661998 58370.2472569002 58372.2575463001]
[303.5818722 303.5818825 303.5819365 303.5819067 303.5818955 303.5817949
303.5818342 303.5818464 303.5817169 303.5818453 303.581839 303.5817122
303.5820197 303.5817131 303.5819175 303.5819107 303.5819203 303.581827
303.5818347 303.5819155 303.5818597 303.5819601 303.5818241 303.5818872]
[23.5718292 23.5718516 23.5718345 23.5718284 23.5717546 23.5717519
 23.5718695 23.571736 23.5717482 23.5718123 23.5717901 23.5717176
 23.5718903 23.5717558 23.5718063 23.571838 23.571838 23.5717979
 23.5717624 23.5718559 23.571858 23.5718487 23.5717666 23.5717776]
[1 1 2 1 1 1 1 1 2 2 1 1 2 1 2 2 2 1 2 1 1 2 1 1]
[19.3178405761719 18.8213596343994 17.6933555603027 19.2889881134033
 19.5614376068115 19.3227100372314 19.4276275634766 18.6863403320312
 17.6444511413574 17.6018676757812 18.7111587524414 19.5735454559326
 18.7006359100342 18.6792221069336 17.9845218658447 17.6935539245605
 18.1521644592285 18.5742492675781 18.3022956848145 19.352014541626
 18.664083480835 18.2836437225342 19.5756530761719 19.2778835296631]]

locus_data.get_time_series('ra', 'dec', 'ztf_fid', 'ztf_magpsf', filters={'ztf_fid': 1})
-->
[[50628 76964 101280 131368 210180 343972 409192 893450 1140978 1561104
  2146976 2455729 2612737 2760548 2918382]
 [58275.4583333 58277.3702778001 58278.4133333 58279.3699536999
 58282.4010068998 58286.4203471998 58288.4130902998 58316.3791898
 58321.4013657002 58345.3099884 58363.1932406998 58366.2684259
 58368.2530439999 58370.2472569002 58372.2575463001]
[303.5818722 303.5818825 303.5819067 303.5818955 303.5817949 303.5818342
303.5818464 303.581839 303.5817122 303.5817131 303.581827 303.5819155
303.5818597 303.5818241 303.5818872]
[23.5718292 23.5718516 23.5718284 23.5717546 23.5717519 23.5718695
 23.571736 23.5717901 23.5717176 23.5717558 23.5717979 23.5718559
 23.571858 23.5717666 23.5717776]
[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]
[19.3178405761719 18.8213596343994 19.2889881134033 19.5614376068115
 19.3227100372314 19.4276275634766 18.6863403320312 18.7111587524414
 19.5735454559326 18.6792221069336 18.5742492675781 19.352014541626
 18.664083480835 19.5756530761719 19.2778835296631]]

locus_data.get_astro_object_matches()
-->
{'2mass_psc':
    [{'j_snr': 47.2, 'pxcntr': 1102951279, 'h_m_stdap': 14.062, 'scan_key': 59124, 'decl': Decimal('23.5717810000'),
     'k_snr': 18.3, 'glat': -6.101, 'use_src': 1, 'id': 1201419629123341841, 'h_m': 14.152, 'gal_contam': 0,
     'h_msig_stdap': 0.063, 'coadd_key': 1359851, 'err_maj': 0.07, 'ph_qual': 'AAA', 'x_scan': -77.7, 'a': 'U',
     'h_cmsig': 0.061, 'mp_flg': 0, 'k_m_stdap': 13.962, 'coadd': 256, 'err_min': 0.06, 'rd_flg': '222',
     'jdate': Decimal('2451686.9188000001'), 'dist_opt': 0.1, 'h_msigcom': 0.061, 'pts_key': 1102951266,
     'k_msig_stdap': 0.079, 'htm20ID': 14125046270269, 'err_ang': 7, 'bl_flg': '111', 'j_psfchi': 0.84, 'phi_opt': 320,
     'h_snr': 24.7, 'hemis': 'n', 'dist_edge_ns': 1568, 'htm16ID': 55175961993, 'designation': '20141962+2334184 ',
     'cc_flg': '000', 'h_psfchi': 0.99, 'b_m_opt': 17.1, 'sid': 331353482, 'k_m': 14.011,
     'date': datetime.date(2000, 5, 22), 'dist_edge_ew': 175, 'j_m': 14.484, 'ndet': '665615', 'k_psfchi': 1.13,
     'vr_m_opt': 16.0, 'cx': Decimal('0.5069737590'), 'k_cmsig': 0.066, 'scan': 36, 'dist_edge_flg': 'ne',
     'cy': Decimal('-0.7635833075'), 'j_cmsig': 0.037, 'prox': 12.0, 'j_m_stdap': 14.495, 'nopt_mchs': 1,
     'ra': Decimal('303.5817880000'), 'k_msigcom': 0.066, 'glon': 63.373, 'dup_src': 0, 'j_msigcom': 0.039, 'pxpa': 57,
     'j_msig_stdap': 0.082, 'ext_key': None, 'cz': Decimal('0.3998976621')}], 'bright_guide_star_cat': [
    {'decEpsilon': 0.316106, 'NpgMagErr': 0.457929, 'JMagCode': None, 'cx': Decimal('0.5069748524'), 'sid': 428121549,
     'FpgMagCode': 35, 'RMag': None, 'semiMajorAxis': 3.43731, 'raProperMotion': 10.1441, 'NpgMagCode': 37,
     'HMag': None, 'cy': Decimal('-0.7635828446'), 'gscID2': 54788, 'JpgMag': 17.4704, 'RMagErr': None,
     'eccentricity': 0.134358, 'decProperMotion': -5.04934, 'UMag': None, 'HMagErr': None,
     'cz': Decimal('0.3998971600'), 'gsc1ID': None, 'JpgMagErr': 0.449012, 'RMagCode': None, 'positionangle': 133.705,
     'raProperMotionErr': 2.75153, 'UMagErr': None, 'HMagCode': None, 'RightAsc_deg': Decimal('303.5818609449'),
     'hstID': 'N2OB054788', 'JpgMagCode': 18, 'IMag': None, 'sourceStatus': 1111205, 'decProperMotionErr': 4.17624,
     'UMagCode': None, 'KMag': None, 'Declination_deg': Decimal('23.5717496115'), 'RightAsc': Decimal('5.2985030228'),
     'VMag': 16.6802, 'IMagErr': None, 'variableFlag': 0, 'deltaEpoch': 44.0167, 'BMag': None, 'KMagErr': None,
     'Declination': Decimal('0.4114046412'), 'VMagErr': 0.361423, 'IMagCode': None, 'multipleFlag': 0,
     'FpgMag': 16.1206, 'BMagErr': None, 'KMagCode': None, 'PositionEpoch': 1992.72, 'VMagCode': 1, 'JMag': None,
     'htm20ID': 14125046270271, 'FpgMagErr': 0.438294, 'BMagCode': None, 'classification': 0, 'raEpsilon': 0.312299,
     'NpgMag': 15.4484, 'JMagErr': None, 'htm16ID': 55175961993}]}

found
catalog
matches
from catalogs: ['2mass_psc', 'bright_guide_star_cat']

2
mass_psc
{'j_snr': 47.2, 'pxcntr': 1102951279, 'h_m_stdap': 14.062, 'scan_key': 59124, 'decl': Decimal('23.5717810000'),
 'k_snr': 18.3, 'glat': -6.101, 'use_src': 1, 'id': 1201419629123341841, 'h_m': 14.152, 'gal_contam': 0,
 'h_msig_stdap': 0.063, 'coadd_key': 1359851, 'err_maj': 0.07, 'ph_qual': 'AAA', 'x_scan': -77.7, 'a': 'U',
 'h_cmsig': 0.061, 'mp_flg': 0, 'k_m_stdap': 13.962, 'coadd': 256, 'err_min': 0.06, 'rd_flg': '222',
 'jdate': Decimal('2451686.9188000001'), 'dist_opt': 0.1, 'h_msigcom': 0.061, 'pts_key': 1102951266,
 'k_msig_stdap': 0.079, 'htm20ID': 14125046270269, 'err_ang': 7, 'bl_flg': '111', 'j_psfchi': 0.84, 'phi_opt': 320,
 'h_snr': 24.7, 'hemis': 'n', 'dist_edge_ns': 1568, 'htm16ID': 55175961993, 'designation': '20141962+2334184 ',
 'cc_flg': '000', 'h_psfchi': 0.99, 'b_m_opt': 17.1, 'sid': 331353482, 'k_m': 14.011,
 'date': datetime.date(2000, 5, 22), 'dist_edge_ew': 175, 'j_m': 14.484, 'ndet': '665615', 'k_psfchi': 1.13,
 'vr_m_opt': 16.0, 'cx': Decimal('0.5069737590'), 'k_cmsig': 0.066, 'scan': 36, 'dist_edge_flg': 'ne',
 'cy': Decimal('-0.7635833075'), 'j_cmsig': 0.037, 'prox': 12.0, 'j_m_stdap': 14.495, 'nopt_mchs': 1,
 'ra': Decimal('303.5817880000'), 'k_msigcom': 0.066, 'glon': 63.373, 'dup_src': 0, 'j_msigcom': 0.039, 'pxpa': 57,
 'j_msig_stdap': 0.082, 'ext_key': None, 'cz': Decimal('0.3998976621')}

bright_guide_star_cat
{'decEpsilon': 0.316106, 'NpgMagErr': 0.457929, 'JMagCode': None, 'cx': Decimal('0.5069748524'), 'sid': 428121549,
 'FpgMagCode': 35, 'RMag': None, 'semiMajorAxis': 3.43731, 'raProperMotion': 10.1441, 'NpgMagCode': 37, 'HMag': None,
 'cy': Decimal('-0.7635828446'), 'gscID2': 54788, 'JpgMag': 17.4704, 'RMagErr': None, 'eccentricity': 0.134358,
 'decProperMotion': -5.04934, 'UMag': None, 'HMagErr': None, 'cz': Decimal('0.3998971600'), 'gsc1ID': None,
 'JpgMagErr': 0.449012, 'RMagCode': None, 'positionangle': 133.705, 'raProperMotionErr': 2.75153, 'UMagErr': None,
 'HMagCode': None, 'RightAsc_deg': Decimal('303.5818609449'), 'hstID': 'N2OB054788', 'JpgMagCode': 18, 'IMag': None,
 'sourceStatus': 1111205, 'decProperMotionErr': 4.17624, 'UMagCode': None, 'KMag': None,
 'Declination_deg': Decimal('23.5717496115'), 'RightAsc': Decimal('5.2985030228'), 'VMag': 16.6802, 'IMagErr': None,
 'variableFlag': 0, 'deltaEpoch': 44.0167, 'BMag': None, 'KMagErr': None, 'Declination': Decimal('0.4114046412'),
 'VMagErr': 0.361423, 'IMagCode': None, 'multipleFlag': 0, 'FpgMag': 16.1206, 'BMagErr': None, 'KMagCode': None,
 'PositionEpoch': 1992.72, 'VMagCode': 1, 'JMag': None, 'htm20ID': 14125046270271, 'FpgMagErr': 0.438294,
 'BMagCode': None, 'classification': 0, 'raEpsilon': 0.312299, 'NpgMag': 15.4484, 'JMagErr': None,
 'htm16ID': 55175961993}

