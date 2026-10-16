
"""
Validation script for siphon
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
        self.tags = ['telemac2d']

    def _pre(self):
        """
        Defining the studies
        """

        # run with soft boundary scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_soft.cas')


        # run with soft boundary parallel mode
        cas = TelemacCas('t2d_soft.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_soft_par.cas',
                       cas=cas)
        del cas

        # run without soft boundary (default) scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_soft_default.cas')

        # run without soft boundary (default) parallel mode
        cas = TelemacCas('t2d_soft_default.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_soft_default_par.cas',
                       cas=cas)
        del cas


    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_soft.slf',
                            eps=[1e-9])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_soft.slf',
                            eps=[1e-9])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1e-9])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_3:T2DRES',
                            'f2d_soft_default.slf',
                            eps=[1e-13])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_4:T2DRES',
                            'f2d_soft_default.slf',
                            eps=[1e-13])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_4:T2DRES',
                            eps=[1e-13])

    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plot2d
        # Getting files
        res_vnv_1_t2dgeo, _ = self.get_study_res('vnv_1:T2DGEO', load_bnd=True)
        res_vnv_1_t2dres, _ = self.get_study_res('vnv_1:T2DRES')
        res_vnv_3_t2dres, _ = self.get_study_res('vnv_3:T2DRES')

        #Plotting mesh
        vnv_plot2d('',
                   res_vnv_1_t2dgeo,
                   plot_mesh=True,
                   fig_size=(12, 2),
                   fig_name='img/Mesh',
                   annotate_bnd=True)

        # Plotting VELOCITY at final time step (Soft)
        vnv_plot2d('VELOCITY',
                   res_vnv_1_t2dres,
                   xlim=[0, 1000],
                   ylim=[0, 1000],
                   record=-1,
                   cbar_label='Speed (m/s)',
                   nv = 7,
                   vmin = 0.0,
                   vmax = 3.0,
                   cbar_properties={'ticks':[0.0,0.5,1.0,1.5,2.0,2.5,3.0]},
                   filled_contours=True,
                   vectors=True,
                   vectors_scale=35,
                   fig_size=(8, 6),
                   fig_name='img/Inflow-Soft')

        # Plotting VELOCITY at final time step (Default)
        vnv_plot2d('VELOCITY',
                   res_vnv_3_t2dres,
                   xlim=[0, 1000],
                   ylim=[0, 1000],
                   record=-1,
                   cbar_label='Speed (m/s)',
                   nv = 7,
                   vmin = 0.0,
                   vmax = 3.0,
                   cbar_properties={'ticks':[0.0,0.5,1.0,1.5,2.0,2.5,3.0]},
                   filled_contours=True,
                   vectors=True,
                   vectors_scale=35,
                   fig_size=(8, 6),
                   fig_name='img/Inflow-Def')

