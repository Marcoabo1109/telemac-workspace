
"""
Validation script for yen
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

        # yen-exp T2D+GAI scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_yen-exp.cas')


        # yen-exp T2D+GAI parallel mode
        cas = TelemacCas('t2d_yen-exp.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_yen-exp_par.cas',
                       cas=cas)

        del cas


        # yen-exp Finite Volume T2D+GAI scalar mode
        self.add_study('vnv_1_vf',
                       'telemac2d',
                       't2d_yen-exp_vf.cas')


        # yen-exp Finite Volume T2D+GAI parallel mode
        cas = TelemacCas('t2d_yen-exp_vf.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2_vf',
                       'telemac2d',
                       't2d_yen-exp_vf_par.cas',
                       cas=cas)

        del cas
        
        # Test for different slope-formulas with MPM 
        for slope in [1, 2, 3]:
            t2d_steering_file = 't2d_yen-exp_slope{}.cas'.format(slope)
            gai_steering_file = 'gai_yen-exp_slope{}.cas'.format(slope)

            t2d_cas = TelemacCas('t2d_yen-exp.cas', get_dico('telemac2d'))
            t2d_cas.set('GAIA STEERING FILE', gai_steering_file)

            gai_cas = TelemacCas('gai_yen-exp.cas', get_dico('gaia'))
            gai_cas.set('BED-LOAD TRANSPORT FORMULA FOR ALL SANDS',1)
            gai_cas.set('FORMULA FOR SLOPE EFFECT', slope)
            gai_cas.set('FORMULA FOR DEVIATION', slope)       
            gai_cas.write(gai_steering_file)

            self.add_study('vnv_slope{}'.format(slope),
                           'telemac2d',
                           t2d_steering_file,
                           cas=t2d_cas)
            del t2d_cas
            del gai_cas


    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:GAIRES',
                            'gai_ref_yen-exp.slf',
                            eps=[1.e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:GAIRES',
                            'gai_ref_yen-exp.slf',
                            eps=[1.e-3])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_2:GAIRES',
                            eps=[1.e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_yen-exp.slf',
                            eps=[1.e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_yen-exp.slf',
                            eps=[1.e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1.e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1_vf:GAIRES',
                            'gai_ref_yen-exp_vf.slf',
                            eps=[1e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2_vf:GAIRES',
                            'gai_ref_yen-exp_vf.slf',
                            eps=[1e-3])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1_vf:GAIRES',
                            'vnv_2_vf:GAIRES',
                            eps=[1e-3])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1_vf:T2DRES',
                            'f2d_yen-exp_vf.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2_vf:T2DRES',
                            'f2d_yen-exp_vf.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1_vf:T2DRES',
                            'vnv_2_vf:T2DRES',
                            eps=[1e-4])

        for slope in [1, 2, 3]:

            # Comparison to reference file
            self.check_epsilons('vnv_slope{}:T2DRES'.format(slope),
                            'f2d_yen-exp_slope{}.slf'.format(slope),
                            eps=[1e-3])

            # Comparison to reference file
            self.check_epsilons('vnv_slope{}:GAIRES'.format(slope),
                            'gai_ref_yen-exp_slope{}.slf'.format(slope),
                            eps=[1e-3])


    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_polylines
        vnv1_t2dres = self.get_study_file('vnv_1:T2DRES')
        res_vnv_1_t2dres = TelemacFile(vnv1_t2dres)


        #======================================================================
        # Load some results as a list:
        res_list,res_labels = self.get_study_res(module='GAI')
        my_res_labels = np.array(res_labels)
        my_res_list = np.array(res_list)
        my_indices = [0,2,4,5,6]
        res_labels = list(my_res_labels[my_indices])
        res_list = list(my_res_list[my_indices])

        #======================================================================
        # filling ref_data from file np.array
        
        data_90 = np.genfromtxt("data/yen_90profilexy-koor.dat", usecols=(1, 2))
        data_180 = np.genfromtxt("data/yen_180profilexy-koor.dat", usecols=(0, 2))                                            
        data_90[:,0]=data_90[:,0]-46.1371
        data_90[:,1]=data_90[:,1]*0.0544
        data_180[:,0]=data_180[:,0]-104.682
        data_180[:,1]=data_180[:,1]*0.0544
        #print(data_90)
        #print(data_180)

        # Plotting bottom at record 0 with mesh
        vnv_plot2d('BOTTOM',
                   res_vnv_1_t2dres,
                   record=0,
                   filled_contours=True,
                   plot_mesh=True,
                   fig_size=(7.5, 9),
                   aspect_ratio='equal',
                   fig_name='img/bottom')

        
       # Comparison normalised evolution measurements to simulations:
        vnv_plot1d_polylines(\
            'CUMUL BED EVOL',
            res_list,
            legend_labels=res_labels,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/90',
            ref_data=data_90,
#            ref_file='data/test.dat',
            markers=True,
            markevery=15,
            y_label='Normalised evolution (m)',
            x_label='Distance (m)',
            y_factor=18.38,
            poly=[[101.1819, 46.1371], [101.1819, 47.1371]],
            poly_number=[100],
            ylim=[-1,1],
            xlim=[0.,1.0],
            plot_bottom=False)

        vnv_plot1d_polylines(\
            'CUMUL BED EVOL',
            res_list,
            legend_labels=res_labels,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/180',
            ref_data=data_180,
#            ref_file='data/test.dat',
            markers=True,
            markevery=15,
            y_label='Normalised evolution (m)',
            x_label='Distance (m)',
            y_factor=18.38,
            poly=[[104.682, 42.6371], [105.682, 42.6371]],
            poly_number=[100],
            ylim=[-1,1],
            xlim=[0.,1.0],
            plot_bottom=False)
        
        def yen_contour(file_name, in_title):
            """
            Custom contour

            @param file_name (str) Name of the result file
            @parma in_title (str) Title of the fig and part of name of file
            """

            import matplotlib.image as image
            from postel.plot2d import plot2d_scalar_filled_contour,plot2d_image

            slf = TelemacFile(file_name)

            evolution = slf.get_data_value('CUMUL BED EVOL', -1)

            #scale evolution
            h0_factor = 0.0544
            evolution = evolution/h0_factor

            data_xmin = 96.6819 -0.08
            data_xmax = 105.6819 + 0.37
            data_ymin = 42.6371 + 0.95
            data_ymax = 42.6371 + 0.95

            title = in_title + "_EvolutionR04"

            xmin = data_xmin -0.2
            xmax = data_xmax -0.055

            ymin = data_ymin -3.3
            ymax = data_ymax + 3.83

            fig, ax = plt.subplots(1, 1, figsize=(12, 12))
            plot2d_scalar_filled_contour(fig, ax,
                    slf.tri, evolution,
                    nv=7,
                    vmin=-0.75,
                    vmax=0.75,
                    data_name='Normalised evolution (m)')
            plot2d_image(ax, image_file='data/PaperDataRun4.png',
                         extent=[xmin, xmax, ymin, ymax],
                         zorder=+1)
            plt.ylim([40,48])
            print(" "*8+"~> Plotting "+title)
            plt.savefig('img/' + title + ".png")
            plt.close('all')

            slf.close()

        yen_contour(self.get_study_file('vnv_1:GAIRES'), 'gaia_yen-exp')

        yen_contour(self.get_study_file('vnv_1_vf:GAIRES'), 'gaia_yen-exp_vf')
