
"""
Validation script for balzano
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from data_manip.extraction.telemac_file import TelemacFile

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of balzano
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 3
        self.tags = ['telemac2d', "fv"]

    def _pre(self):
        """
        Defining the studies
        """
        #======================================================================
        # kin1 run
        self.add_study('cin1_seq', 'telemac2d', 't2d_balzano-cin1.cas')
        # kin1 run in parallel
        cas = TelemacCas('t2d_balzano-cin1.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('cin1_par', 'telemac2d', 't2d_balzano-cin1_par.cas', cas=cas)
        del cas

        #======================================================================
        # hllc run
        self.add_study('hllc_seq', 'telemac2d', 't2d_balzano-hllc.cas')
        # hllc run in parallel
        cas = TelemacCas('t2d_balzano-hllc.cas', get_dico('telemac2d'))
        cas.set('FINITE VOLUME SCHEME', 5)
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('hllc_par', 'telemac2d', 't2d_balzano-hllc_par.cas', cas=cas)
        del cas


    def _check_results(self):
        """
        Post-treatment processes
        """
        #======================================================================
        # cin1 check
        self.check_epsilons('cin1_seq:T2DRES', 'f2d_balzano-cin1.slf',
                            eps=[1.e-8, 1.e-8, 1.e-8, 1.e-8,
                                 1.e-8, 1.e-8, 1.e-8, 1.e-8])
        self.check_epsilons('cin1_par:T2DRES', 'f2d_balzano-cin1.slf',
                             eps=[1.e-8, 1.e-8, 1.e-8, 1.e-8,
                                  1.e-8, 1.e-8, 1.e-8, 1.e-8])
        self.check_epsilons('cin1_seq:T2DRES', 'cin1_par:T2DRES',
                             eps=[1.e-8, 1.e-8, 1.e-8, 1.e-8,
                                  1.e-8, 1.e-8, 1.e-8, 1.e-8])

         #======================================================================
         # hllc check
        self.check_epsilons('hllc_seq:T2DRES', 'f2d_balzano-hllc.slf',
                             eps=[1.e-8, 1.e-8, 1.e-8, 1.e-8,
                                  1.e-8, 1.e-8, 1.e-8, 1.e-8])
        self.check_epsilons('hllc_par:T2DRES', 'f2d_balzano-hllc.slf',
                             eps=[1.e-3, 1.e-3, 1.e-3, 1.e-3,
                                  1.e-3, 1.e-3, 1.e-3, 1.e-3])
        self.check_epsilons('hllc_seq:T2DRES', 'hllc_par:T2DRES',
                             eps=[1.e-3, 1.e-3, 1.e-3, 1.e-3,
                                  1.e-3, 1.e-3, 1.e-3, 1.e-3])

    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plot3d, vnv_plot2d, vnv_plot1d, vnv_plotbar, \
                vnv_plot1d_polylines, vnv_plot1d_history, vnv_plotbar_cpu_times
        from os import path
        import numpy as np
        #======================================================================
        # GET TELEMAC RESULT FILES:
        #
        # Load all results as a list:
        res_list, res_labels = self.get_study_res(module='T2D', whitelist=['seq'])

        #======================================================================
        # PLOT 1D
        records = [-1]

        for idx, record in enumerate(records):
            vnv_plot1d_polylines(\
                'FREE SURFACE',
                res_list,
                res_labels,
                record=record,
                fig_size=(6, 5),
                y_label='z',
                x_label='x',
                fig_name='img/t2d_balzano_h_{}'.format(record),
                plot_bottom=True)

            vnv_plot1d_polylines(\
                'VELOCITY U',
                res_list,
                res_labels,
                record=record,
                fig_size=(6, 5),
                y_label='z',
                x_label='x',
                fig_name='img/t2d_balzano_u_{}'.format(record))

