"""
Validation script for bump juste check that the template steering file are
running
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
        self.tags = ['telemac2d']

    def _pre(self):
        """
        Defining the studies
        """
        self.add_study('fe_seq',
                       'telemac2d',
                       't2d_bump_FE.cas')

        cas = TelemacCas('t2d_bump_FE.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('fe_par',
                       'telemac2d',
                       't2d_bump_FE_par.cas',
                       cas=cas)
        del cas


        self.add_study('fv_seq',
                       'telemac2d',
                       't2d_bump_FV.cas')

        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('fv_par',
                       'telemac2d',
                       't2d_bump_FV_par.cas',
                       cas=cas)
        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """

    def _post(self):
        """
        Post-treatment processes
        """
