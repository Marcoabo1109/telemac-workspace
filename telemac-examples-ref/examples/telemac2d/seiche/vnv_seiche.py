
"""
Validation script for seiche
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
        self.rank = 4
        self.tags = ['telemac2d', 'fv']

    def _pre(self):
        """
        Defining the studies
        """

        # seiche scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_seiche.cas')


        # seiche scalar mode
        cas = TelemacCas('t2d_seiche.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_seiche_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_seiche.slf',
                            eps=[1.E-7, 1.E-7, 1.E-6, 1.E-6, 1.E-8])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_seiche.slf',
                            eps=[3.E-6, 1.E-6, 1.E-6, 1.E-6, 1.E-8])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[3.E-6, 1.E-6, 1.E-6, 1.E-6, 1.E-8])


    def _post(self):
        """
        Post-treatment processes
        """

