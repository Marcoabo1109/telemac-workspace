
"""
Validation script for waq3d_eutro_streeter_phelps
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from data_manip.extraction.telemac_file import TelemacFile
from postel.plot_vnv import get_data

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 4
        self.tags = ['telemac2d', 'waqtel']

    def _pre(self):
        """
        Defining the studies
        """

        # water quality- dissolved biomas process
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_waq2d_eutro_streeter_phelps.cas')

        # water quality- dissolved biomas process
        cas = TelemacCas('t2d_waq2d_eutro_streeter_phelps.cas', get_dico('telemac2d'))
        cas_waq = TelemacCas('waq_eutro_streeter_phelps.cas', get_dico('waqtel'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_waq2d_eutro_streeter_phelps_par.cas',
                       cas=cas)

        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_waq2d_eutro_streeter_phelps.slf',
                            eps=[1.E-5, 1.E-6, 1.E-5, 1.E-5, 1.E-15,
                                 1.E-15, 1.E-5, 1.E-15, 1.E-15, 1.E-15,
                                 1.E-15, 1.E-15, 1.E-15, 1.E-6, 1.E-6])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_waq2d_eutro_streeter_phelps.slf',
                            eps=[1.E-5, 1.E-6, 1.E-5, 1.E-5, 1.E-15,
                                 1.E-15, 0.9, 1.E-15, 1.E-15, 1.E-15,
                                 1.E-15, 1.E-15, 1.E-15, 0.09, 0.09])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1.E-5, 1.E-6, 1.E-5, 1.E-5, 1.E-15,
                                 1.E-15, 0.9, 1.E-15, 1.E-15, 1.E-15,
                                 1.E-15, 1.E-15, 1.E-15, 0.09, 0.09])

    def _post(self):
        """
        Post-treatment processes
        """

        from os import path
        import math
        import matplotlib.pyplot as plt
        import numpy as np

        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_polylines

        # Getting file
        geom, _ = self.get_study_res('vnv_1:T2DGEO', load_bnd=True)
        res1, _ = self.get_study_res('vnv_1:T2DRES')

        # Plotting mesh
        vnv_plot2d('',
                   geom,
                   plot_mesh=True,
                   fig_size=(15., 3.),
                   fig_name='img/res_mesh',
                   annotate_bnd=True)

        # Analytical solution
        WATSAL=0.0
        WATTEMP=20.0
        ka=0.9
        kd=0.36
        u=0.045

        Cs= 1.429*(0.0223916*(math.exp(-135.90205+(1.575701*10**5)/(WATTEMP+273.15)
           -(6.642308*10**7)/(WATTEMP+273.15)**2+(1.2438*10**10)/(WATTEMP+273.15)**3
           -(8.621949*10**11)/(WATTEMP+273.15)**4
           -WATSAL*(0.017674-10.754/(WATTEMP+273.15)+2140.7/(WATTEMP+273.15)**2))))

        C0=Cs
        L0=10.0

        xl = np.linspace(0, 30000, 3000)

        yl = [Cs -(Cs-C0) * math.exp(-ka/86400.*np.array(x)/u)
            -kd * L0 /(ka-kd)*(  math.exp(-kd/86400.*np.array(x)/u)
                               - math.exp(-ka/86400.*np.array(x)/u))
        for x in xl]

        data_analytic=np.squeeze(np.array([xl,yl]))
        data_analytic=np.transpose(data_analytic)

        # Plot results

        times = res1.times/3600.

        records = [-1]

        fig, ax = plt.subplots(figsize=(10,5))

        for idx, record in enumerate(records):
            vnv_plot1d_polylines(
                var_name='DISSOLVED O2',
                res=res1,
                legend_labels='T2D',
                fig_size=(8., 5.),
                fig_title='DISSOLVED O2',
                ref_name=None,
                ref_file=None,
                ref_data=data_analytic,
                ref_label='analytical solution',
                poly=[[0., 200.], [30000., 200.]],
                poly_number=None,
                record=record,
                time=None,
                fig_name='img/res_O2',
                xlim=None,
                ylim=[0,16],
                x_factor=1.,
                y_factor=1.,
                x_label='x (m)',
                y_label='mgO2/l',
                plot_bottom=False,
                bottom_label='bottom',
                markers=False,
                markevery=15)

        plt.close('all')

        res1.close()
        geom.close()
