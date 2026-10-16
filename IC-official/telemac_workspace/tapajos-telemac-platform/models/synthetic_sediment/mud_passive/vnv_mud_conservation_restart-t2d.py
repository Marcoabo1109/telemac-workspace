
"""
Validation script for mud_conservation-t2d restart
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
        self.tags = ['telemac2d', 'gaia']

    def _pre(self):
        """
        Defining the studies
        """

        # Mud conservation T2D+GAI scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_mud_cons.cas')


        # Mud conservation T2D+GAI parallel mode
        cas = TelemacCas('t2d_mud_cons.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_mud_cons_par.cas',
                       cas=cas)

        del cas

        # Restart scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_mud_cons_restart.cas')


        # Restart parallel mode
        cas = TelemacCas('t2d_mud_cons_restart.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_mud_cons_restart_par.cas',
                       cas=cas)

        del cas

        # From restart scalar mode
        self.add_study('vnv_5',
                       'telemac2d',
                       't2d_mud_cons_from_restart.cas')


        # From restart parallel mode
        t2d_par_cas_filename = 't2d_mud_cons_from_restart_par.cas'
        gai_par_cas_filename = 'gai_mud_cons_from_restart-t2d_par.cas'
        cas = TelemacCas('t2d_mud_cons_from_restart.cas', get_dico('telemac2d'))
        casgai = TelemacCas('gai_mud_cons_from_restart-t2d.cas', get_dico('gaia'))
        cas.set('PARALLEL PROCESSORS', 4)
        cas.set('PREVIOUS COMPUTATION FILE', 'restart_mud_cons_t2d_par.slf')
        casgai.set('PREVIOUS SEDIMENTOLOGICAL COMPUTATION FILE', 'restart_mud_cons_gai_par.slf')

        # Write the GAIA steering file to new file
        casgai.write(gai_par_cas_filename)

        # Change GAIA steering filename in TELEMAC steering file
        cas.set('GAIA STEERING FILE', gai_par_cas_filename)

        # Write the new T2D steering file
        cas.write(t2d_par_cas_filename)

        self.add_study('vnv_6',
                       'telemac2d',
                       't2d_mud_cons_from_restart-t2d_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1e-7])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_2:GAIRES',
                            eps=[1e-7])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:T2DRST',
                            'restart_mud_cons_t2d.slf',
                            eps=[1e-7])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:GAIRST',
                            'restart_mud_cons_gai.slf',
                            eps=[1e-9])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_4:T2DRST',
                            'restart_mud_cons_t2d_par.slf',
                            eps=[1e-7])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_4:GAIRST',
                            'restart_mud_cons_gai_par.slf',
                            eps=[1e-9])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_5:T2DRES',
                            eps=[1e-8])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_5:GAIRES',
                            eps=[1e-8])

        # Comparison between one way and intermediate step, parallel run.
        self.check_epsilons('vnv_2:T2DRES',
                            'vnv_6:T2DRES',
                            eps=[1e-7])

        # Comparison between one way and intermediate step, parallel run.
        self.check_epsilons('vnv_2:GAIRES',
                            'vnv_6:GAIRES',
                            eps=[1e-7])

    def _post(self):
        """
        Post-treatment processes
        """
