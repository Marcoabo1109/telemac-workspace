
"""
Validation script for yen_multi
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
        self.tags = ['telemac2d', 'gaia']
        # Forcing listing
        self.listing = True

    def _pre(self):
        """
        Defining the studies
        """

        # yen-exp_multi T2D+GAI scalar mode
        self.add_study('vnv_multi1',
                       'telemac2d',
                       't2d_yen-exp_multi1.cas')


        # yen-exp_multi T2D+GAI scalar mode
        for bed_form in [2, 3, 4, 5, 6, 7, 10, 30, 9]:
            t2d_steering_file = 't2d_yen-exp_multi{}.cas'.format(bed_form)
            gai_steering_file = 'gai_yen-exp_multi{}.cas'.format(bed_form)

            t2d_cas = TelemacCas('t2d_yen-exp_multi1.cas', get_dico('telemac2d'))
            t2d_cas.set('GAIA STEERING FILE', gai_steering_file)

            gai_cas = TelemacCas('gai_yen-exp_multi1.cas', get_dico('gaia'))
            gai_cas.set('BED-LOAD TRANSPORT FORMULA FOR ALL SANDS', bed_form)
            if bed_form == 9:
                gai_cas.set('LAYERS NON COHESIVE BED POROSITY',
                            [0.37500, 0.375, 0.375, 0.375])
                gai_cas.set('ACTIVE LAYER THICKNESS', 0.01)
                gai_cas.set('NUMBER OF LAYERS FOR INITIAL STRATIFICATION', 4)
            if bed_form == 3:
                gai_cas.set('MAXIMUM NUMBER OF ITERATIONS FOR POSITIVE THICKNESS', 50)

            if bed_form == 2 or bed_form == 3 or bed_form == 30 or bed_form == 4:
                gai_cas.set('FORMULA FOR SLOPE EFFECT',1)

            gai_cas.write(gai_steering_file)

            self.add_study('vnv_multi{}'.format(bed_form),
                           'telemac2d',
                           t2d_steering_file,
                           cas=t2d_cas)
            del t2d_cas
            del gai_cas


        for hid_form in [1, 2, 4]:
            t2d_steering_file = 't2d_yen-exp_multi1_hid{}.cas'.format(hid_form)
            gai_steering_file = 'gai_yen-exp_multi1_hid{}.cas'.format(hid_form)

            t2d_cas = TelemacCas('t2d_yen-exp_multi1.cas', get_dico('telemac2d'))
            t2d_cas.set('GAIA STEERING FILE', gai_steering_file)

            gai_cas = TelemacCas('gai_yen-exp_multi1.cas', get_dico('gaia'))
            gai_cas.set('HIDING FACTOR FORMULA', hid_form)
            gai_cas.write(gai_steering_file)

            self.add_study('vnv_multi1_hid{}'.format(hid_form),
                           'telemac2d',
                           t2d_steering_file,
                           cas=t2d_cas)
            del t2d_cas
            del gai_cas

    def _check_results(self):
        """
        Post-treatment processes
        """
        for bed_form in [1, 2, 3, 4, 5, 6, 7, 10, 30, 9]:
        
            # Comparison with the last time frame of the reference file.
            self.check_epsilons('vnv_multi{}:GAIRES'.format(bed_form),
                            'gai_ref_multi{}.slf'.format(bed_form),
                            eps=[1e-3])

            # Comparison with the last time frame of the reference file.
            self.check_epsilons('vnv_multi{}:T2DRES'.format(bed_form),
                            'f2d_multi{}.slf'.format(bed_form),
                            eps=[1e-3])

        for hid_form in [1, 2, 4]:
            # Comparison with the last time frame of the reference file.
            self.check_epsilons('vnv_multi1_hid{}:GAIRES'.format(hid_form),
                            'gai_ref_multi1_hid{}.slf'.format(hid_form),
                            eps=[1e-3])

            # Comparison with the last time frame of the reference file.
            self.check_epsilons('vnv_multi1_hid{}:T2DRES'.format(hid_form),
                            'f2d_multi1_hid{}.slf'.format(hid_form),
                            eps=[1e-3])

    def _post(self):
        """
        Post-treatment processes
        """
        from postel.parser_output import get_latest_output_files
        from postel.parser_output import OutputFileData
        from postel.plot_vnv import vnv_plot1d,vnv_plot1d_polylines
        import matplotlib.pyplot as plt
        import numpy as np

        #======================================================================
        # Load some results as a list:
        res_list,res_labels = self.get_study_res(module='GAI')
        my_res_labels = np.array(res_labels)
        my_res_list = np.array(res_list)
        my_indices = [0,1,2,3,4,5,6,7,8,9]
        my_indices2 = [10,11,12]
        res_labels1 = list(my_res_labels[my_indices])
        res_list1 = list(my_res_list[my_indices])
        res_labels2 = list(my_res_labels[my_indices2])
        res_list2 = list(my_res_list[my_indices2])
        #======================================================================
        # filling ref_data from file np.array
        
        data_90 = np.genfromtxt("data/yen_90profilexy-koor.dat", usecols=(1, 2))
        data_180 = np.genfromtxt("data/yen_180profilexy-koor.dat", usecols=(0, 2))                                            
        data_90[:,0]=data_90[:,0]-46.1371
        data_90[:,1]=data_90[:,1]*0.0544
        data_180[:,0]=data_180[:,0]-104.682
        data_180[:,1]=data_180[:,1]*0.0544

          # Comparison normalised evolution measurements to simulations:
        vnv_plot1d_polylines(\
            'CUMUL BED EVOL',
            res_list1,
            legend_labels=res_labels1,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/90_multi',
            ref_data=data_90,
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
            res_list1,
            legend_labels=res_labels1,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/180_multi',
            ref_data=data_180,
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

        vnv_plot1d_polylines(\
            'CUMUL BED EVOL',
            res_list2,
            legend_labels=res_labels2,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/90_multi1',
            ref_data=data_90,
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
            res_list2,
            legend_labels=res_labels2,
            record=-1,
            fig_size=(8, 5),
            ref_label='measurements',                 
            fig_name='img/180_multi1',
            ref_data=data_180,
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
            plt.title(title)
            print(" "*8+"~> Plotting "+title)
            plt.savefig('img/' + title + ".png")
            plt.close('all')

            slf.close()

        for bed_form in [1, 2, 3, 4, 5, 6, 7, 10, 30, 9]:
            res_file = self.get_study_file('vnv_multi{}:GAIRES'.format(bed_form))
            title = 'gaia_yen-exp_multi{}'.format(bed_form)
            #yen(res_file, title)
            yen_contour(res_file, title)

        for hid_form in [1, 2, 4]:
            res_file = self.get_study_file('vnv_multi1_hid{}:GAIRES'.format(hid_form))
            title = 'gaia_yen-exp_multi1_hid{}'.format(hid_form)
            #yen(res_file, title)
            yen_contour(res_file, title)

        for bed_form in [1, 2, 3, 4, 5, 6, 7, 10, 30, 9]:
            cas_file = self.studies['vnv_multi{}'.format(bed_form)].steering_file

            file_name = get_latest_output_files(cas_file)

            file_name = file_name[0]
            out_file = OutputFileData(file_name)

            mass = out_file.get_sediment_mass_profile()

            tmp_iterations, tmp_times = out_file.get_time_profile()
            _, iterations = tmp_iterations
            _, times = tmp_times
            sed_class = 0
            ttype = 'Lost'

            data = np.zeros(len(mass[sed_class][ttype.lower()]))

            for i in range(0, len(data)):
                data[i] += data[-1] + mass[sed_class][ttype.lower()][i]

            title = "{}_{:02d}".format(ttype.lower(), sed_class)

            vnv_plot1d(times[2::2], data,
                       [title],
                       x_label="time (s)", y_label="Cumulated lost mass",
                       fig_name="img/multi{}_{}.png".format(bed_form, title))

