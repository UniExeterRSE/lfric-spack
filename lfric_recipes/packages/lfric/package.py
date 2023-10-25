# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install lfric
#
# You can edit this file again by typing:
#
#     spack edit lfric
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

import sys
import os
from spack.package import *


class Lfric(MakefilePackage):
    """The LFRic project aims to develop a software infrastructure primarily to
    support the development of a replacement for the UK Met Office's Unified
    Model but also to provide a common library that underpins a range of
    modelling requirments and related tools."""

    homepage = "https://code.metoffice.gov.uk/trac/lfric"
    svn = "https://code.metoffice.gov.uk/svn/lfric/LFRic/trunk"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    # FIXME: Add proper versions and checksums here.
    version("r39162", revision=39162)

    # FIXME: Add variants for different installation types

    # FIXME: Restrict versions
    depends_on("mpi")
    depends_on("hdf5+mpi")

    # NetCDF seemingly needs to be built with --enable_dap for MacOS - it is
    # recommended not to use external curl, as spack has issues finding libs
    if sys.platform == 'darwin':
        depends_on("netcdf-c+mpi+dap")
    else:
        depends_on("netcdf-c+mpi")
    depends_on("netcdf-fortran ^netcdf-c+mpi")

    depends_on("yaxt")
    depends_on("xios@2.5")
    depends_on("pfunit")
    depends_on("py-jinja2")
    depends_on("py-psyclone@2.3.1")
    depends_on("rose-picker")

    # Patch out "-warn errors" for Intel so build doesn't fail with:
    #   utilities/mpi_mod.F90(184): error #8889: Explicit declaration of the
    #   EXTERNAL attribute is required.   [MPI_ALLREDUCE]
    #      call mpi_allreduce( l_sum, g_sum, 1, get_mpi_datatype( real_type,
    #      r_double ), &
    patch("ifort.mk.patch", when="%intel")


    def setup_lfric_env(self, env):
        env.set("FC", self.compiler.fc)
        env.set("FPP", "cpp -traditional-cpp")
        env.set("LFRIC_TARGET_PLATFORM", "meto-xc40")

        # Use compiler to link for MPI variants which dont include an MPI
        # compiler wrapper
        if self.spec['mpi'].satisfies("cray-mpich"):
            env.set("LDMPI", self.compiler.fc)
        else:
            env.set("LDMPI", self.spec['mpi'].mpifc)

        env.set("FFLAGS", f"-I{self.spec['mpi'].prefix}/lib -I{self.spec['mpi'].prefix}/include \
                            -I{self.spec['netcdf-fortran'].prefix}/include \
                            -I{self.spec['yaxt'].prefix}/include \
                            -I{self.spec['xios'].prefix}/include \
                            -I{self.spec['pfunit'].prefix}/include")

        env.set("LDFLAGS", f"-L{self.spec['mpi'].prefix}/lib \
                             -L{self.spec['hdf5'].prefix}/lib \
                             -L{self.spec['netcdf-c'].prefix}/lib \
                             -L{self.spec['netcdf-fortran'].prefix}/lib \
                             -L{self.spec['yaxt'].prefix}/lib \
                             -L{self.spec['xios'].prefix}/lib \
                             -L{self.spec['pfunit'].prefix}/lib")

        env.set("LD_LIBRARY_PATH", f"{self.spec['mpi'].prefix}/lib \
                                     {self.spec['hdf5'].prefix}/lib \
                                     {self.spec['netcdf-c'].prefix}/lib \
                                     {self.spec['netcdf-fortran'].prefix}/lib \
                                     {self.spec['yaxt'].prefix}/lib \
                                     {self.spec['xios'].prefix}/lib \
                                     {self.spec['pfunit'].prefix}/lib")

        env.set("PSYCLONE_CONFIG", os.path.join(self.spec['py-psyclone'].prefix.share, "psyclone/psyclone.cfg"))
        env.set("PYTHONPATH", f"{self.spec['rose-picker'].prefix}/lib/python3.11/site-packages")


    def setup_build_environment(self, env):
        self.setup_lfric_env(env)


    def setup_run_environment(self, env):
        self.setup_lfric_env(env)


    build_directory = "miniapps/skeleton" # FIXME
    def build(self, spec, prefix):
        with working_dir(self.build_directory):
            make("build")

    def install(self, spec, prefix):
        with working_dir(self.build_directory):
            install_tree("bin/", prefix.bin)
            
