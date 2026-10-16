
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
        self.rank = 1
        self.tags = ['telemac2d', 'fv']

    def _pre(self):
        """
        Defining the studies
        """

        # friction channel in 2D finite volume
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_friction.cas')


        # friction channel finite volume parallel mode
        cas = TelemacCas('t2d_friction.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_friction_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_friction.slf',
                            eps=[1e-12])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_friction.slf',
                            eps=[1e-12])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1e-12])


    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plot1d_polylines
        # Getting files
        vnv_1_t2dres = self.get_study_file('vnv_1:T2DRES')
        res = TelemacFile(vnv_1_t2dres)

        # Plot water depth:
        vnv_plot1d_polylines(\
            'WATER DEPTH', res, 'water depth',
            fig_size=(12, 3),
            record=-1,
            poly=[[0.0, 225.0], [41000.0, 225.0]],
            ref_name='EXACT DEPTH',
            fig_name='img/figure1')

        # Plot free surface:
        vnv_plot1d_polylines(\
            'FREE SURFACE', res, 'elevation',
            fig_size=(13, 3),
            record=-1,
            poly=[[0.0, 225.0], [41000.0, 225.0]],
            ref_name='EXACT ELEVATION',
            fig_name='img/figure2')

        res.close()
