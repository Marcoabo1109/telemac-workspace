
"""
Validation script for flotteurs
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

        # flotteurs scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_flotteurs_v1p0.cas')


        # flotteurs parallel mode
        cas = TelemacCas('t2d_flotteurs_v1p0.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_flotteurs_v1p0_par.cas',
                       cas=cas)

        del cas


        # flotteurs scalar mode
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_flotteurs_v2p0.cas')


        # flotteurs parallel mode
        cas = TelemacCas('t2d_flotteurs_v2p0.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_flotteurs_v2p0_par.cas',
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
        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_history, vnv_plot1d_polylines
                # Getting files
        vnv_1_t2dres = self.get_study_file('vnv_1:T2DRES')
        res_vnv_1_t2dres = TelemacFile(vnv_1_t2dres)
        vnv_1_t2dgeo = self.get_study_file('vnv_1:T2DGEO')
        res_vnv_1_t2dgeo = TelemacFile(vnv_1_t2dgeo)

        #Plotting FREE SURFACE on [270, 500], [1030, 460] over records range(0, res_vnv_1_t2dres.ntimestep)
        vnv_plot1d_history(\
                'FREE SURFACE',
                res_vnv_1_t2dres,
                'FREE SURFACE',
                points=[[270, 500], [1030, 460]],
                fig_size=(12, 5),
                fig_name='img/FreeSurfaceTimeSeries')


        # Plotting FREE SURFACE over polyline over records range(0, res_vnv_1_t2dres.ntimestep, 10)
        vnv_plot1d_polylines(\
                'FREE SURFACE',
                res_vnv_1_t2dres,
                poly=[[0, 500], [1000, 500]],
                record=[i for i in range(0, res_vnv_1_t2dres.ntimestep, 10)],
                fig_size=(12, 5),
                fig_name='img/FreeSurfaceProfiles')

        #Plotting mesh
        vnv_plot2d('',
                   res_vnv_1_t2dgeo,
                   plot_mesh=True,
                   fig_size=(15, 7),
                   fig_name='img/Mesh')


        # Plotting FREE SURFACE at -1
        vnv_plot2d('FREE SURFACE',
                   res_vnv_1_t2dres,
                   record=-1,
                   filled_contours=True,
                   fig_size=(15, 7),
                   fig_name='img/FreeSurfacetf')


        # Plotting FREE SURFACE at 1
        vnv_plot2d('FREE SURFACE',
                   res_vnv_1_t2dres,
                   record=1,
                   filled_contours=True,
                   fig_size=(15, 7),
                   fig_name='img/FreeSurfacet1')

        # Closing files
        res_vnv_1_t2dres.close()
        res_vnv_1_t2dgeo.close()
