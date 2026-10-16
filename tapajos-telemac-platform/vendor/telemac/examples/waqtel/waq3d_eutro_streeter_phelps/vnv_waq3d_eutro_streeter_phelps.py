
"""
Validation script for waq3d_eutro_streeter_phelps
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
        self.rank = 4
        self.tags = ['telemac3d', 'waqtel']
        # For vnv_1 and vnv_3
        self.walltime = "3:00:00"

    def _pre(self):
        """
        Defining the studies
        """

        # water quality- dissolved biomas process
        self.add_study('vnv_1',
                       'telemac3d',
                       't3d_waq3d_eutro_streeter_phelps.cas')


        # water quality- dissolved biomas process
        cas = TelemacCas('t3d_waq3d_eutro_streeter_phelps.cas', get_dico('telemac3d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac3d',
                       't3d_waq3d_eutro_streeter_phelps_par.cas',
                       cas=cas)

        del cas

        # water quality- dissolved biomas process
        self.add_study('vnv_3',
                       'telemac3d',
                       't3d_waq3d_eutro_streeter_phelps_cst.cas')


        # water quality- dissolved biomas process
        cas = TelemacCas('t3d_waq3d_eutro_streeter_phelps_cst.cas', get_dico('telemac3d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac3d',
                       't3d_waq3d_eutro_streeter_phelps_cst_par.cas',
                       cas=cas)

        del cas



    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_1:T3DRES',
                            'f3d_waq3d_eutro_streeter_phelps.slf',
                            eps=[1.E-10,1.E-8,1.E-13,1.E-12,1.E-15,1.E-15,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-7,1.E-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_2:T3DRES',
                            'f3d_waq3d_eutro_streeter_phelps.slf',
                            eps=[1.E-10,1.E-8,1.E-12,1.E-12,1.E-15,1.E-15,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-7,1.E-4])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_1:T3DRES',
                            'vnv_2:T3DRES',
                            eps=[1.E-10,1.E-8,1.E-13,1.E-12,1.E-15,1.E-15,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-7,1.E-4])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_3:T3DRES',
                            'f3d_waq3d_eutro_streeter_phelps_cst.slf',
                            eps=[1.E-10,1.E-8,1.E-12,1.E-12,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-13,1.E-6])

        # Comparison with the last time frame of the reference file.
        self.check_epsilons('vnv_4:T3DRES',
                            'f3d_waq3d_eutro_streeter_phelps_cst.slf',
                            eps=[1.E-10,1.E-8,1.E-12,1.E-12,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-7,1.E-5])

        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_3:T3DRES',
                            'vnv_4:T3DRES',
                            eps=[1.E-10,1.E-8,1.E-12,1.E-12,
                                 1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,1.E-15,
                                 1.E-7,1.E-5])


    def _post(self):
        """
        Post-treatment processes
        """

        from postel.plot_vnv import vnv_plot2d
        import matplotlib.pyplot as plt
        from postel.plot1d import plot1d

        # Getting files
        vnv_1_t3dres = self.get_study_file('vnv_1:T3DRES')
        res = TelemacFile(vnv_1_t3dres)

        #Plotting mesh
        vnv_plot2d('',
                   res,
                   plot_mesh=True,
                   fig_size=(15., 3.),
                   fig_name='img/res_mesh')

        # Plotting 3D mesh section (vertical mesh)
        vnv_plot2d('ELEVATION Z',
                   res,
                   poly=[[0., 200.], [30000., 200.]],
                   record=0,
                   plot_mesh=True,
                   x_label='$x$ (m)', y_label='$z$ (m)',
                   fig_size=(10, 3),
                   fig_name='img/res_mesh_section')

        # Plotting final condition for TRACER 1 (at -1)
#        vnv_plot2d('TRACER 1',
#                   res,
#                   poly=[[10, 110], [210, 110]],
#                   record=-1,
#                   filled_contours=True,
#                   x_label='$x$ (m)', y_label='$z$ (m)',
#                   cbar_label='Tracer 1',
#                   fig_size=(20, 5),
#                   fig_name='img/res_ta1')

        #----------------------------------------------------------------------
        # Comparison of tracers (1D slice):

        # Getting array of time values from file 
        times = res.times/3600.

        # List of points we what to display
        points = [[15000., 200., -9.]]

        # Getting tracer values over time for each point of extraction
#        data1 = res.get_timeseries_on_points('PHYTO BIOMASS', points)
#        data2 = res.get_timeseries_on_points('DISSOLVED PO4', points)
#        data3 = res.get_timeseries_on_points('POR NON ASSIMIL', points)
#        data4 = res.get_timeseries_on_points('DISSOLVED NO3', points)
#        data5 = res.get_timeseries_on_points('NOR NON ASSIM', points)
#        data6 = res.get_timeseries_on_points('NH4 LOAD', points)
        data7 = res.get_timeseries_on_points('ORGANIC LOAD', points)
        data8 = res.get_timeseries_on_points('DISSOLVED O2', points)

        #Initialising figure
        fig, ax = plt.subplots(figsize=(10,5))

        # for each plot adding a history plot with a label node_(law)
        plot1d(ax, times, data7[0, :],
               x_label='$t$ (hours)',
               y_label='tracer concentration',
               plot_label='Organic load in mg/l')

        # for each plot adding a history plot with a label node_(law)
        plot1d(ax, times, data8[0, :],
               x_label='$t$ (hours)',
               y_label='tracer concentration',
               plot_label='Dissolved O$_2$ in mg/l')

        # Displaying legend
        ax.legend()

        fig_name = 'img/res_tracers'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)
        plt.close('all')

        res.close()
