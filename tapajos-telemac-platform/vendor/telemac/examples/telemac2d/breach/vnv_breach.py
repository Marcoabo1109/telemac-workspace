
"""
Validation script for breach
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico

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

        # breach scalar mode
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_breach.cas')

        # breach parallel mode
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_breach_par.cas',
                       cas=cas)

        # initiation criteria 4 and 5
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('FORTRAN FILE','user_fortran')
        cas.set('FORMATTED RESULTS FILE','crit4+5_evolutions.txt')
        cas.set('BREACHES DATA FILE','breach_crit4+5.txt')

        self.add_study('vnv_crit4_5_seq',
                       'telemac2d',
                       't2d_breach_crit4+5.cas',
                       cas=cas)

        # initiation criteria 4 and 5 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_crit4_5_paral',
                       'telemac2d',
                       't2d_breach_crit4+5_par.cas',
                       cas=cas)

        # initiation criteria 4 and 5 but water in the floodplain: breach not opens
        self.add_study('vnv_crit4_5_no_breaching',
                       'telemac2d',
                       't2d_no_breach.cas')

        # two steps scalar mode
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('BREACHES DATA FILE','breach_2steps.txt')

        self.add_study('vnv_2steps',
                       'telemac2d',
                       't2d_breach_2steps.cas',
                       cas=cas)

        # two steps parallel mode
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2steps_paral',
                       'telemac2d',
                       't2d_breach_2steps_par.cas',
                       cas=cas)

        # USBR and Von Thun scalar mode
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('BREACHES DATA FILE','breach_USBR_VonThun.txt')

        self.add_study('vnv_USBR_VonThun',
                       'telemac2d',
                       't2d_breach_USBR_VonThun.cas',
                       cas=cas)

        # USBR and Von Thun parallel mode
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_USBR_VonThun_paral',
                       'telemac2d',
                       't2d_breach_USBR_VonThun_par.cas',
                       cas=cas)

        # Verheij2002 and Verheij2003 scalar mode
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('BREACHES DATA FILE','breach_Verheij2002_Verheij2003.txt')

        self.add_study('vnv_Verheij2002_Verheij2003',
                       'telemac2d',
                       't2d_breach_Verheij2002_Verheij2003.cas',
                       cas=cas)

        # Verheij2002 and Verheij2003 parallel mode
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_Verheij2002_Verheij2003_paral',
                       'telemac2d',
                       't2d_breach_Verheij2002_Verheij2003_par.cas',
                       cas=cas)

        # Froehlich scalar mode
        cas = TelemacCas('t2d_breach.cas', get_dico('telemac2d'))
        cas.set('BREACHES DATA FILE','breach_Froehlich.txt')

        self.add_study('vnv_Froehlich',
                       'telemac2d',
                       't2d_breach_Froehlich.cas',
                       cas=cas)

        # Froehlich parallel mode
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_Froehlich_paral',
                       'telemac2d',
                       't2d_breach_Froehlich_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_breach.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T2DRES',
                            'f2d_breach.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2steps:T2DRES',
                            'f2d_breach_2steps.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2steps_paral:T2DRES',
                            'f2d_breach_2steps.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_2steps:T2DRES',
                            'vnv_2steps_paral:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_USBR_VonThun:T2DRES',
                            'f2d_breach_USBR_VonThun.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_USBR_VonThun_paral:T2DRES',
                            'f2d_breach_USBR_VonThun.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_USBR_VonThun:T2DRES',
                            'vnv_USBR_VonThun_paral:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_Verheij2002_Verheij2003:T2DRES',
                            'f2d_breach_Verheij2002_Verheij2003.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_Verheij2002_Verheij2003_paral:T2DRES',
                            'f2d_breach_Verheij2002_Verheij2003.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_Verheij2002_Verheij2003:T2DRES',
                            'vnv_Verheij2002_Verheij2003_paral:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_Froehlich:T2DRES',
                            'f2d_breach_Froehlich.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_Froehlich_paral:T2DRES',
                            'f2d_breach_Froehlich.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_Froehlich:T2DRES',
                            'vnv_Froehlich_paral:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_crit4_5_seq:T2DRES',
                            'f2d_breach_crit4+5.slf',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_crit4_5_paral:T2DRES',
                            'f2d_breach_crit4+5.slf',
                            eps=[1e-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_crit4_5_seq:T2DRES',
                            'vnv_crit4_5_paral:T2DRES',
                            eps=[1e-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_crit4_5_no_breaching:T2DRES',
                            'f2d_breach_crit4+5_no_breaching.slf',
                            eps=[1e-4])

    def _post(self):
        """
        Post-treatment processes
        """

        from postel.plot_vnv import vnv_plot2d, vnv_plot1d_polylines,vnv_plot1d
        from postel.plot1d import plot1d
        from postel.plot2d import plot2d_triangle_mesh,plot2d_scalar_filled_contour
        from postel.deco_vnv import decoVNV
        import numpy as np
        import matplotlib.pyplot as plt

        # Getting files
        res_vnv_seq_t2dgeo, _ = self.get_study_res('vnv_1:T2DGEO', load_bnd=True)
        res_vnv_seq_t2dres, _ = self.get_study_res('vnv_1:T2DRES')
        crit4_5_t2dres, _ = self.get_study_res('vnv_crit4_5_seq:T2DRES', load_bnd=True)
        crit4_5_no_breaching_t2dres, _ = self.get_study_res('vnv_crit4_5_no_breaching:T2DRES', load_bnd=True)

        #Plotting mesh
        vnv_plot2d('',
                   res_vnv_seq_t2dgeo,
                   plot_mesh=True,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_geo',
                   annotate_bnd=True)

        #Plotting mesh zoom
        vnv_plot2d('',
                   res_vnv_seq_t2dgeo,
                   xlim=[1500.0, 2500.0],
                   ylim=[0., 100.],
                   plot_mesh=True,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_mesh2')

        # Plotting BOTTOM at 0
        vnv_plot2d('BOTTOM',
                   res_vnv_seq_t2dres,
                   record=0,
                   cbar_label='Bottom elevation (m)',
                   filled_contours=True,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_bathy')

        # Plotting 1d BOTTOM at the beginning of the channel
        vnv_plot1d_polylines('BOTTOM',
                   res_vnv_seq_t2dres,
                   poly=[(10,0),(10,26)],
                   record=0,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_channel_section',
                   plot_bottom=True)

        # Plotting 1d BOTTOM over the dike
        vnv_plot1d_polylines('BOTTOM',
                   res_vnv_seq_t2dres,
                   ylim=[3.,8.5],
                   poly=[(2050,0),(2050,50)],
                   record=0,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_dyke_section',
                   plot_bottom=True)

        # Plotting evolution of breaching for br1
        vnv_plot1d_polylines('BOTTOM',
                   crit4_5_t2dres,
                   poly=[(2000,37),(2120,37)],
                   record=[27,28,29,30,31,32,33] ,
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_evolution_section_br1',
                   plot_bottom=False)
#
        # Plotting evolution of breaching for br2
        vnv_plot1d_polylines('BOTTOM',
                   crit4_5_t2dres,
                   poly=[(2430,37),(2570,37)],
                   record=[30,31,33,36,39,42,45],
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_evolution_section_br2',
                   plot_bottom=False)
#
        # Plotting evolution of breaching for br3
        vnv_plot1d_polylines('BOTTOM',
                   crit4_5_t2dres,
                   poly=[(2880,37),(3000,37)],
                   record=[8,9,11,13,15,17,19],
                   fig_size=(9, 3),
                   fig_name='img/t2d_breach_evolution_section_br3',
                   plot_bottom=False)
#
        # Plot bottom for first breach with point locations
        plt.style.use('default')
        plt.rcParams.update(decoVNV)
        fig, ax = plt.subplots(1, 1, figsize=(15, 4))
        mesh = res_vnv_seq_t2dres.tri
        bottom = res_vnv_seq_t2dres.get_data_value('BOTTOM', 0)
        plot2d_scalar_filled_contour(\
            fig, ax, mesh, bottom,
            extend='both',
            data_name='bottom (m)', colorbar=True)
        plot2d_triangle_mesh(ax, mesh, color='k', linewidth=0.1, alpha=.5)
        plt.xlim(1500.0,2500.0)
        plt.ylim(0.,100.)
        plt.plot(2051.05, 23., marker='x', markersize=8, color='k')
        plt.annotate("channel control node", xy=(2051.05, 23.), xytext=(2051.05, 18.))
        plt.plot(2048.21, 55.21, marker='x', markersize=8, color='k')
        plt.annotate("floodplain control node", xy=(2048.21, 55.21), xytext=(2048.21,50.21))
        plt.plot(2000., 40., marker='o', markersize=8, color='k')
        plt.annotate("br1", xy=(2000., 40.), xytext=(1960, 40.))
        plt.plot(2099.1, 40., marker='o', markersize=8, color='k')
        plt.annotate("br1", xy=(2099.1, 40.), xytext=(2110., 40.))
        fig_name = "img/points_br1"
        fig.savefig(fig_name)
        plt.close('all')
#
        # Plot bottom for second breach with point locations
        plt.style.use('default')
        plt.rcParams.update(decoVNV)
        fig, ax = plt.subplots(1, 1, figsize=(15, 4))
        mesh = res_vnv_seq_t2dres.tri
        bottom = res_vnv_seq_t2dres.get_data_value('BOTTOM', 0)
        plot2d_scalar_filled_contour(\
            fig, ax, mesh, bottom,
            extend='both',
            data_name='bottom (m)', colorbar=True)
        plot2d_triangle_mesh(ax, mesh, color='k', linewidth=0.1, alpha=.5)
        plt.xlim(2200.0,2800.0)
        plt.ylim(0.,100.)
        plt.plot(2500., 35.5, marker='x', markersize=8, color='k')
        plt.annotate("weak point", xy=(2500., 35.5), xytext=(2500, 30.))
        plt.plot(2500.25, 13.49, marker='x', markersize=8, color='k')
        plt.annotate("control node", xy=(2500.25, 13.49), xytext=(2500.25,8))
        plt.plot(2450., 40., marker='o', markersize=8, color='k')
        plt.annotate("br2", xy=(2450., 40.), xytext=(2420, 40.))
        plt.plot(2549.55, 40., marker='o', markersize=8, color='k')
        plt.annotate("br2", xy=(2549.55, 40.), xytext=(2560., 40.))
        fig_name = "img/points_br2"
        fig.savefig(fig_name)
        plt.close('all')
#
        # First observations:
        #
        records = [0, 24, 26, 30, 34, -1]
        times = [0.,1440., 1560.,1680.,2040.,2700.]
#
        for itm in range(len(records)):
            time_str = int(times[itm])
            fig_name = 'img/WD_F1_{}_{}_firstobs'.format(time_str, 'crit4+5')
            vnv_plot2d(\
                'WATER DEPTH', crit4_5_t2dres,
                record=records[itm],
                fig_size=(10, 5),
                fig_title='$t = {}$ s'.format(time_str),
                xlim=[1800., 3200.],
                ylim=[0., 100.],
                fig_name=fig_name,
                cbar_label='Water depth (m)',
                filled_contours=True,
                mask_tidal_flats=True,
                tidal_flats_threshold=0.01,
                plot_mesh=True,
                plot_only_dry_mesh=True)
#
        records = [0, 24, 34]
        times = [0.,1440., 2040.]
#
        for itm in range(len(records)):
            time_str = int(times[itm])
            fig_name = 'img/WD_F2_{}_{}_firstobs'.format(time_str, 'crit4+5')
            vnv_plot2d(\
                'WATER DEPTH', crit4_5_no_breaching_t2dres,
                record=records[itm],
                fig_size=(10, 5),
                fig_title='$t = {}$ s'.format(time_str),
                xlim=[1800., 3200.],
                ylim=[0., 100.],
                fig_name=fig_name,
                cbar_label='Water depth (m)',
                filled_contours=True,
                mask_tidal_flats=True,
                tidal_flats_threshold=0.01,
                plot_mesh=True,
                plot_only_dry_mesh=True)
#
        vnv_plot2d(\
            'WATER DEPTH', crit4_5_no_breaching_t2dres,
            record=-1,
            fig_size=(10, 5),
            fig_title='t = 2700 s',
            xlim=[1800., 3200.],
            ylim=[0., 100.],
            fig_name='img/WD_F2_2700_crit4+5_firstobs',
            cbar_label='Water depth (m)',
            filled_contours=True)
#
        res_vnv_seq_t2dgeo.close()
        res_vnv_seq_t2dres.close()
        crit4_5_t2dres.close()
        crit4_5_no_breaching_t2dres.close()
#
        # Check initiation criterion 4 and 5 via ascii file from TELEMAC:
#
        for name, study in self.studies.items():
            if ('vnv_crit4_5') in name:
                times_list = []
                fs_br1_list = []
                fs_br2_list = []
                deltah_list = []

                values_file = self.get_study_file(name+':T2DRFO')
                values = np.genfromtxt(values_file)
                times_list.append(values[:, 0])
                times_list.append(values[:, 0])
                fs_br1_list.append(values[:, 1])
                fs_br2_list.append(values[:, 2])
                deltah_list.append(values[:, 3])
                labels1=["Control node",'Threshold value']
                labels2=["Control node",'Threshold value']
                labels3=['$\Delta$E at nodes','Threshold value']
#
                # Threshold value for hydraulic load is different between case F1 and F2 (cf. breach data file and doc)
                if(name=='vnv_crit4_5_seq'):
                  threshold_h=[1.]*len(values[:, 0])
                else:
                  threshold_h=[2.]*len(values[:, 0])
                threshold_h=np.array(threshold_h)
                deltah_list.append(threshold_h)
#
                # Threshold value for free surface br1
                threshold_br1=np.array([7.2]*len(values[:, 0]))
                fs_br1_list.append(threshold_br1)
#
                # Threshold value for free surface br2
                threshold_br2=np.array([6.]*len(values[:, 0]))
                fs_br2_list.append(threshold_br2)
#
                vnv_plot1d(\
                    times_list,
                    fs_br1_list,
                    labels1,
                    fig_size=(6, 3),
                    x_label='t (s)',
                    y_label='z$_{f}$+h (m)',
                    fig_name='img/t2d_breach_threshold_evolutions_{}_br1'.format(name))
#
                vnv_plot1d(\
                    times_list,
                    fs_br2_list,
                    labels2,
                    fig_size=(6, 3),
                    x_label='t (s)',
                    y_label='z$_{f}$+h (m)',
                    fig_name='img/t2d_breach_threshold_evolutions_{}_br2'.format(name))
#
                vnv_plot1d(\
                    times_list,
                    deltah_list,
                    labels3,
                    fig_size=(6, 3),
                    ylim=[0., 2.5],
                    x_label='t (s)',
                    y_label='$\Delta$E (m)',
                    fig_name='img/t2d_breach_threshold_evolutions_DeltaH_{}_br1'.format(name))
#
        # Check initiation criterion 5 from graphic printouts:
        # List of points where hydraulic load is computed (points of polyline +/- (polygon width)/2)
        # channel side
        points_ch = [[2450.45, 31.], [2453.45,31.], [2456.46,31.],[2459.46,31.],[2462.46,31.],[2465.47,31.],[2468.47,31.],[2471.47,31.],[2474.47,31.],[2477.48, 31.00],[2480.48, 31.00],[2483.48, 31.00],[2486.49,31.00],[2489.49, 31.00],[2492.49,31.00],[2495.50,31.00],[2498.50,31.00],[2501.50,31.00],[2504.50, 31.00],[2507.51,31.00],[2510.51,31.00],[2513.51,31.00],[2516.52,31.00],[2519.52,31.00],[2522.52,31.00],[2525.53,31.00],[2528.53,31.00],[2531.53,31.00],[2534.53,31.00],[2537.54,31.00],[2540.54,31.00],[2543.54,31.00],[2546.55,31.00],[2549.55,31.00]]
        # floodplain side
        points_fp = [[2450.45, 49.], [2453.45,49.], [2456.46,49.],[2459.46,49.],[2462.46,49.],[2465.47,49.],[2468.47,49.],[2471.47,49.],[2474.47,49.],[2477.48, 49.00],[2480.48, 49.00],[2483.48, 49.00],[2486.49,49.00],[2489.49, 49.00],[2492.49,49.00],[2495.50,49.00],[2498.50,49.00],[2501.50,49.00],[2504.50, 49.00],[2507.51,49.00],[2510.51,49.00],[2513.51,49.00],[2516.52,49.00],[2519.52,49.00],[2522.52,49.00],[2525.53,49.00],[2528.53,49.00],[2531.53,49.00],[2534.53,49.00],[2537.54,49.00],[2540.54,49.00],[2543.54,49.00],[2546.55,49.00],[2549.55,49.00]]
        points=[points_ch,points_fp]
#
        for name, study in self.studies.items():
          if ('vnv_crit4_5') in name:
            res_file,_ = self.get_study_res(name+':T2DRES')
            times = res_file.times
            avg_shape=(len(points),len(times))
            avg=np.empty(avg_shape)
            for ip in range(len(points)):
              # Getting values over time for each point of extraction
              wd = res_file.get_timeseries_on_points('WATER DEPTH', points[ip])
              u = res_file.get_timeseries_on_points('VELOCITY U', points[ip])
              v = res_file.get_timeseries_on_points('VELOCITY V', points[ip])
              z = res_file.get_timeseries_on_points('BOTTOM', points[ip])
              # Computing hydraulic load
              load=z+wd+(u**2+v**2)/(2*9.81)
              for itm in range(len(times)):
                avg[ip][itm] = (load[:, itm].sum())/len(points_ch)
            # Difference between points on channel and floodplain side
            dh=np.empty(len(times))
            dh=abs(np.diff(avg,axis=0))
            dh=np.reshape(dh, len(times))
            # Threshold value for hydraulic load is different between case F1 and F2 (cf. breach data file and doc)
            if(name=='vnv_crit4_5_seq'):
              threshold_hbr2=np.ones(len(times))
              y_lim=[0.,1.5]
            else:
              threshold_hbr2=np.full(len(times),2.)
              y_lim=[0.,2.5]
            dh_y=[dh,threshold_hbr2]
            times_x=[times,times]
            labels=['$\Delta$E simulation','Threshold value']
            vnv_plot1d(times_x,dh_y,labels,
                fig_size=(6, 3),
                ylim=y_lim,
                x_label='t (s)',
                y_label='$\Delta$E (m)',
                fig_name='img/t2d_breach_threshold_evolutions_DeltaH_{}_br2'.format(name))
#
        for name in self.studies.items():
          if ('vnv_crit4_5') in name:
            res_file.close()
