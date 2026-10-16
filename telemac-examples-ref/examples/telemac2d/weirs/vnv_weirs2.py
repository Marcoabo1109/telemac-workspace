
"""
Validation script for weirs2
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
        self.rank = 2
        self.tags = ['telemac2d']

    def _pre(self):
        """
        Defining the studies
        """

        # weirs2 scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_weirs2.cas')


        # weirs2 parallel mode
        cas = TelemacCas('t2d_weirs2.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_weirs2_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_weirs2.slf',
                            eps=[1.E-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_weirs2.slf',
                            eps=[1.E-3])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1.E-3])


    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_polylines
        # Getting files
        vnv_1_t2dgeo = self.get_study_file('vnv_1:T2DGEO')
        vnv_1_t2dres = self.get_study_file('vnv_1:T2DRES')
        res_vnv_1_t2dgeo = TelemacFile(vnv_1_t2dgeo)
        res_vnv_1_t2dres = TelemacFile(vnv_1_t2dres)

        # Plotting FREE SURFACE over polyline over records [0, 1, 2, 3, 4]
        vnv_plot1d_polylines(\
            'FREE SURFACE',
            res_vnv_1_t2dres, 'Elevation',
            fig_size=(8, 4),
            poly=[[0, 500], [2600., 500.0], [2600., 1550.0], [0, 1550.0]],
            record=[0, 1, 2, 3, 4],
            fig_name='img/weirs2_free_surface')

        # Plotting BOTTOM
        vnv_plot2d(\
            '',
            res_vnv_1_t2dgeo,
            record=0,
            plot_mesh=True,
            fig_size=(5.5, 5),
            fig_name='img/weirs2_geo')

        # Plotting VELOCITY
        records = [0, 1, 2, 3]
        fig_names = ['img/weirs2_figure_velo1500s', \
                     'img/weirs2_figure_velo3000s', \
                     'img/weirs2_figure_velo4500s', \
                     'img/weirs2_figure_velo6000s']

        for idx, record in enumerate(records):
            vnv_plot2d(\
                'VELOCITY',
                res_vnv_1_t2dres,
                record=record,
                filled_contours=True,
                vectors=True,
                vectors_scale=10,
                fig_size=(6, 5),
                fig_name=fig_names[idx],
                annotate_time=True)

        # Closing files
        res_vnv_1_t2dgeo.close()
        res_vnv_1_t2dres.close()
