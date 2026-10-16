
"""
Validation script for seccurrents
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
        # rank is moved to 5 (not tested) until
        # seccurent functionality has been improved
        self.rank = 5
        self.tags = ['telemac2d']

    def _pre(self):
        """
        Defining the studies
        """

        # seccurrents scalar mode
        self.add_study('vnv_seq',
                       'telemac2d',
                       't2d_seccurrents.cas')


        # seccurrents scalar mode
        cas = TelemacCas('t2d_seccurrents.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_par',
                       'telemac2d',
                       't2d_seccurrents_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_seq:T2DRES',
                            'f2d_seccurrents.slf',
                            eps=[1., 1., 1.e-2, 1.e-2,
                                 1.e-6, 10., 1.e-1, 1.,
                                 1., 1.e-1, 1.e-1, 100.,
                                 100., 10.])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_par:T2DRES',
                            'f2d_seccurrents.slf',
                            eps=[1., 1., 1.e-2, 1.e-2,
                                 1.e-6, 10., 1.e-1, 1.,
                                 1., 1.e-1, 1.e-1, 100.,
                                 100., 10.])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_seq:T2DRES',
                            'vnv_par:T2DRES',
                            eps=[1., 1., 1.e-2, 1.e-2,
                                 1.e-6, 10., 1.e-1, 1.,
                                 1., 1.e-1, 1.e-1, 100.,
                                 100., 10.])


    def _post(self):
        """
        Post-treatment processes
        """

