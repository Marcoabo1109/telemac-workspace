
"""
Validation script for tide
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
        self.rank = 2
        self.tags = ['telemac2d']

    def _pre(self):
        """
        Defining the studies
        """

        # tide pressure bc scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_tide-pressbc.cas')


        # tide pressure bc parallel mode
        cas = TelemacCas('t2d_tide-pressbc.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_tide-pressbc_par.cas',
                       cas=cas)

        del cas


        # tide no pressure bc scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_tide-nopressbc.cas')


        # tide no pressure bc parallel mode
        cas = TelemacCas('t2d_tide-nopressbc.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_tide-nopressbc_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_tide-pressbc.slf',
                            eps=[3e-3, 2e-3, 0.016, 0.016, 4e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_tide-pressbc.slf',
                            eps=[3e-3, 2e-3, 0.014, 0.014, 4e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[2e-3, 2e-3, 8e-3, 8e-3, 2e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_3:T2DRES',
                            'f2d_tide-nopressbc.slf',
                            eps=[9e-4, 8e-4, 3e-3, 3e-3, 2e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_4:T2DRES',
                            'f2d_tide-nopressbc.slf',
                            eps=[2e-3, 2e-3, 8e-3, 8e-3, 3e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_4:T2DRES',
                            eps=[2e-3, 2e-3, 0.01, 0.01, 3e-3])


    def _post(self):
        pass
