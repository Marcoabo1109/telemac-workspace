
"""
Validation script for buoyancy frazil ice model
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from data_manip.extraction.telemac_file import TelemacFile
from data_manip.computation.datetimes import compute_datetimes

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """
    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 3
        self.tags = ['telemac3d', 'khione']

    def _pre(self):
        """
        Defining the studies
        """

        # thermal budget under icy conditions (serial)
        self.add_study('vnv_1', 'telemac3d', 't3d_reservoir_buoyancy.cas')

        # thermal budget under icy conditions (parallel)
        cas = TelemacCas('t3d_reservoir_buoyancy.cas', get_dico('telemac3d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('vnv_2', 'telemac3d', 't3d_reservoir_buoyancy_par.cas', cas=cas)
        del cas

        # thermal budget under icy conditions (serial)
        self.add_study('vnv_3', 'telemac3d', 't3d_reservoir_buoyancy_multi.cas')

        # thermal budget under icy conditions (parallel)
        cas = TelemacCas('t3d_reservoir_buoyancy_multi.cas', get_dico('telemac3d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('vnv_4', 'telemac3d', 't3d_reservoir_buoyancy_multi_par.cas', cas=cas)
        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """
        self.check_epsilons('vnv_1:T3DRES', 'f3d_reservoir_buoyancy.slf', eps=[1.E-6])
        self.check_epsilons('vnv_2:T3DRES', 'f3d_reservoir_buoyancy.slf', eps=[1.E-6])
        self.check_epsilons('vnv_1:T3DRES', 'vnv_2:T3DRES', eps=[1.E-6])
        self.check_epsilons('vnv_1:ICERES', 'fce_reservoir_buoyancy.slf', eps=[1.E-6])
        self.check_epsilons('vnv_2:ICERES', 'fce_reservoir_buoyancy.slf', eps=[1.E-6])
        self.check_epsilons('vnv_1:ICERES', 'vnv_2:ICERES', eps=[1.E-6])

        self.check_epsilons('vnv_3:T3DRES', 'f3d_reservoir_buoyancy_multi.slf', eps=[1.E-6])
        self.check_epsilons('vnv_4:T3DRES', 'f3d_reservoir_buoyancy_multi.slf', eps=[1.E-6])
        self.check_epsilons('vnv_3:T3DRES', 'vnv_4:T3DRES', eps=[1.E-6])
        self.check_epsilons('vnv_3:ICERES', 'fce_reservoir_buoyancy_multi.slf', eps=[1.E-6])
        self.check_epsilons('vnv_4:ICERES', 'fce_reservoir_buoyancy_multi.slf', eps=[1.E-6])
        self.check_epsilons('vnv_3:ICERES', 'vnv_4:ICERES', eps=[1.E-6])

    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plot2d,\
            vnv_plot1d_polylines
        from postel.plot1d import plot1d
        import datetime
        import matplotlib.pyplot as plt

        res = TelemacFile(self.get_study_file('vnv_1:T3DRES'))
        res_multi = TelemacFile(self.get_study_file('vnv_3:T3DRES'))

        # Getting array of time values from file
        times = res.times

        # List of points we want to display
        points = [[0., 0., 0], [0., 0., 0.5], [0., 0., 1.]]

        data1 = res.get_timeseries_on_points('FRAZIL', points)
        fig, ax = plt.subplots(figsize=(10, 5))

        # for each plot adding a history plot with a label node_(law)
        plot1d(ax, times, data1[2, :],
               color='lime',
               x_label='$t$(s)',
               y_label='frazil concentration',
               plot_label='$z$ = 1 m')

        plot1d(ax, times, data1[1, :],
               color='green',
               x_label='$t$ (s)',
               y_label='frazil concentration',
               plot_label='$z$ = 0.5 m')

        plot1d(ax, times, data1[0, :],
               color='olive',
               x_label='$t$ (s)',
               y_label='frazil concentration',
               plot_label='$z$ = 0 m')

        ax.legend()
        fig_name = 'img/frazil'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        for i in range(10):
            # Getting array of time values from file
            times = res_multi.times

            # List of points we want to display
            points = [[0., 0., 0], [0., 0., 0.5], [0., 0., 1.]]

            data1 = res_multi.get_timeseries_on_points('FRAZIL '+str(i+1), points)
            fig, ax = plt.subplots(figsize=(5, 2.5))

            # for each plot adding a history plot with a label node_(law)
            plot1d(ax, times, data1[2, :],
                   color='lime',
                   x_label='$t$(s)',
                   y_label='frazil '+str(i+1)+' concentration',
                   plot_label='$z$ = 1 m')

            plot1d(ax, times, data1[1, :],
                   color='green',
                   x_label='$t$ (s)',
                   y_label='frazil '+str(i+1)+' concentration',
                   plot_label='$z$ = 0.5 m')

            plot1d(ax, times, data1[0, :],
                   color='olive',
                   x_label='$t$ (s)',
                   y_label='frazil '+str(i+1)+' concentration',
                   plot_label='$z$ = 0 m')

            ax.legend()
            fig_name = 'img/frazil'+str(i+1)
            print(" "*8+'~> Plotting '+fig_name)
            plt.savefig(fig_name)
        # Closing files
        res.close()
        res_multi.close()

        plt.close('all')

