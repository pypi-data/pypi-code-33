import GPy

class KernelFactory:
    """
    This class contains the construction of the kernel.
    """

    @staticmethod
    def construct_kernel(STS, forced_hypers=None):
        """
        Creates the kernel.
        """
        kerns = [None]*(STS.dim)
        KernelFactory._select_kernels(kerns, STS, forced_hypers)
        if forced_hypers is None: KernelFactory._set_constraints(kerns, STS)
        if forced_hypers is None: KernelFactory._set_priors(kerns, STS)

        # multiplies the kernels into one object and returns it
        Kernel = kerns[0]
        if len(kerns) > 1:
            for i in range(1, len(kerns)):
                Kernel = Kernel * kerns[i]
        return Kernel

    @staticmethod
    def _select_kernels(kerns, STS, forced_hypers):
        """
        Selects and creates kernel objects for each dimension. Hyperparameters
        are set to their initial values and default constraints removed.
        """
        for i in range(STS.dim):
            if forced_hypers is None:
                if i == 0: Ksi = STS.thetainit[0]
                else: Ksi = 1.
                Klsi = STS.thetainit[i+1]
            else:
                Ksi = forced_hypers[0]
                Klsi = forced_hypers[1 + i]
            Kp = STS.periods[i]
                
            if STS.kerntype[i] == 'stdp':
                kerns[i] = GPy.kern.StdPeriodic(
                    input_dim=1, variance=Ksi, period=Kp, lengthscale=Klsi,
                    ARD1=True, ARD2=True, active_dims=[i], name='kern'
                            )
            elif STS.kerntype[i] == 'rbf':
                kerns[i] = GPy.kern.RBF(
                    input_dim=1, variance=Ksi, lengthscale=Klsi, ARD=True,
                    active_dims=[i], name='kern'
                            )
            elif STS.kerntype[i] == 'mat32':
                kerns[i] = GPy.kern.Matern32(
                    input_dim=1, variance=Ksi, lengthscale=Klsi, ARD=True,
                    active_dims=[i], name='kern'
                            )
            elif STS.kerntype[i] == 'mat52':
                kerns[i] = GPy.kern.Matern52(
                    input_dim=1, variance=Ksi, lengthscale=Klsi, ARD=True,
                    active_dims=[i], name='kern'
                            )
            else:
                raise TypeError("ERROR: Unknown kernel '" +
                                STS.kerntype[i] + "'")

#            kerns[i].unconstrain()

    @staticmethod
    def _set_constraints(kerns, STS):
        """
        Sets hyperparameter constraints on kernels.
        """
        # variance
        if STS.thetabounds is not None:
            kerns[0].variance.constrain_bounded(
                STS.thetabounds[0][0], STS.thetabounds[0][1], warning=False)
        # lengthscale
            for i in range(STS.dim):
                kerns[i].lengthscale.constrain_bounded(
                    STS.thetabounds[i+1][0], 
                    STS.thetabounds[i+1][1], warning=False)
        # period
        for i in range(STS.dim):
            if STS.kerntype[i] == 'stdp': # pbc
                kerns[i].period.constrain_fixed(STS.periods[i], warning=False)

        # other than the first kernel's variances
        if STS.dim > 1:
            for i in range(1, STS.dim):
                kerns[i].variance.constrain_fixed(1., warning=False)
            
    @staticmethod
    def _set_priors(kerns, STS):
        """
        Sets hyperparameter priors on kernels.
        """
        if STS.thetaprior is not None:
            prior = None
            if STS.thetaprior == "gamma":
                prior = GPy.priors.Gamma
            else:
                raise TypeError("Unknown value '" + STS.thetaprior 
                                + "' given in keyword thetaprior.")

            # variance
            kerns[0].variance.set_prior(
                    prior(STS.thetapriorpar[0][0],
                          STS.thetapriorpar[0][1]),
                    warning=False
            )
            # lengthscale
            for i in range(STS.dim):
                kerns[i].lengthscale.set_prior(
                    prior(STS.thetapriorpar[i+1][0], 
                          STS.thetapriorpar[i+1][1]),
                    warning=False
                )

