from __future__ import division, print_function


def get_args(raw_args):
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "output_file",
        help="File to output posterior samples to.",
    )

    parser.add_argument(
        "m1_source",
        type=float,
        help="Source-frame primary component mass.",
    )
    parser.add_argument(
        "m2_source",
        type=float,
        help="Source-frame secondary component mass.",
    )

    parser.add_argument(
        "chi1xyz",
        type=float, nargs=3,
#        metavar=["CHI1X", "CHI1Y", "CHI1Z"],
        help="Cartesian components of primary's dimensionless spin.",
    )
    parser.add_argument(
        "chi2xyz",
        type=float, nargs=3,
#        metavar=["CHI2X", "CHI2Y", "CHI2Z"],
        help="Cartesian components of secondary's dimensionless spin.",
    )

    parser.add_argument(
        "network_snr",
        type=float,
        help="Network signal-to-noise ratio.",
    )

    parser.add_argument(
        "--IFO-PSD",
        type=str, nargs=2, action="append",
        help="(IFO, PSD XML file) pair.",
    )

    parser.add_argument(
        "--n-samples",
        type=int, default=1000,
        help="Number of synthetic posterior samples to generate.",
    )

    parser.add_argument(
        "--n-walkers",
        type=int, default=40,
        help="Number of walkers to use for MCMC. Must be even and at least 16.",
    )

    parser.add_argument(
        "--no-shift",
        action="store_true",
        help="Do not take a draw from the initial Gaussian. This is important "
             "if you are trying to mimic a specific real event, rather than "
             "trying to make a fully synthetic event.",
    )

    parser.add_argument(
        "--n-threads",
        type=int,
        help="Number of threads to use for MCMC. If not given, will try to use "
             "max number of threads on system.",
    )

    parser.add_argument(
        "--burnin",
        type=int, default=2000,
        help="Burnin time for MCMC. Should be fairly long.",
    )

    parser.add_argument(
        "--acorr",
        type=int, default=40,
        help="Autocorrelation time to assume for MCMC. Only keeps one sample "
             "for every autocorrelation time that passes.",
    )


    parser.add_argument(
        "--full-chain-output",
        help="HDF5 file to store full MCMC chains to (optional).",
    )


    parser.add_argument(
        "--label-source",
        action="store_true",
        help="Add 'source' to mass labels in output table. Fisher matrix "
             "calculation currently works in detector frame, but for high mass"
             "systems the uncertainties from unknown redshift are dominated by "
             "the intrinsic uncertainties in mass. If neglecting redshift "
             "effects are okay, you may want to use this flag.",
    )

    parser.add_argument(
        "--m-min",
        type=float,
        help="Impose a lower limit on the component masses.",
    )
    parser.add_argument(
        "--m-max",
        type=float,
        help="Impose an upper limit on the component masses.",
    )
    parser.add_argument(
        "--M-max",
        type=float,
        help="Impose an upper limit on the total mass.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for random number generator.",
    )


    return parser.parse_args(raw_args)



def main(raw_args=None):
    import sys

    if raw_args is None:
        raw_args = sys.argv[1:]

    args = get_args(raw_args)

    # Ensure at least one PSD was provided.
    if args.IFO_PSD is None:
        raise ValueError(
            "Need at least one IFO,PSD pair (see --IFO-PSD option)."
        )
    else:
        psd_map = dict(args.IFO_PSD)


    from . import gw, synthetic_pe
    import numpy

    if args.label_source:
        def source(label):
            return "{}_source".format(label)
    else:
        def source(label):
            return label

    random_state = numpy.random.RandomState(args.seed)

    mc_eta_chi12xyz_samples = synthetic_pe.get_samples(
        args.m1_source, args.m2_source,
        args.chi1xyz, args.chi2xyz,
        args.network_snr,
        args.n_samples, psd_map,
        burnin=args.burnin, acorr=args.acorr,
        walkers=args.n_walkers,
        m_min=args.m_min, m_max=args.m_max, M_max=args.M_max,
        threads=args.n_threads,
        no_shift=args.no_shift,
        full_chain_hdf5=args.full_chain_output,
        random_state=random_state
    )

    mc, eta, a1x, a1y, a1z, a2x, a2y, a2z = (
        mc_eta_chi12xyz_samples.T
    )

    m1, m2 = gw.mc_eta_2_m1_m2(mc, eta)

    M = m1 + m2
    q = m2 / m1

    a1 = numpy.linalg.norm([a1x, a1y, a1z], axis=0)
    a2 = numpy.linalg.norm([a2x, a2y, a2z], axis=0)

    costilt1 = a1z / a1
    costilt2 = a2z / a2

    chi_eff = gw.effective_inspiral_spin(m1, m2, a1z, a2z, M=M)

    output_samples = numpy.column_stack((
        m1, m2,
        M, q,
        mc, eta,
        a1x, a1y, a1z, a2x, a2y, a2z,
        a1, a2,
        costilt1, costilt2,
        chi_eff,
    ))

    numpy.savetxt(
        args.output_file, output_samples,
        delimiter="\t",
        header="\t".join([
            source("m1"), source("m2"),
            source("M"), "q",
            source("mc"), "eta",
            "a1x", "a1y", "a1z", "a2x", "a2y", "a2z",
            "a1", "a2",
            "costilt1", "costilt2",
            "chi_eff",
        ])
    )
