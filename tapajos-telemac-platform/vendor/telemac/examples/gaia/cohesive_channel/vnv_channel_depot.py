
"""
Validation script for cohesive_channel
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
        self.rank = 4
        self.tags = ['telemac2d', 'gaia']
        self.listing = True

    def _pre(self):
        """
        Defining the studies
        """

        # Erosion scalar mode T2D+GAI
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_depot.cas')


        # Erosion parallel mode T2D+GAI
        cas = TelemacCas('t2d_depot.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_depot_par.cas',
                       cas=cas)


        # Erosion scalar mode T2D+GAI
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_depot_diff.cas')


        # Erosion parallel mode T2D+GAI
        cas = TelemacCas('t2d_depot_diff.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_erosion_depot_par.cas',
                       cas=cas)

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_depot.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1.E-6])

        # Comparison with reference file
        self.check_epsilons('vnv_1:GAIRES',
                            'gai_ref_depot.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_2:GAIRES',
                            eps=[1.E-6])

        # Comparison with reference file
        self.check_epsilons('vnv_3:T2DRES',
                            'f2d_depot_diff.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_4:T2DRES',
                            eps=[1.E-5])

        # Comparison with reference file
        self.check_epsilons('vnv_3:GAIRES',
                            'gai_ref_depot_diff.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_3:GAIRES',
                            'vnv_4:GAIRES',
                            eps=[1.E-5])

    def _post(self):
        """
        Post-treatment processes
        """

        from postel.plot1d import plot1d
        import numpy as np
        from postel.plot_vnv import vnv_plot2d
        import matplotlib.pyplot as plt
        from math import exp,sqrt

        # Selection to display
        line = [np.array([0.,25.]),np.array([1500.,25.])]
        line_num = [50]
        res, _ = self.get_study_res('vnv_1:T2DRES')
        l, _, c = res.get_timeseries_on_polyline('COH SEDIMENT1',line,line_num)

        time_index = -1  # first frame

        _, ax = plt.subplots(figsize=(5, 4))

        sol = []
        h = 4.5
        u = 10. / (50. * h)
#        s = 225.
#        la = 50.
        lo = 1500.
        g = 9.81
        rho = 1000.
        kp = 85.
        Rh = h
#        Rh = s / ( 2 * h + la)
        tau = rho * g * u * u
        tau = tau / (kp * kp * Rh ** (1. / 3.))
        fludpt = 1. - tau / 0.1
        alpha = 1.5e-4 * fludpt * lo / (h * u)
        for x in l[:,0]:
            sol.append(exp(-alpha * x / lo))

        plot1d(ax,
                l[:,0],
                c[:,-1],
                plot_label='Simulation',
                x_label='Distance (m)',
                y_label='Concentration (g/l)')
        plot1d(ax,
                l[:,0],
                sol,
                plot_label='Analytical solution',
                x_label='Distance (m)',
                y_label='Concentration (g/l)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_conc_depot'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        # Selection to display
        line = [np.array([0.,25.]),np.array([1500.,25.])]
        line_num = [50]
        res, _ = self.get_study_res('vnv_3:T2DRES')
        l, _, c = res.get_timeseries_on_polyline('COH SEDIMENT1',line,line_num)

        time_index = -1  # first frame

        _, ax = plt.subplots(figsize=(5, 4))

        cpt = 0
        Pe = 1.
        w1 = (1. + sqrt(1. + 4. * alpha / Pe)) / (2. / Pe)
        w2 = (1. - sqrt(1. + 4. * alpha / Pe)) / (2. / Pe)
        for x in l[:,0]:
            sol[cpt] = (w2 * exp(w2) * exp(w1*x/lo) - w1 * exp(w1) * exp(w2*x/lo)) \
                       / (w2 * exp(w2) - w1 * exp(w1))
            cpt += 1

        plot1d(ax,
                l[:,0],
                c[:,-1],
                plot_label='Simulation',
                x_label='Distance (m)',
                y_label='Concentration (g/l)')
        plot1d(ax,
                l[:,0],
                sol,
                plot_label='Analytical solution',
                x_label='Distance (m)',
                y_label='Concentration (g/l)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_conc_depot_diff'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

