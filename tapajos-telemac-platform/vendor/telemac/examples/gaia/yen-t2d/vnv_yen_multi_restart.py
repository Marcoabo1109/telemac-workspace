
"""
Validation script for yen_multi restart
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

        # yen-exp_multi T2D+GAI scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_yen-exp_multi1_short.cas')

        # Restart scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_yen-exp_multi1_restart.cas')

        # From restart scalar mode
        self.add_study('vnv_5',
                       'telemac2d',
                       't2d_yen-exp_multi1_from_restart.cas')


    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:T2DRST',
                            'restart_yen_multi1_t2d.slf',
                            eps=[1e-4])

        # Comparison with the restart file used to continue.
        self.check_epsilons('vnv_3:GAIRST',
                            'restart_yen_multi1_gai.slf',
                            eps=[1e-4])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_5:T2DRES',
                            eps=[1e-4])

        # Comparison between one way and intermediate step, sequential run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_5:GAIRES',
                            eps=[1e-4])

    def _post(self):
        """
        Post-treatment processes
        """
