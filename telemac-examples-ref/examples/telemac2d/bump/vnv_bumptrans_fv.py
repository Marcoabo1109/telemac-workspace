
"""
Validation script for bumpsub
"""
import numpy as np
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from analytic_sol import BumpAnalyticSol

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 0
        self.tags = ['telemac2d', 'fv']

        # Boundary conditions:
        self.q_in = 0.45
        self.h_out = 0.35

        # Analytic solution:
        self.sol = BumpAnalyticSol(\
            flow='trans', Q=self.q_in, hl=self.h_out, length=20.,\
            bottom_function='exponential', N=801)
        self.sol()

    def set_bumptrans_values(self, cas):
        cas.set('PRESCRIBED FLOWRATES', [0., self.q_in])
        cas.set('PRESCRIBED ELEVATIONS', [self.h_out, 0.])


    def _pre(self):
        """
        Defining the studies
        """
        #======================================================================
        # ROE run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 0)
        self.add_study('roe_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # ROE parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('roe_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # KIN1 run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 1)
        self.add_study('kin1_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # KIN1 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('kin1_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # KIN2 run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 1)
        cas.set('FINITE VOLUME SCHEME SPACE ORDER', 2)
        self.add_study('kin2_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # KIN2 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('kin2_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # ZOKAGOA run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 3)
        self.add_study('zoka_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # ZOKAGOA parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('zoka_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # TCHAMEN run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 4)
        self.add_study('tcha_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # TCHAMEN parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('tcha_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # HLLC1 run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 5)
        self.add_study('hllc1_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # HLLC1 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('hllc1_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # HLLC2 run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 5)
        cas.set('FINITE VOLUME SCHEME SPACE ORDER', 2)
        self.add_study('hllc2_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        # HLLC2 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('hllc2_par', 'telemac2d', 't2d_bump_FV_par.cas', cas=cas)
        del cas

        #======================================================================
        # WAF run
        cas = TelemacCas('t2d_bump_FV.cas', get_dico('telemac2d'))
        self.set_bumptrans_values(cas)
        cas.set('FINITE VOLUME SCHEME', 6)
        self.add_study('waf_seq', 'telemac2d', 't2d_bump_FV.cas', cas=cas)
        del cas

        #======================================================================
        # Copy of analytic solution in studies for initialization
        for name, study in self.studies.items():
            self.sol.savetxt(path=self.get_vnv_working_dir(name))

    def _check_results(self):
        """
        Post-treatment processes
        """
        self.check_epsilons('roe_seq:T2DRES', 'f2d_bumptrans-roe.slf', eps=[1e-8])
        self.check_epsilons('roe_par:T2DRES', 'f2d_bumptrans-roe.slf', eps=[1e-8])
        self.check_epsilons('roe_seq:T2DRES', 'roe_par:T2DRES', eps=[1e-8])

        self.check_epsilons('kin1_seq:T2DRES', 'f2d_bumptrans-kin1.slf', eps=[1e-8])
        self.check_epsilons('kin1_par:T2DRES', 'f2d_bumptrans-kin1.slf', eps=[1e-8])
        self.check_epsilons('kin1_seq:T2DRES', 'kin1_par:T2DRES', eps=[1e-8])

        self.check_epsilons('kin2_seq:T2DRES', 'f2d_bumptrans-kin2.slf', eps=[1.])
        self.check_epsilons('kin2_par:T2DRES', 'f2d_bumptrans-kin2.slf', eps=[1.])
        self.check_epsilons('kin2_seq:T2DRES', 'kin2_par:T2DRES', eps=[1.])

        self.check_epsilons('zoka_seq:T2DRES', 'f2d_bumptrans-zoka.slf', eps=[1e-8])
        self.check_epsilons('zoka_par:T2DRES', 'f2d_bumptrans-zoka.slf', eps=[1e-8])
        self.check_epsilons('zoka_seq:T2DRES', 'zoka_par:T2DRES', eps=[1e-8])

        self.check_epsilons('tcha_seq:T2DRES', 'f2d_bumptrans-tcha.slf', eps=[1e-8])
        self.check_epsilons('tcha_par:T2DRES', 'f2d_bumptrans-tcha.slf', eps=[1e-8])
        self.check_epsilons('tcha_seq:T2DRES', 'tcha_par:T2DRES', eps=[1e-8])

        self.check_epsilons('hllc1_seq:T2DRES', 'f2d_bumptrans-hllc.slf', eps=[1e-8])
        self.check_epsilons('hllc1_par:T2DRES', 'f2d_bumptrans-hllc.slf', eps=[1e-8])
        self.check_epsilons('hllc1_seq:T2DRES', 'hllc1_par:T2DRES', eps=[1e-8])

        self.check_epsilons('hllc2_seq:T2DRES', 'f2d_bumptrans-hllc2.slf', eps=[1.])
        self.check_epsilons('hllc2_par:T2DRES', 'f2d_bumptrans-hllc2.slf', eps=[1.])
        self.check_epsilons('hllc2_seq:T2DRES', 'hllc2_par:T2DRES', eps=[1.])

        self.check_epsilons('waf_seq:T2DRES', 'f2d_bumptrans-waf.slf', eps=[2e-1])

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
        records = [0, -1]

        for idx, record in enumerate(records):
            vnv_plot1d_polylines(\
                'FREE SURFACE',
                res_list,
                res_labels,
                record=record,
                fig_size=(6, 5),
                y_label='z',
                x_label='x',
                fig_name='img/t2d_bumptrans_fvschemes_comparison_{}'.format(record),
                plot_bottom=True)

