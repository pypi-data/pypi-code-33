class FFT3dFakeForDoc(object):
    """Perform Fast Fourier Transform in 3D.

    Parameters
    ----------

    n0 : int

      Global size over the first dimension in spatial space. This corresponds
      to the z direction.

    n1 : int

      Global size over the second dimension in spatial space. This corresponds
      to the y direction.

    n2 : int

      Global size over the second dimension in spatial space. This corresponds
      to the x direction.

    """

    def __init__(self, n0=2, n1=2, n2=4):
        pass

    def get_short_name(self):
        """Get a short name of the class."""

    def get_dim_first_fft(self):
        """The dimension (real space) over which the first fft is taken.

        It is usually 2 but it seems to be 0 for p3dfft (written in Fortran!).
        """

    def get_local_size_X(self):
        """Get the local size in real space."""

    def run_tests(self):
        """Run simple tests from C++."""

    def run_benchs(self, nb_time_execute=10):
        """Run the C++ benchmarcks."""

    def fft_as_arg(self, fieldX, fieldK):
        """Perform FFT and put result in second argument."""

    def ifft_as_arg(self, fieldK, fieldX):
        """Perform iFFT and put result in second argument."""

    def ifft_as_arg_destroy(self, fieldK, fieldX):
        """Perform iFFT and put result in second argument."""

    def fft(self, fieldX):
        """Perform FFT and return the result."""

    def ifft(self, fieldK):
        """Perform iFFT and return the result."""

    def get_shapeX_loc(self):
        """Get the shape of the array in real space for this mpi process."""

    def get_shapeK_loc(self):
        """Get the shape of the array in Fourier space for this mpi process."""

    def get_shapeX_seq(self):
        """Get the shape of an array in real space for a sequential run."""

    def gather_Xspace(self, ff_loc, root=0):
        """Gather an array in real space for a parallel run.
        """

    def scatter_Xspace(self, ff_seq, root=0):
        """Scatter an array in real space for a parallel run.

        """

    def get_shapeK_seq(self):
        """Get the shape of an array in Fourier space for a sequential run."""

    def sum_wavenumbers(self, fieldK):
        """Compute the sum over all wavenumbers."""

    def get_dimX_K(self):
        """Get the indices of the real space dimension in Fourier space."""

    def get_seq_indices_first_K(self):
        """Get the "sequential" indices of the first number in Fourier space."""

    def get_seq_indices_first_X(self):
        """Get the "sequential" indices of the first number in real space."""

    def get_k_adim_loc(self):
        """Get the non-dimensional wavenumbers stored locally.

        Returns
        -------

        k0_adim_loc : np.ndarray

        k1_adim_loc : np.ndarray

        k2_adim_loc :  np.ndarray

        The indices correspond to the index of the dimension in spectral space.

        """

    def build_invariant_arrayX_from_2d_indices12X(self, o2d, arr2d):
        """Build an array in real space invariant in the third dim."""

    def build_invariant_arrayK_from_2d_indices12X(self, o2d, arr2d):
        """Build an array in Fourier space invariant in the third dim."""

    def compute_energy_from_X(self, fieldX):
        """Compute the mean energy from a real space array."""

    def compute_energy_from_K(self, fieldK):
        """Compute the mean energy from a Fourier space array."""

    def sum_wavenumbers(self, fieldK):
        """Compute the sum over all wavenumbers."""

    def create_arrayX(self, value=None):
        """Return a constant array in real space."""

    def create_arrayK(self, value=None):
        """Return a constant array in real space."""
