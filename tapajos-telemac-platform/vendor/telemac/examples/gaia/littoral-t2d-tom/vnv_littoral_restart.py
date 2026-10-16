
"""
Validation script for littoral restart
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 1
        self.tags = ['telemac2d', 'tomawac', 'gaia']

    def _pre(self):
        """
        Defining the studies
        """

        # littoral T2D+TOM+GAI scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_littoral_P1.cas')


        # littoral T2D+TOM+GAI scalar mode
        cas = TelemacCas('t2d_littoral_P1.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_littoral_P1_par.cas',
                       cas=cas)

        del cas

        # Restart scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_littoral_P1_restart.cas')


        # Restart parallel mode
        cas = TelemacCas('t2d_littoral_P1_restart.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_littoral_P1_restart_par.cas',
                       cas=cas)

        del cas

        # From restart scalar mode
        self.add_study('vnv_5',
                       'telemac2d',
                       't2d_littoral_P1_from_restart.cas')


        # From restart parallel mode
        t2d_par_cas_filename = 't2d_littoral_P1_from_restart_par.cas'
        gai_par_cas_filename = 'gai_littoral_from_restart_par.cas'
        tom_par_cas_filename = 'tom_littoral_from_restart_par.cas'
        cas = TelemacCas('t2d_littoral_P1_from_restart.cas', get_dico('telemac2d'))
        casgai = TelemacCas('gai_littoral_from_restart.cas', get_dico('gaia'))
        castom = TelemacCas('tom_littoral_from_restart.cas', get_dico('tomawac'))
        cas.set('PARALLEL PROCESSORS', 4)
        cas.set('PREVIOUS COMPUTATION FILE', 'restart_littoral_t2d_par.slf')
        casgai.set('PREVIOUS SEDIMENTOLOGICAL COMPUTATION FILE', 'restart_littoral_gai_par.slf')
        castom.set('PREVIOUS COMPUTATION FILE', 'restart_littoral_tom_par.slf')

        # write the gaia cas file to new file
        casgai.write(gai_par_cas_filename)

        # write the tomawac cas file to new file
        castom.write(tom_par_cas_filename)

        # change gaia steering filename in telemac cas file
        cas.set('GAIA STEERING FILE', gai_par_cas_filename)

        # change tomawac steering filename in telemac cas file
        cas.set('TOMAWAC STEERING FILE', tom_par_cas_filename)

        # write the new t3d cas file
        cas.write(t2d_par_cas_filename)

        self.add_study('vnv_6',
                       'telemac2d',
                       't2d_littoral_P1_from_restart_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1e-9])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_2:GAIRES',
                            eps=[1e-9])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:WACRES',
                            'vnv_2:WACRES',
                            eps=[1e-8])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:T2DRST',
                            'restart_littoral_t2d.slf',
                            eps=[1e-12])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:GAIRST',
                            'restart_littoral_gai.slf',
                            eps=[1e-9])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:WACRBI',
                            'restart_littoral_tom.slf',
                            eps=[1e-12])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_4:T2DRST',
                            'restart_littoral_t2d_par.slf',
                            eps=[1e-12])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_4:GAIRST',
                            'restart_littoral_gai_par.slf',
                            eps=[1e-9])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_4:WACRBI',
                            'restart_littoral_tom_par.slf',
                            eps=[1e-12])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_5:T2DRES',
                            eps=[1e-10])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_5:GAIRES',
                            eps=[1e-11])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:WACRES',
                            'vnv_5:WACRES',
                            eps=[1e-8])

        # Comparison between one way and intermediate step, parallel run.
        self.check_epsilons('vnv_2:T2DRES',
                            'vnv_6:T2DRES',
                            eps=[1e-9])

        # Comparison between one way and intermediate step, parallel run.
        self.check_epsilons('vnv_2:GAIRES',
                            'vnv_6:GAIRES',
                            eps=[1e-9])

        # Comparison between one way and intermediate step, parallel run.
        self.check_epsilons('vnv_2:WACRES',
                            'vnv_6:WACRES',
                            eps=[1e-8])

    def _post(self):
        """
        Post-treatment processes
        """
