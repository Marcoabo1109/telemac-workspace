
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
                       't2d_erosion.cas')


        # Erosion parallel mode T2D+GAI
        cas = TelemacCas('t2d_erosion.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_erosion_par.cas',
                       cas=cas)


        # Erosion scalar mode T2D+GAI
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_erosion_diff.cas')


        # Erosion parallel mode T2D+GAI
        cas = TelemacCas('t2d_erosion_diff.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)

        self.add_study('vnv_4',
                       'telemac2d',
                       't2d_erosion_diff_par.cas',
                       cas=cas)

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        self.check_epsilons('vnv_1:T2DRES',
                            'f2d_erosion.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_1:T2DRES',
                            'vnv_2:T2DRES',
                            eps=[1.E-6])

        # Comparison with reference file
        self.check_epsilons('vnv_1:GAIRES',
                            'gai_ref_erosion.slf',
                            eps=[1.E-6])

        # Comparison seq/par.
        self.check_epsilons('vnv_1:GAIRES',
                            'vnv_2:GAIRES',
                            eps=[1.E-6])

        # Comparison with reference file
        self.check_epsilons('vnv_3:T2DRES',
                            'f2d_erosion_diff.slf',
                            eps=[1.E-4])

        # Comparison seq/par.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_4:T2DRES',
                            eps=[1.E-3])

        # Comparison with reference file
        self.check_epsilons('vnv_3:GAIRES',
                            'gai_ref_erosion_diff.slf',
                            eps=[1.E-4])

        # Comparison seq/par.
        self.check_epsilons('vnv_3:GAIRES',
                            'vnv_4:GAIRES',
                            eps=[1.E-4])

    def _post(self):
        """
        Post-treatment processes
        """

        from postel.plot1d import plot1d
        import numpy as np
        import matplotlib.pyplot as plt
        from math import exp

        # Selection to display
        line = [np.array([0.,25.]),np.array([1500.,25.])]
        line_num = [50]
        res, _ = self.get_study_res('vnv_1:T2DRES')
        l, _, c = res.get_timeseries_on_polyline('COH SEDIMENT1',line,line_num)

        _, ax = plt.subplots(figsize=(5, 4))

        sol = []
        h = 4.5
        u = 0.2222
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
        fluer = (tau / 0.01 - 1.)
        alpha = 0.01 * fluer * lo
        for x in l[:,0]:
            sol.append(alpha * x / lo)

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
        fig_name = 'img/profile_conc'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        # Selection to display
        line = [np.array([0.,25.]),np.array([1500.,25.])]
        line_num = [50]
        res, _ = self.get_study_res('vnv_3:T2DRES')
        l, _, c = res.get_timeseries_on_polyline('COH SEDIMENT1',line,line_num)

        _, ax = plt.subplots(figsize=(5, 4))

        cpt = 0
        Pe = 1.
        for x in l[:,0]:
            sol[cpt] = sol[cpt] + alpha * (exp(-Pe) - exp(-Pe * (1. - x / 1500.))) / Pe
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
        fig_name = 'img/profile_conc_diff'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

