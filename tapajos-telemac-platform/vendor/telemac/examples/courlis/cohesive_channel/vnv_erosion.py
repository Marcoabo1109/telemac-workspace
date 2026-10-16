
"""
Validation script for cohesive erosion
"""
from vvytel.vnv_study import AbstractVnvStudy

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of cohesive erosion
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 2
        self.tags = ['mascaret', 'courlis']

    def _pre(self):
        """
        Defining the studies
        """
        # erosion cohesive fluvial kernel
        self.add_study('vnv_1',
                       'mascaret',
                       'rezodt.xcas')

        # erosion cohesive fluvial kernel with diffusion
        self.add_study('vnv_2',
                       'mascaret',
                       'rezodt_diff.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with reference file
        self.check_epsilons('vnv_1:listing_courlis',
                            'rezodt0_ref.listingcourlis',
                            eps=[1.E-11],
                            masc=True)

        # Comparison with reference file
        self.check_epsilons('vnv_2:listing_courlis',
                            'rezodt_diff_ref.listingcourlis',
                            eps=[1.E-12],
                            masc=True)


    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt
        from postel.plot1d import plot1d
        from math import exp

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_1:test_2.listingcourlis', 'mascaret')
        varnames = ['Concentration en vase']
        reach_id = 1  # first reach

        time_index = -1  # first frame
        reach = masc_file.reaches[reach_id]

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
        for x in reach.get_section_pk_list():
            sol.append(alpha * x / lo)

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, reach_id, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='Simulation',
                   x_label='Distance (m)',
                   y_label='Concentration (g/l)')
            plot1d(ax,
                   reach.get_section_pk_list(),
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
        masc_file, _ = self.get_study_res('vnv_2:test_2.listingcourlis', 'mascaret')
        varnames = ['Concentration en vase']
        reach_id = 1  # first reach

        time_index = -1  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(5, 4))

        cpt = 0
        Pe = 1.
        for x in reach.get_section_pk_list():
            sol[cpt] = sol[cpt] + alpha * (exp(-Pe) - exp(-Pe * (1. - x / 1500.))) / Pe
            cpt += 1

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, reach_id, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='Simulation',
                   x_label='Distance (m)',
                   y_label='Concentration (g/l)')
            plot1d(ax,
                   reach.get_section_pk_list(),
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
