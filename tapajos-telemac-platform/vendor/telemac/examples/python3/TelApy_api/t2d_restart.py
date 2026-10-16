#!/usr/bin/env python3
"""
Example of a telapy telemac2d run with restart capabilities (test case gouttedo)
"""
import sys
from os import path, chdir, environ, getcwd, makedirs
if(not path.exists(path.join(environ.get('HOMETEL', ''),
                             'builds',
                             environ.get('USETELCFG', ''),
                             'wrap_api', 'lib', 'api.pyf'))):
    print("  -> telapy not available doing nothing")
    sys.exit(0)

from telapy.api.t2d import Telemac2d
from execution.telemac_cas import TelemacCas
from data_manip.extraction.telemac_file import TelemacFile
from mpi4py import MPI
import numpy as np

def vnv_copy_files(module, cas_file, par):
    """
    Copying input files into validation folder if HOMETEL and USETEL other wise
    running in cas folder

    @param module (str) Name of the module
    @param cas_file (str) steering file
    @param dist (str) Folder in which to copy (creates it if it does not exist)
    """

    if 'USETELCFG' in environ and 'HOMETEL' in environ:
        vnv_working_dir = path.join(getcwd(),
                                    'vnv_api',
                                    path.basename(__file__[:-3])+par,
                                    environ['USETELCFG'])

        # Creating folders if they do not exists
        if MPI.COMM_WORLD.Get_rank() == 0:
            if not path.exists(vnv_working_dir):
                print("  ~> Creating: ", vnv_working_dir)
                makedirs(vnv_working_dir)
            chdir(path.dirname(cas_file))
            dico_file = path.join(environ['HOMETEL'], 'sources', module,
                                  module+'.dico')
            cas = TelemacCas(cas_file, dico_file)

            cas.copy_cas_files(vnv_working_dir, copy_cas_file=True)

            del cas
        MPI.COMM_WORLD.barrier()
    else:
        vnv_working_dir = path.dirname(cas_file)

    return vnv_working_dir


def main(recompile=True, restart_write=False, continued=False, restart_online=False):
    """
    Main function of script

    @param recompile (Boolean) If True recompiling user fortran
    @param restart_write (Boolean) If True writes a complete restart
    @param continued (Boolean) If True resumes computation from a restart
    @param restart_online (Boolean) If True resumes computation via the api

    @retuns Value of waterdepth at the end of the simulation
    """
    comm = MPI.COMM_WORLD
    master = comm.rank == 0

    root = environ.get('HOMETEL', path.join('..', '..', '..'))

    pwd = getcwd()

    cas_file = path.join(root, 'examples', 'telemac2d', 'pildepon',
                         't2d_pildepon.cas')

    ncsize = comm.Get_size()

    par = '-par' if ncsize > 1 else "-seq"

    vnv_working_dir = vnv_copy_files('telemac2d', cas_file, par)

    chdir(vnv_working_dir)

    # Make local cas file restart capable
    cas_file = path.join('.',path.basename(cas_file))

    if master:
        dico_file = path.join(environ['HOMETEL'], 'sources', 'telemac2d',
                              'telemac2d.dico')
        cas = TelemacCas(cas_file, dico_file)
        printout = cas.get('VARIABLES FOR GRAPHIC PRINTOUTS')
        if 'W' not in printout:
            cas.set('VARIABLES FOR GRAPHIC PRINTOUTS',printout+',W')
        cas.set('LISTING PRINTOUT PERIOD', 300)
        cas.set('INITIAL GUESS FOR H', 2)
        cas.set('INITIAL GUESS FOR U', 2)
        cas.set('RESTART MODE', restart_write)
        cas.set('COMPUTATION CONTINUED', continued)
        if restart_write:
            cas.set('RESTART FILE', 't2d_restart_file.slf')
            cas.set('RESTART FILE FORMAT', 'SERAFIND')
            cas.set('RESULTS FILE', 'r2d_pildepon.slf')
        else:
            cas.remove('RESTART FILE')
            cas.remove('RESTART FILE FORMAT')
        if continued:
            cas.set('PREVIOUS COMPUTATION FILE', 't2d_restart_file.slf')
            cas.set('PREVIOUS COMPUTATION FILE FORMAT', 'SERAFIND')
            cas.set('RESULTS FILE', 'r2d_pildepon_restarted.slf')
        else:
            cas.remove('PREVIOUS COMPUTATION FILE')
            cas.remove('PREVIOUS COMPUTATION FILE FORMAT')
        if restart_online:
            cas.set('RESULTS FILE', 'r2d_pildepon_rst_online.slf')
        cas.write(cas_file)
    comm.barrier()

    # Creation of the instance Telemac2d
    study = Telemac2d(cas_file, user_fortran='user_fortran',
                      comm=comm, stdout=0, recompile=recompile)
    # Testing construction of variable list
    _ = study.variables

    study.set_case()
    # Determine the run extent and mode
    tot_timestep = 1500
    rst_timestep = 750
    if restart_write:
        # Allow restart output at every timestep since it is invoked explicitly
        study.set('MODEL.RESTART_PERIOD', 1)
        ntimesteps = [tot_timestep]
        restart_records = [tot_timestep/3-1, rst_timestep-1, 2*tot_timestep/3-1]
        #            i.e. [500th, 750th, 1000th] counted from 0
    if continued:
        study.set('MODEL.START_RECORD', 2)
        ntimesteps = [tot_timestep - rst_timestep]
    if restart_online:
        ntimesteps = [tot_timestep, tot_timestep - rst_timestep]

    # Allow results output at every timestep since it is invoked explicitly
    graphic_freq = study.get('MODEL.GRAPH_PERIOD')
    study.set('MODEL.GRAPH_PERIOD', 1)

    # Initalization
    study.init_state_default()
    # Modify the friction coefficient in the first run or in the online restart run
    if restart_write or restart_online:
        ks = study.get_array('MODEL.CHESTR') - 10.
        study.set_array('MODEL.CHESTR', ks)
    # Run all time steps
    for tstep in range(ntimesteps[0]):
        if restart_online and tstep == rst_timestep:
            rst_at = study.get('MODEL.AT')
            rst_lt = study.get('MODEL.LT')
            study.save_state()
        # Computation only timestep
        study.run_one_time_step_compute()
        # Invoke results output explicitly
        if restart_online:
            doprint = tstep < rst_timestep
        else:
            doprint = True
        if doprint and (tstep+1) % graphic_freq == 0:
            study.run_one_time_step_res()
        # Invoke restart output explicitly
        if restart_write and tstep in restart_records:
            study.run_one_time_step_rst()
    if restart_online:
        # Reinitialise the model at restart time
        study.set('MODEL.AT', rst_at)
        study.set('MODEL.LT', rst_lt)
        study.restore_state()
        # Second integration rerunning the second half of the event
        for tstep in range(ntimesteps[1]):
            # Computation only timestep
            study.run_one_time_step_compute()
            # Invoke results output explicitly
            if (tstep+1) % graphic_freq == 0:
                study.run_one_time_step_res()
    # Storing the final field for final output
    h = study.mpi_get_array("MODEL.WATERDEPTH")
    t4 = study.mpi_get_array("MODEL.TRACER", 3)
    # Ending the run
    study.finalize()
    # Instance delete
    del study
    chdir(pwd)
    return h, t4, vnv_working_dir

if __name__ == "__main__":
    master = MPI.COMM_WORLD.rank == 0
    # First run on 1500 timesteps storing a restart at the 750th (among other)
    H1, T1, vnv_working_dir = main(restart_write=True)
    if master: print("First run passed")
    # Second run on 750 timesteps starting from the 750th of the previous run
    H2, T2, _ = main(recompile=False, continued=True)
    if master: print("Second run passed")
    # Third run on 1500 timesteps restarted online from the 750th
    H3, T3, _ = main(recompile=False, restart_online=True)
    if master: print("Third run passed")
    # Coherency check
    assert ( np.array_equal(H1, H2) and np.array_equal(H1, H3) )
    if master: print("Coherency check on final computed water height passed")
    assert ( np.array_equal(T1, T2) and np.array_equal(T1, T3) )
    if master: print("Coherency check on final computed tracer 4 passed")
    # Check coeherency on result files
    out1 = TelemacFile(path.join(vnv_working_dir,'r2d_pildepon.slf'))
    out2 = TelemacFile(path.join(vnv_working_dir,'r2d_pildepon_restarted.slf'))
    out3 = TelemacFile(path.join(vnv_working_dir,'r2d_pildepon_rst_online.slf'))
    KS1 = out1.get_data_value('BOTTOM FRICTION',15)[:]
    KS2 = out2.get_data_value('BOTTOM FRICTION',0)[:]
    KS3 = out3.get_data_value('BOTTOM FRICTION',15)[:]
    assert ( np.array_equal(KS1, KS2) and np.array_equal(KS1, KS3) )
    if master: print("Coherency check on restarted bottom friction passed")
    H1 = out1.get_data_value('WATER DEPTH',-1)[:]
    H2 = out2.get_data_value('WATER DEPTH',-1)[:]
    H3 = out3.get_data_value('WATER DEPTH',-1)[:]
    assert ( np.array_equal(H1, H2) and np.array_equal(H1, H3) )
    if master: print("Coherency check on final stored water height passed")
    N1 = out1.get_data_value('N SCHEME  PC 1',-1)[:]
    N2 = out2.get_data_value('N SCHEME  PC 1',-1)[:]
    N3 = out3.get_data_value('N SCHEME  PC 1',-1)[:]
    assert ( np.array_equal(N1, N2) and np.array_equal(N1, N3) )
    if master: print("Coherency check on final stored tracer 4 passed")
    P1 = out1.get_data_value('PSI SCHEME PC 2',-1)[:]
    P2 = out2.get_data_value('PSI SCHEME PC 2',-1)[:]
    P3 = out3.get_data_value('PSI SCHEME PC 2',-1)[:]
    assert ( np.array_equal(P1, P2) and np.array_equal(P1, P3) )
    if master: print("Coherency check on final stored tracer 9 passed")
    if master: print("My work is done")
