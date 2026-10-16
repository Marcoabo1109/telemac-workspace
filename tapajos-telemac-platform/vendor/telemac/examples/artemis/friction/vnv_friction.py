
"""
Validation script for friction
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
        self.rank = 0
        self.tags = ['artemis']

    def _pre(self):
        """
        Defining the studies
        """

        # friction scalar mode
        self.add_study('vnv_1',
                       'artemis',
                       'art_friction.cas')


        # friction parallel mode
        cas = TelemacCas('art_friction.cas', get_dico('artemis'))
        cas.set('PARALLEL PROCESSORS', 4)
        cas.set('SOLVER', 9)


        self.add_study('vnv_2',
                       'artemis',
                       'art_friction_par.cas',
                       cas=cas)

        del cas
        # friction scalar mode
        self.add_study('vnv_3',
                       'artemis',
                       'art_friction_skin.cas')



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:ARTRES',
                            'f2d_friction.slf',
                            eps=[1.e-7, 5.e-7, 1.e-7, 1.e-8, 1.e-8, 1.e-8, 1.e-8, 1.e-7, 1.e-7, 1.e-8, 1.e-8])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:ARTRES',
                            'f2d_friction.slf',
                            eps=[1.e-7, 5.e-7, 1.e-7, 1.e-8, 1.e-8, 0.001, 1.e-4, 0.2, 1.e-5, 1.e-5, 1.e-5])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:ARTRES',
                            'vnv_2:ARTRES',
                            eps=[1.e-8, 1.e-8, 1.e-8, 1.e-8, 1.e-8, 0.001, 1.e-4, 0.2, 1.e-5, 1.e-5, 1.e-5])


    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt
        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_polylines
        from postel.plot1d import plot1d
        # Getting files
        vnv_1_artres = self.get_study_file('vnv_1:ARTRES')
        res_vnv_1_artres = TelemacFile(vnv_1_artres)
        vnv_1_artgeo = self.get_study_file('vnv_1:ARTGEO')
        res_vnv_1_artgeo = TelemacFile(vnv_1_artgeo)
        vnv_3_artres = self.get_study_file('vnv_3:ARTRES')
        res_vnv_3_artres = TelemacFile(vnv_3_artres)

        # Plotting WAVE HEIGHT over polyline
        poly=[[0, 0.6], [19.9, 0.6]]
        polydis, absc, skin = res_vnv_3_artres.get_data_on_polyline('WAVE HEIGHT', -1, poly)
        polydis, absc, full = res_vnv_1_artres.get_data_on_polyline('WAVE HEIGHT', -1, poly)
        _, axe = plt.subplots()
        plot1d(axe, polydis[:,0], full,
               plot_label='Wave height with full roughness')
        plot1d(axe, polydis[:,0], skin,
               plot_label='Wave height with skin roughness')
        axe.set(xlim=[0, 20], ylim=[0.15, 0.18])
        axe.legend()
        fig_name = 'img/profile'
        plt.savefig(fig_name)
        plt.close('all')
 
        #Plotting mesh
        vnv_plot2d('',
                   res_vnv_1_artgeo,
                   plot_mesh=True,
                   fig_size=(12, 4),
                   fig_name='img/Mesh')


        # Plotting WAVE HEIGHT at 0
        vnv_plot2d('WAVE HEIGHT',
                   res_vnv_1_artres,
                   record=0,
                   filled_contours=True,
                   cmap_name='viridis',
                   fig_size=(12, 4),
                   fig_name='img/Wave_height')


        # Plotting FREE SURFACE at -1
        vnv_plot2d('FREE SURFACE',
                   res_vnv_1_artres,
                   record=-1,
                   filled_contours=True,
                   cmap_name='viridis',
                   fig_size=(12, 4),
                   fig_name='img/Free_Surface')

        # Closing files
        res_vnv_1_artres.close()
        res_vnv_1_artgeo.close()
