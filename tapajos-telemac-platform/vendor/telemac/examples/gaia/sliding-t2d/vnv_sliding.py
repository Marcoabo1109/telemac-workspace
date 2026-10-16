
"""
Validation script for sliding
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
        self.tags = ['telemac2d', 'gaia']

    def _pre(self):
        """
        Defining the studies
        """
        # Test for different sliding formulas for MPM and all slope formulas
        for slide in [1, 2]:
            for slope in [1, 2, 3]:
                t2d_steering_file = 't2d_slide{}'.format(slide)+'_slope{}.cas'.format(slope)
                gai_steering_file = 'gai_slide{}'.format(slide)+'_slope{}.cas'.format(slope)
                t2d_cas = TelemacCas('t2d_sliding.cas', get_dico('telemac2d'))
                t2d_cas.set('GAIA STEERING FILE', gai_steering_file)

                gai_cas = TelemacCas('gai_sliding.cas', get_dico('gaia'))
                gai_cas.set('SEDIMENT SLIDE', slide)
                gai_cas.set('FORMULA FOR SLOPE EFFECT', slope)
                gai_cas.set('FORMULA FOR DEVIATION', slope)
                gai_cas.write(gai_steering_file)

                self.add_study('vnv_slide{}'.format(slide)+'_slope{}'.format(slope),
                           'telemac2d',
                           t2d_steering_file,
                           cas=t2d_cas)
                del t2d_cas
                del gai_cas

                # testing parallel mode for slope=1
                if slope == 1:
                    t2d_steering_file2 = 't2d_slide{}'.format(slide)+'_slope{}_par.cas'.format(slope)
                    t2d_cas_p = TelemacCas('t2d_sliding.cas', get_dico('telemac2d'))
                    t2d_cas_p.set('PARALLEL PROCESSORS', 4)
                    t2d_cas_p.set('GAIA STEERING FILE', gai_steering_file)
                    gai_cas_p = TelemacCas('gai_sliding.cas', get_dico('gaia'))
                    gai_cas_p.set('SEDIMENT SLIDE', slide)
                    gai_cas_p.set('FORMULA FOR SLOPE EFFECT', slope)
                    gai_cas_p.set('FORMULA FOR DEVIATION', slope)

                    self.add_study('vnv_slide{}'.format(slide)+'_slope{}'.format(slope)+'par',
                                   'telemac2d',
                                   t2d_steering_file2,
                                   cas=t2d_cas_p)
                    del t2d_cas_p
                    del gai_cas_p


    def _check_results(self):
        """
        Post-treatment processes
        """
        for slide in [1, 2]:
            for slope in [1, 2, 3]:

        # Comparison with the last time frame of the reference file.
                self.check_epsilons('vnv_slide{}'.format(slide)+'_slope{}'.format(slope)+':T2DRES',
                            'f2d_slide{}'.format(slide)+'_slope{}.slf'.format(slope),
                            eps=[5e-3])
                self.check_epsilons('vnv_slide{}'.format(slide)+'_slope{}'.format(slope)+':GAIRES',
                            'gai_ref_slide{}'.format(slide)+'_slope{}.slf'.format(slope),
                            eps=[5e-3])
                if slope == 1:
                    self.check_epsilons('vnv_slide{}'.format(slide)+'_slope{}par'.format(slope)+':T2DRES',
                            'f2d_slide{}'.format(slide)+'_slope{}.slf'.format(slope),
                                        eps=[5e-3])
                    self.check_epsilons('vnv_slide{}'.format(slide)+'_slope{}par'.format(slope)+':GAIRES',
                            'gai_ref_slide{}'.format(slide)+'_slope{}.slf'.format(slope),
                                        eps=[5e-3])

    def _post(self):
        """
        Post-treatment processes
        """
        import numpy as np
        from os import path
        from postel.plot_vnv import vnv_plot1d_polylines, vnv_plot2d, \
                vnv_plotbar, vnv_plotbar_cpu_times
        #======================================================================
        # GET TELEMAC RESULT FILES:
        #
        geom, _ = self.get_study_res('vnv_slide1_slope1:T2DGEO', load_bnd=True)
        res, _ = self.get_study_res('vnv_slide1_slope1:T2DRES')
        res2, _ = self.get_study_res('vnv_slide2_slope1:T2DRES')
        resgai, _ = self.get_study_res('vnv_slide1_slope1:GAIRES')
        resgai2, _ = self.get_study_res('vnv_slide2_slope1:GAIRES')


        # Load all results as a list:
        res_list, res_labels = self.get_study_res(module='T2D')
#        res_list_p, res_labels_p = self.get_study_res(module='T2D',whitelist=['slope1'])
        # choose only seriel runs
        my_res_labels = np.array(res_labels)
        my_res_list = np.array(res_list)
        # seriel runs
        my_indices = [0,2,3,4,6,7]
        # slope 1
        my_indices_p = [0,1,4,5]
        res_labels_p = list(my_res_labels[my_indices_p])
        res_list_p = list(my_res_list[my_indices_p])
        res_labels = list(my_res_labels[my_indices])
        res_list = list(my_res_list[my_indices])

        # reference data for 20°
        refdata=np.array([[40,0],[70,-10.9191074371],[76.5,-10.9191074371],[106.5,0]])

        # Plot bathy longitudinal section:
        vnv_plot1d_polylines(\
            'BOTTOM',
            res,
            '',
            fig_size=(8, 2),
            record=0,
            fig_name='img/sliding_bathy',
            plot_bottom=True)

        # Plot mesh
        vnv_plot2d(\
            '',
            geom,
            fig_size=(10, 2),
            fig_name='img/sliding_mesh',
            annotate_bnd=False,
            plot_mesh=True)

        #----------------------------------------------------------------------
        # Comparison of bottom (1D slice):
        vnv_plot1d_polylines(\
            'BOTTOM',
            res_list,
            res_labels,
            record=-1,
            fig_size=(8, 5),
            ref_data=refdata,
            ref_label='given angle of repose',
            fig_name='img/sliding_bottom',
            markers=True,
            markevery=15,
            y_label='Bottom (m)',
            plot_bottom=False)
#
        # Comparison of bottom (1D slice) only slope1 (parallel/scalar):
        vnv_plot1d_polylines(\
            'BOTTOM',
            res_list_p,
            res_labels_p,
            record=-1,
            fig_size=(8, 5),
            ref_data=refdata,
            ref_label='given angle of repose',
            fig_name='img/sliding_check_paral',
            markers=True,
            markevery=15,
            y_label='Bottom (m)',
            plot_bottom=False)
#
        # longitudinal slice over time slide 1 slope 1
        vnv_plot1d_polylines(\
            'BOTTOM',
            res,
            record=[0,1,2,3,4,5,6,7,8,9,-1],
            fig_size=(8, 5),
            fig_name='img/sliding1_bottom_time',
            markers=True,
            markevery=15,
            y_label='Bottom (m)',
            plot_bottom=False)
#
        # longitudinal slice over time slide 2 slope 1
        vnv_plot1d_polylines(\
            'BOTTOM',
            res2 ,
            record=[0,1,2,3,4,5,6,7,8,9,-1],
            fig_size=(8, 5),
            fig_name='img/sliding2_bottom_time',
            markers=True,
            markevery=15,
            y_label='Bottom (m)',
            plot_bottom=False)
#
        # final evolution slide 1 slope 1
        vnv_plot2d('BOTTOM',
                   resgai,
                   record=-1,
                   filled_contours=True,
                   fig_size=(10, 4),
                   cbar_label='Bottom evolution (m)',
                   aspect_ratio='equal',
                   vmax=0.0001,
                   vmin=-12,
                   fig_name='img/final_evol')
#
        # final evolution slide 2 slope 1
        vnv_plot2d('BOTTOM',
                   resgai2,
                   record=-1,
                   filled_contours=True,
                   fig_size=(10, 4),
                   cbar_label='Bottom evolution (m)',
                   aspect_ratio='equal',
                   vmax=0.0001,
                   vmin=-12,
                   fig_name='img/final_evol2')
