
"""
Validation script for yen
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from data_manip.extraction.telemac_file import TelemacFile

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

        # yen-exp T2D+GAI scalar mode
        self.add_study('vnv_ser',
                       'telemac2d',
                       't2d_yen-expRestart.cas')


        # yen-exp T2D+GAI parallel mode
        cas = TelemacCas('t2d_yen-expRestart.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_par',
                       'telemac2d',
                       't2d_yen-expRestart.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_ser:GAIRES',
                            'gai_ref_yen-expRestart.slf',
                            eps=[1.e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_par:GAIRES',
                            'gai_ref_yen-expRestart.slf',
                            eps=[1.e-3])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_ser:GAIRES',
                            'vnv_par:GAIRES',
                            eps=[1.e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_ser:T2DRES',
                            'f2d_yen-expRestart.slf',
                            eps=[1.e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_par:T2DRES',
                            'f2d_yen-expRestart.slf',
                            eps=[1.e-3])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_ser:T2DRES',
                            'vnv_par:T2DRES',
                            eps=[1.e-3])

    def _post(self):
        """
        Post-treatment processes
        """
#        import matplotlib.pyplot as plt
#        import numpy as np
#        from postel.plot_vnv import vnv_plot2d
#        vnv1_t2dres = self.get_study_file('vnv_:T2DRES')
#        res_vnv_1_t2dres = TelemacFile(vnv1_t2dres)







