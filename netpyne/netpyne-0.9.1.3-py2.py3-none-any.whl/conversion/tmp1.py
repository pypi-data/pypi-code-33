    def setCellRuleDynamicParamsFromNeuroml(self, cell, cellRule):
        
        segGroupKeys = set([sec.split('_')[0] for sec in cellRule['secs']])
        seg_grps_vs_nrn_sections = {segGroup: [sec for sec in cellRule['secs'] if sec.startswith(segGroup)] for segGroup in segGroupKeys}
        seg_grps_vs_nrn_sections['all'] = list(cellRule['secs'])
        inhomogeneous_parameters = {segGroup: [] for segGroup in segGroupKeys}  # how to fill in this from swc file?  

        for cm in cell.biophysical_properties.membrane_properties.channel_densities:
                      
            group = 'all' if not cm.segment_groups else cm.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                if cm.ion_channel=='pas':
                    mech = {'g':gmax}
                else:
                    mech = {'gmax':gmax}
                erev = pynml.convert_to_units(cm.erev,'mV')
                
                cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                
                ion = self._determine_ion(cm)
                if ion == 'non_specific':
                    mech['e'] = erev
                else:
                    if 'ions' not in cellRule['secs'][section_name]:
                        cellRule['secs'][section_name]['ions'] = {}
                    if ion not in cellRule['secs'][section_name]['ions']:
                        cellRule['secs'][section_name]['ions'][ion] = {}
                    cellRule['secs'][section_name]['ions'][ion]['e'] = erev
        
        for cm in cell.biophysical_properties.membrane_properties.channel_density_v_shifts:
                      
            group = 'all' if not cm.segment_groups else cm.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                if cm.ion_channel=='pas':
                    mech = {'g':gmax}
                else:
                    mech = {'gmax':gmax}
                erev = pynml.convert_to_units(cm.erev,'mV')
                
                cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                
                ion = self._determine_ion(cm)
                if ion == 'non_specific':
                    mech['e'] = erev
                else:
                    if ion not in cellRule['secs'][section_name]['ions']:
                        cellRule['secs'][section_name]['ions'][ion] = {}
                    cellRule['secs'][section_name]['ions'][ion]['e'] = erev
                mech['vShift'] = pynml.convert_to_units(cm.v_shift,'mV')
                    
        for cm in cell.biophysical_properties.membrane_properties.channel_density_nernsts:
            group = 'all' if not cm.segment_groups else cm.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                if cm.ion_channel=='pas':
                    mech = {'g':gmax}
                else:
                    mech = {'gmax':gmax}
                
                cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                
                #TODO: erev!!
                
                ion = self._determine_ion(cm)
                if ion == 'non_specific':
                    pass
                    ##mech['e'] = erev
                else:
                    if ion not in cellRule['secs'][section_name]['ions']:
                        cellRule['secs'][section_name]['ions'][ion] = {}
                    ##cellRule['secs'][section_name]['ions'][ion]['e'] = erev
                    
                    
        for cm in cell.biophysical_properties.membrane_properties.channel_density_ghk2s:
                      
            group = 'all' if not cm.segment_groups else cm.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                if cm.ion_channel=='pas':
                    mech = {'g':gmax}
                else:
                    mech = {'gmax':gmax}
                
                ##erev = pynml.convert_to_units(cm.erev,'mV')
                
                cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                
                ion = self._determine_ion(cm)
                if ion == 'non_specific':
                    pass
                    #mech['e'] = erev
                else:
                    if ion not in cellRule['secs'][section_name]['ions']:
                        cellRule['secs'][section_name]['ions'][ion] = {}
                    ##cellRule['secs'][section_name]['ions'][ion]['e'] = erev
        
        for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniforms:
            
            for vp in cm.variable_parameters:
                if vp.parameter=="condDensity":
                    iv = vp.inhomogeneous_value
                    grp = vp.segment_groups
                    path_vals = inhomogeneous_parameters[grp]
                    expr = iv.value.replace('exp(','math.exp(')
                    #print("variable_parameter: %s, %s, %s"%(grp,iv, expr))
                    
                    for section_name in seg_grps_vs_nrn_sections[grp]:
                        path_start, path_end = inhomogeneous_parameters[grp][section_name]
                        p = path_start
                        gmax_start = pynml.convert_to_units('%s S_per_m2'%eval(expr),'S_per_cm2')
                        p = path_end
                        gmax_end = pynml.convert_to_units('%s S_per_m2'%eval(expr),'S_per_cm2')
                        
                        nseg = cellRule['secs'][section_name]['geom']['nseg'] if 'nseg' in cellRule['secs'][section_name]['geom'] else 1
                        
                        #print("   Cond dens %s: %s S_per_cm2 (%s um) -> %s S_per_cm2 (%s um); nseg = %s"%(section_name,gmax_start,path_start,gmax_end,path_end, nseg))
                        
                        gmax = []
                        for fract in [(2*i+1.0)/(2*nseg) for i in range(nseg)]:
                            
                            p = path_start + fract*(path_end-path_start)
                            
                            
                            gmax_i = pynml.convert_to_units('%s S_per_m2'%eval(expr),'S_per_cm2')
                            #print("     Point %s at %s = %s"%(p,fract, gmax_i))
                            gmax.append(gmax_i)
                        
                        if cm.ion_channel=='pas':
                            mech = {'g':gmax}
                        else:
                            mech = {'gmax':gmax}
                        erev = pynml.convert_to_units(cm.erev,'mV')

                        cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == 'non_specific':
                            mech['e'] = erev
                        else:
                            if ion not in cellRule['secs'][section_name]['ions']:
                                cellRule['secs'][section_name]['ions'][ion] = {}
                            cellRule['secs'][section_name]['ions'][ion]['e'] = erev
                        
                    
        for cm in cell.biophysical_properties.membrane_properties.channel_density_ghks:
            raise Exception("<channelDensityGHK> not yet supported!")
        
        for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniform_nernsts:
            raise Exception("<channelDensityNonUniformNernst> not yet supported!")
        
        for cm in cell.biophysical_properties.membrane_properties.channel_density_non_uniform_ghks:
            raise Exception("<channelDensityNonUniformGHK> not yet supported!")
        
        
        for vi in cell.biophysical_properties.membrane_properties.init_memb_potentials:
            
            group = 'all' if not vi.segment_groups else vi.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                cellRule['secs'][section_name]['vinit'] = pynml.convert_to_units(vi.value,'mV')
                    
        for sc in cell.biophysical_properties.membrane_properties.specific_capacitances:
            
            group = 'all' if not sc.segment_groups else sc.segment_groups
            for section_name in seg_grps_vs_nrn_sections[group]:
                cellRule['secs'][section_name]['geom']['cm'] = pynml.convert_to_units(sc.value,'uF_per_cm2')
        
        if hasattr(cell.biophysical_properties.intracellular_properties, 'resistivities'):
            for ra in cell.biophysical_properties.intracellular_properties.resistivities:
                
                group = 'all' if not ra.segment_groups else ra.segment_groups
                for section_name in seg_grps_vs_nrn_sections[group]:
                    cellRule['secs'][section_name]['geom']['Ra'] = pynml.convert_to_units(ra.value,'ohm_cm')
        
        if hasattr(cell.biophysical_properties.intracellular_properties, 'species'):  
            for specie in cell.biophysical_properties.intracellular_properties.species:
                
                group = 'all' if not specie.segment_groups else specie.segment_groups
                for section_name in seg_grps_vs_nrn_sections[group]:
                    cellRule['secs'][section_name]['ions'][specie.ion]['o'] = pynml.convert_to_units(specie.initial_ext_concentration,'mM')
                    cellRule['secs'][section_name]['ions'][specie.ion]['i'] = pynml.convert_to_units(specie.initial_concentration,'mM')
                    
                    cellRule['secs'][section_name]['mechs'][specie.concentration_model] = {}
                
        
        return cellRule