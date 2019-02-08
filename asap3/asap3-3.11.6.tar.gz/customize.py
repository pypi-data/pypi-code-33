"""User provided customizations.

This files defines system specific options etc for compiling Asap.

To adapt Asap to a new system type, please add code to this file
to identify it, and contribute the modified file back to the 
Asap project.

Alternatively, make a file called customize-local.py, and put
your customizations there.  

Here are all the lists that can be modified:

NORMAL COMPILATION:
* libraries             Link against these extra libraries
* library_dirs          Search for libraries here (-L)
* include_dirs          Search for include files here (-I)
* extra_link_args       Extra arguments used when linking
* extra_compile_args    Extra arguments used when compilation
* remove_compile_args   Remove these arguments from compilation command line

The following are less likely to be important
* runtime_library_dirs  ???
* extra_objects         Extra object that should be linked (probably useless).
* define_macros         Macros that should be defined
* undef_macros          Macros that should be undefined.

COMPILATION WITH MPI
* mpi_compiler          Tuple of MPI C and C++ compiler driver scripts.

Typically, the following do not need customization.
* mpi_libraries         Extra libraries when compiling with MPI
* mpi_library_dirs      Search for libraries here
* mpi_include_dirs      Search for include files here
* mpi_runtime_library_dirs  ???
* mpi_define_macros     Define these extra macros.

COMPILATION WITH INTEL COMPILER:
* use_intel_compiler    False, True or 'auto'.  Can be overruled on command line.
* intel_compiler        Tuple of Intel C and C++ compiler names
* intel_mpi_compiler    Tuple of command lines that makes the mpi compiler scripts
                        use the Intel compiler.  Should match mpi_compiler.
* intel_compile_args    Command lines flags when compiling.  Overrules extra_compile_args
* intel_libraries       Libraries to link against.  Overrules libraries
* intel_link_args       Command line flags when linking.  Overrules extra_compile_args

COMPILATION WITH INTEL MATH KERNEL LIBRARY (--with-mkl)
* mkl_supported         True if $MKLROOT is defined, or set manually in this file.
* mkl_compile_args      Command line args added to extra_compile_args
* mkl_intel_compile_args  Command line args added to intel_compile_args
* mkl_include_dirs      Extra include directories for MKL
* mkl_libraries         Extra libraries for MKL
* mkl_library_dirs      Extra library_dirs for MKL
* mkl_define_macros     Extra macros to be defined - should at least be ['ASAP_MKL']


To override use the form:
    
    libraries = ['somelib', 'otherlib']

To append use the form

    libraries += ['somelib', 'otherlib']

You can access all variable from the setup.py script.  Useful ones are
* systemname  (for example 'Linux')
* hostname    (may or may not be fully qualified)
* machinename  (The CPU architechture, e.g. x86_64)
* processorname   (May contain more infor than machinename)

"""


if systemname == 'Linux' and machinename == 'x86_64':
    # For performance on 64-bit Linux.
    #
    # WARNING: -march=native is not appropriate to build
    #   binary packages that will run on another machine.
    
    extra_compile_args += ['-ffast-math', 
                           '-march=native', 
                           '-Wno-sign-compare',
                           '-Wno-write-strings']
    remove_compile_args += ['-Wstrict-prototypes']
elif systemname == 'Linux' and machinename == 'i686':
    # For performance on 32-bit Linux.
    
    extra_compile_args += ['-ffast-math', 
                           '-Wno-sign-compare']
    remove_compile_args += ['-Wstrict-prototypes']


# If linking fails with a large number of missing symbols, many of them
# starting with rl_ then try uncommenting the following line.

#libraries += ['readline']
