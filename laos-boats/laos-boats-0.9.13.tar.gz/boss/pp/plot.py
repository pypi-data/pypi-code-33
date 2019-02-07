import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import warnings

class Plot:
    """
    Plotting functionality. All plot functions make PNG images to destination
    file based on given source array(s) of data.
    """

    def data_acquisitions(STS, dest_file, acqs, min_preds):
        """
        Plots minimum predictions and uncertainty, acquisition energies 
        and locations as a function of iteration.
        """
        itNo_acqs = np.clip(acqs[:,0], int(min_preds[0,0]), np.inf)
        x = acqs[:,2:STS.dim+2]
        y = acqs[:,STS.dim+2]
        itNo_mp = min_preds[:,0]
        xhat = min_preds[:,2:STS.dim+2]
        muhat = min_preds[:,-2]
        nuhat = min_preds[:,-1]

        plt.subplot(211)
        plt.fill_between(itNo_mp, muhat + nuhat, muhat, color='lightgrey')
        plt.fill_between(itNo_mp, muhat - nuhat, muhat, color='lightgrey')
        plt.plot(itNo_mp, muhat + nuhat, 'grey', linewidth=2)
        plt.plot(itNo_mp, muhat - nuhat, 'grey', linewidth=2)
        plt.plot(itNo_mp, muhat, 'black', linewidth=5, label=r'$\mu(\hat{x})$')
        plt.scatter(itNo_acqs, y, s=200, linewidth=4, facecolors='none', \
                edgecolors='black', label='$acq_y$')


        plt.xlim(min(itNo_mp), max(itNo_mp))
        plt.xticks(itNo_mp[::max(1,round(len(itNo_mp)/10))])
        plt.ylabel('$y$ with $\mu(\hat{x})$', size=20)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)


        plt.subplot(212)
        colors = ['blue','red','green','brown','yellow','purple','cyan',
                  'magenta','grey','gold']
        for i in range(x.shape[1]):
            plt.plot(itNo_mp, xhat[:,i], color=colors[i%len(colors)], linewidth=5,
                        label='$\hat{x}_%i$'%(i+1))
            plt.scatter(itNo_acqs, x[:,i], s=200, linewidth=4, facecolors='none',
                        edgecolors=colors[i%len(colors)], label='$acq_{x%i}$'%(i+1))

        plt.xlim(min(itNo_mp), max(itNo_mp))
        plt.xticks(itNo_mp[::max(1,round(len(itNo_mp)/10))])
        plt.xlabel('iteration', size=20)
        plt.ylabel('$x_i$ with $\hat{x}_i$', size=20)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)

        plt.suptitle('Data acquisitions', size=20)
        plt.gcf().set_size_inches(9,8)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(dest_file)
        plt.close()
        

    def conv_measures(STS, dest_file, conv_meas, legends=True):
        """
        Plots quantities related to convergence as a function of iteration.
        """
        itNo = conv_meas[:,0]
        dxhat = conv_meas[:,2]
        dmuhat = conv_meas[:,3]
        
        plt.subplot(211)
        plt.plot(itNo, dxhat, 'k', linewidth=5)
        #plt.xlabel('iteration', size=20)
        plt.ylabel(r'$\Delta \hat{x}$', size=24)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.grid(True)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if max(dxhat) > 0: plt.yscale('log')
        
        plt.subplot(212)
        plt.plot(itNo, dmuhat, 'k', linewidth=5)
        plt.xlabel('iteration', size=20)
        plt.ylabel(r'$abs(\Delta \mu(\hat{x}))/\Delta y$', size=24)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.grid(True)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if max(dmuhat) > 0: plt.yscale('log')

        plt.suptitle('Convergence tracking', size=20)
        plt.gcf().set_size_inches(9,7)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(dest_file)
        plt.close()

    def hyperparameters(STS, dest_file, hypers, legends=True):
        """
        Plots GP model unfixed hyperparameters (variances and lengthscales)
        as a function of iteration.
        """
        itNo = hypers[:,0]
        var = hypers[:,2]
        ls = hypers[:,3:]

        colors = ['blue','red','green','brown','yellow','purple','cyan',
                  'magenta','black','gold']
        markers = ['s', 'p','*','h','^','+','x','d','v','|']

        plt.subplot(211)
        plt.plot(itNo, var, color='r', linewidth=5)
        plt.ylabel('Variance', size=20)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.yscale('log')
        plt.grid(True)
        plt.gca().tick_params(labelsize=18)
        #plt.gca().ticklabel_format(useOffset=False)
        
        plt.subplot(212)
        for i in range(STS.dim):
            plt.plot(itNo, ls[:,i], color=colors[i%10], linewidth=5, \
                linestyle='-', marker=markers[i%10], markersize=12,
                label=r'$\ell_ %i$'%(i+1))
        plt.xlabel('iteration', size=20)
        plt.ylabel('Lengthscale', size=20)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.yscale('log')
        plt.grid(True)
        plt.gca().tick_params(labelsize=18)
        #plt.gca().ticklabel_format(useOffset=False)
        if legends: lgd = plt.legend(loc='upper right', prop={'size':18})

        plt.suptitle('Hyperparameter values', size=20)
        plt.gcf().set_size_inches(11,7)
        #plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(dest_file)
        if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,),
            bbox_inches='tight')
        else:
            plt.savefig(dest_file)
        plt.close()


    def truef_hat(STS, dest_file, truef_hats, legends=True):
        """
        Plots true function value at xhat locations
        as a function of iteration.
        """
        itNo = truef_hats[:,0]
        truehat = truef_hats[:,-2]
        last = truehat[-1]
        best = np.array([np.min(truehat[:i]) for i in range(1,len(truehat)+1)])
        tfhat_muhat = truef_hats[:,-1]
        
        plt.subplot(211)
        plt.plot(itNo, abs(truehat-last), 'k', linewidth=5)
        plt.plot(itNo, abs(best-last), 'k', linestyle='dashed', linewidth=3,
        label='best')
        plt.grid(True)
        plt.ylabel(r'$f(\hat{x})-f(\hat{x}_{last})$', size=24)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if max(abs(truehat-last)) and max(abs(best-last)) > 0: plt.yscale('log')
        if legends: lgd = plt.legend(loc='upper right', prop={'size':20})

        plt.subplot(212)
        plt.plot(itNo, abs(tfhat_muhat), 'k', linewidth=5)
        plt.xlabel('iteration', size=20)
        plt.ylabel(r'$f(\hat{x})-\mu(\hat{x})$', size=24)
        plt.xticks(itNo[::max(1,round(len(itNo)/10))])
        plt.grid(True)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if max(abs(tfhat_muhat)) > 0: plt.yscale('log')

        plt.suptitle('True function at minimum predictions', size=20)
        plt.gcf().set_size_inches(9,9)
        #plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(dest_file)
        if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,),
            bbox_inches='tight')
        else:
            plt.savefig(dest_file)
        plt.close()

    def model(STS, dest_file, model_data, xhat=None, acqs=None, xnext=None,
                    minima=None, truef=None, incl_uncert=True,
                    axis_labels=None, legends=True, paths=None):
        """
        Plots a (max 2D) slice of the model.
        """
        coords = model_data[:,:STS.dim]
        mu, nu = model_data[:,-2], model_data[:,-1]
        slice_dim = 1 if STS.pp_m_slice[0] == STS.pp_m_slice[1] else 2
        if axis_labels is None:
            axis_labels = ["$x_%i$"%(STS.pp_m_slice[0]+1), "$x_%i$"%(STS.pp_m_slice[1]+1)]

        if slice_dim == 1:
            x1 = coords[:,STS.pp_m_slice[0]]
            if truef is not None:
                crds = truef[:,:STS.dim]
                tf = truef[:,-1]
                tfx1 = crds[:,STS.pp_m_slice[0]]
                plt.plot(tfx1, tf, 'k', linewidth=5, label='f(x)')
            if incl_uncert:
                plt.fill_between(x1, mu + nu, mu, color='lightgrey')
                plt.fill_between(x1, mu - nu, mu, color='lightgrey')
                plt.plot(x1, mu + nu, 'grey', linewidth=3, label='$\\nu(x)$')
                plt.plot(x1, mu - nu, 'grey', linewidth=3)
            plt.plot(x1, mu, 'b', linewidth=5, label='$\\mu(x)$')

            if xhat is not None:
                plt.axvline(xhat[STS.pp_m_slice[0]], color='red', linewidth=5,
                                label='$\hat{x}$', zorder=19)

            if acqs is not None:
                x1 = acqs[:,STS.pp_m_slice[0]]; y = acqs[:,-1];
                plt.scatter(x1, y, s=200, linewidth=6, facecolors='none',
                                edgecolors='brown', label='acqs', zorder=18)

            if xnext is not None:
                plt.axvline(xnext[STS.pp_m_slice[0]], color='green', linewidth=5,
                        label='$x_{next}$', linestyle='dashed', zorder=20)

            if minima is not None:
                x1 = minima[:,STS.pp_m_slice[0]]; y = minima[:,-1];
                plt.scatter(x1, y, s=250, linewidth=6, zorder=19,
                         facecolors='none', edgecolors='lawngreen',
                         label='minima')

            plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
            yd = max(mu) - min(mu)
            plt.ylim(min(mu) - 0.1*yd, max(mu) + 0.1*yd)
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel('$y$', size=24)
            if legends:
                lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                 ncol=4, mode="expand", borderaxespad=0.,
                                 prop={'size':20})
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            #plt.tight_layout()
            if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
                plt.savefig(dest_file, bbox_extra_artists=(lgd,),
                bbox_inches='tight')
            else:
                plt.savefig(dest_file)
            plt.close()

        elif slice_dim == 2:
            npts = STS.pp_m_slice[2]
            x1 = coords[:,STS.pp_m_slice[0]]
            x2 = coords[:,STS.pp_m_slice[1]]

            if truef is not None:
                pass # 2D true func slice will be plotted in separate graph only

            if incl_uncert:
                plt.contour(x1[:npts], x2[::npts], nu.reshape(npts,npts),
                                25, colors = 'k')
                plt.contourf(x1[:npts], x2[::npts], nu.reshape(npts,npts),
                                150, cmap='viridis')
                cbar = plt.colorbar()#, orientation='horizontal')
                cbar.set_label(label='$\\nu(x)$', size=24)
                cbar.ax.tick_params(labelsize=18)
                plt.xlabel(axis_labels[0], size=24)
                plt.ylabel(axis_labels[1], size=24)
                plt.gcf().set_size_inches(10, 8)
                plt.gca().tick_params(labelsize=18)
                plt.tight_layout()
                plt.savefig(dest_file[:-4] + '_uncert.png')
                plt.close()

            plt.contour(x1[:npts], x2[::npts], mu.reshape(npts,npts),
                            25, colors = 'k')
            plt.contourf(x1[:npts], x2[::npts], mu.reshape(npts,npts),
                            150, cmap='viridis')
            cbar = plt.colorbar()#, orientation='horizontal')
            cbar.set_label(label='$\mu(x)$', size=24)
            cbar.ax.tick_params(labelsize=18)

            lo = False
            if xhat is not None:
                plt.plot(xhat[STS.pp_m_slice[0]], xhat[STS.pp_m_slice[1]], 'r*',
                markersize=26, zorder=21, label='$\hat{x}$')
                lo = True

            if acqs is not None:
                x1 = acqs[:,STS.pp_m_slice[0]]; x2 = acqs[:,STS.pp_m_slice[1]];
                sz = np.linspace(200,500,len(x1))
                lw = np.linspace(3,8,len(x1))
                plt.scatter(x1[0], x2[0], s=sz[int(len(x1)/2.)],
                    linewidth=lw[int(len(x1)/2.)], zorder=10, facecolors='none',
                    edgecolors='magenta', label='acqs')
                for i in range(len(x1)):
                    plt.scatter(x1[i], x2[i], s=sz[i], linewidth=lw[i],
                        zorder=10, facecolors='none', edgecolors='magenta')
                lo = True

            if xnext is not None:
                plt.plot(xnext[STS.pp_m_slice[0]], xnext[STS.pp_m_slice[1]], 'b^',
                                markersize=26, label='$x_{next}$', zorder=20)
                lo = True

            if minima is not None:
                x1 = minima[:,STS.pp_m_slice[0]]; x2 = minima[:,STS.pp_m_slice[1]];
                plt.scatter(x1, x2, s=350, linewidth=6, facecolors='none',
                            edgecolors='navajowhite', zorder=11, label='minima')
                lo = True

            if paths is not None:
                threshold = min(STS.bounds[:,1] - STS.bounds[:,0]) / 2
                for path in paths:
                    start = 0
                    stop = 1
                    while True:
                        if (stop == path.crds.shape[0]-1 or 
                                np.linalg.norm(path.crds[stop,:]
                                - path.crds[stop-1,:]) > threshold):
                            plt.plot(path.crds[range(start, stop),0],
                                     path.crds[range(start, stop),1],
                                     linewidth=3.0,
                                     color='red',
                            )
                            if stop == path.crds.shape[0]-1: break
                            else: start = stop
                        stop += 1

            plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
            plt.ylim(min(coords[:,STS.pp_m_slice[1]]), max(coords[:,STS.pp_m_slice[1]]))
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel(axis_labels[1], size=24)
            top = 0.99            
            if legends and lo:
                lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                 ncol=4, mode="expand", borderaxespad=0., 
                                 prop={'size':20})
                top = 0.85
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            #plt.tight_layout()
            if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
                plt.savefig(dest_file, bbox_extra_artists=(lgd,),
                bbox_inches='tight')
            else:
                plt.savefig(dest_file)
            plt.close()
        else:
            raise TypeError("ERROR: Model plot only applicable up to 2D (slices)")




    def acq_func(STS, dest_file, acqf_data, acqs=None, xhat=None, xnext=None,
                    axis_labels=None, legends = True):
        """
        Plots a (max 2D) slice of the acquisition function. Can include also
        acquisitions, xhat and xnext if those are given.
        """
        coords = acqf_data[:,:STS.dim]
        af = acqf_data[:,-1]
        slice_dim = 1 if STS.pp_m_slice[0] == STS.pp_m_slice[1] else 2
        if axis_labels is None:
            axis_labels = ["$x_%i$"%(STS.pp_m_slice[0]+1), "$x_%i$"%(STS.pp_m_slice[1]+1)]

        if slice_dim == 1:
            x1 = coords[:,STS.pp_m_slice[0]]
            plt.plot(x1, af, 'k', linewidth=5)

            if acqs is not None:
                x1 = acqs[:,STS.pp_m_slice[0]]; y = acqs[:,-1];
                plt.scatter(x1, y, s=200, linewidth=6, facecolors='none', \
edgecolors='brown', label='acqs')

            if xhat is not None:
                plt.axvline(xhat[STS.pp_m_slice[0]], color='red', linewidth=5,
                                    label='$\hat{x}$')

            if xnext is not None:
                plt.axvline(xnext[STS.pp_m_slice[0]], color='green', linewidth=5,
                                    label='$x_{next}$', linestyle='dashed')

            plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
            yd = max(af) - min(af)
            plt.ylim(min(af) - 0.1*yd, max(af) + 0.1*yd)
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel('$acqfn(x)$', size=24)
            top = 0.99
            if legends:
                lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                 ncol=4, mode="expand", borderaxespad=0.,
                                 prop={'size':20})
                top=0.9
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            #plt.tight_layout()
            if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
                plt.savefig(dest_file, bbox_extra_artists=(lgd,),
                bbox_inches='tight')
            else:
                plt.savefig(dest_file)
            plt.close()

        elif slice_dim == 2:
            npts = STS.pp_m_slice[2]
            x1 = coords[:,STS.pp_m_slice[0]]
            x2 = coords[:,STS.pp_m_slice[1]]

            plt.contour(x1[:npts], x2[::npts], af.reshape(npts,npts),
                            25, colors = 'k')
            plt.contourf(x1[:npts], x2[::npts], af.reshape(npts,npts),
                            150, cmap='viridis')
            cbar = plt.colorbar()#, orientation='horizontal')
            cbar.set_label(label='$af(x)$', size=24)
            cbar.ax.tick_params(labelsize=18)

            lo = False
            if acqs is not None:
                x1 = acqs[:,STS.pp_m_slice[0]]; x2 = acqs[:,STS.pp_m_slice[1]];
                sz = np.linspace(200,500,len(x1))
                lw = np.linspace(3,8,len(x1))
                plt.scatter(x1[0], x2[0], s=sz[int(len(x1)/2)],
                    linewidth=lw[int(len(x1)/2)], zorder=10, facecolors='none',
                    edgecolors='magenta', label='acqs')
                for i in range(1,len(x1)):
                    plt.scatter(x1[i], x2[i], s=sz[i], linewidth=lw[i],
                        zorder=10, facecolors='none', edgecolors='magenta')
                lo = True

            if xhat is not None:
                plt.plot(xhat[STS.pp_m_slice[0]], xhat[STS.pp_m_slice[1]], 'r*',
                                zorder=19, markersize=26, label='$\hat{x}$')
                lo = True

            if xnext is not None:
                plt.plot(xnext[STS.pp_m_slice[0]], xnext[STS.pp_m_slice[1]], 'b^',
                                zorder=20, markersize=26, label='$x_{next}$')
                lo = True

            plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
            plt.ylim(min(coords[:,STS.pp_m_slice[1]]), max(coords[:,STS.pp_m_slice[1]]))
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel(axis_labels[1], size=24)
            top = 0.99
            if legends and lo:
                lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                 ncol=4, mode="expand", borderaxespad=0.,
                                 prop={'size':20})
                top=0.9
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            #plt.tight_layout()
            if legends and lo: # FOR OLD MATPLOTLIB COMPATIBILITY
                plt.savefig(dest_file, bbox_extra_artists=(lgd,),
                bbox_inches='tight')
            else:
                plt.savefig(dest_file)
            plt.close()
        else:
            raise TypeError("ERROR: Acquisition function plot only"
                          + " applicable up to 2D (slices)")


    def truef(STS, dest_file, truef_data, axis_labels=None):
        """
        Plots a (max 2D) slice of the true function.
        """
        coords = truef_data[:,:STS.dim]
        tf = truef_data[:,-1]
        slice_dim = 1 if STS.pp_m_slice[0] == STS.pp_m_slice[1] else 2
        if axis_labels is None:
            axis_labels = ["$x_%i$"%(STS.pp_m_slice[0]+1), "$x_%i$"%(STS.pp_m_slice[1]+1)]

        if slice_dim == 1:
            x1 = coords[:,STS.pp_m_slice[0]]
            plt.plot(x1, tf, 'k', linewidth=5)
            plt.xlim(min(x1), max(x1))
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel('$f(x)$', size=24)
            plt.title('True function', size=20)
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            #plt.tight_layout()
            plt.tight_layout(); plt.savefig(dest_file)
            plt.close()

        elif slice_dim == 2:
            npts = STS.pp_truef_npts
            x1 = coords[:,STS.pp_m_slice[0]]
            x2 = coords[:,STS.pp_m_slice[1]]

            plt.contour(x1[:npts], x2[::npts], tf.reshape(npts,npts),
                            25, colors = 'k')
            plt.contourf(x1[:npts], x2[::npts], tf.reshape(npts,npts),
                            150, cmap='viridis')
            cbar = plt.colorbar()#, orientation='horizontal')
            cbar.set_label(label='$f(x)$', size=24)
            cbar.ax.tick_params(labelsize=18)

            plt.xlim(min(x1), max(x1))
            plt.ylim(min(x2), max(x2))
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel(axis_labels[1], size=24)
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.gca().ticklabel_format(useOffset=False)
            plt.title('True function', size=20)
            #plt.tight_layout()
            plt.tight_layout(); plt.savefig(dest_file)
            plt.close()
        else:
            raise TypeError("ERROR: True function plot only"
                          + " applicable up to 2D (slices)")






