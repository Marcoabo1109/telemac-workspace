
"""
Validation script for Equilibrium channel
"""
from vvytel.vnv_study import AbstractVnvStudy

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of Equilibrium channel
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 1
        self.tags = ['mascaret', 'courlis']

    def _pre(self):
        """
        Defining the studies
        """
        # equilibrium test case permanent kernel
        self.add_study('vnv_1',
                       'mascaret',
                       'sarap.xcas')

        # equilibrium test case non-permanent kernel
        self.add_study('vnv_2',
                       'mascaret',
                       'rezodt.xcas')

        # equilibrium test case non-permanent kernel
        self.add_study('vnv_3',
                       'mascaret',
                       'mascaret.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        self.check_epsilons('vnv_1:listing_courlis',
                            'sarap_ref.listingcourlis',
                            eps=[1.E-9],
                            masc=True)

        # Comparison with reference file
        self.check_epsilons('vnv_2:listing_courlis',
                            'rezodt_ref.listingcourlis',
                            eps=[1.E-9],
                            masc=True)

        # Comparison with reference file
        self.check_epsilons('vnv_3:listing_courlis',
                            'mascaret_ref.listingcourlis',
                            eps=[1.E-10],
                            masc=True)

    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt
        from postel.plot1d import plot1d

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_1:hydro_perm_res.opt', 'mascaret')
        varnames = ['Cote de l eau', 'Cote du fond']

        time_index = 0  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_init_sarap'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        time_index = -1  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_final_sarap'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        masc_file, _ = self.get_study_res('vnv_1:resu.listingcourlis', 'mascaret')
        varnames = ['Contrainte effective moyenne']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Tau (Pa)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_tau_sarap'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        varnames = ['Flux massique de sable']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Qs (m3/s)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_flux_sarap'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_2:hyrdro_res.opt', 'mascaret')
        varnames = ['Cote de l eau', 'Cote du fond']

        time_index = 0  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_init_rezo'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        time_index = -1  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_final_rezo'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        masc_file, _ = self.get_study_res('vnv_2:resu.listingcourlis', 'mascaret')
        varnames = ['Contrainte effective moyenne']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Tau (Pa)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_tau_rezo'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        varnames = ['Flux massique de sable']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Qs (m3/s)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_flux_rezo'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_3:hydro_torrent_res.opt', 'mascaret')
        varnames = ['Cote de l eau', 'Cote du fond']

        time_index = 0  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_init_masc'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        time_index = -1  # first frame
        reach = masc_file.reaches[1]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_final_masc'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        masc_file, _ = self.get_study_res('vnv_3:resu.listingcourlis', 'mascaret')
        varnames = ['Contrainte effective moyenne']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Tau (Pa)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_tau_masc'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        varnames = ['Flux massique de sable']
        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, 1, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Qs (m3/s)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_flux_masc'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
