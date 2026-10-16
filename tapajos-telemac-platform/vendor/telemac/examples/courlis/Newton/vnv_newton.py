
"""
Validation script for Newton
"""
from vvytel.vnv_study import AbstractVnvStudy

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of Newton
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
        # Newton test case permanent kernel
        self.add_study('vnv_1',
                       'mascaret',
                       'sarap.xcas')

        # Newton test case non-permanent kernel
        self.add_study('vnv_2',
                       'mascaret',
                       'rezodt.xcas')

        # Newton test case supercritical kernel
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
                            eps=[1.E-8],
                          #  var1='Cote du fond',
                          #  var2='Cote du fond',
                            masc=True)
        # Comparison with reference file
        self.check_epsilons('vnv_2:listing_courlis',
                            'rezodt_ref.listingcourlis',
                          #  var1='Cote du fond',
                          #  var2='Cote du fond',
                            eps=[1.E-8],
                            masc=True)
        # Comparison with reference file
        self.check_epsilons('vnv_3:listing_courlis',
                            'mascaret_ref.listingcourlis',
                            eps=[1.E-8],
                          #  var1='Cote du fond',
                          #  var2='Cote du fond',
                            masc=True)
    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt
        import numpy as np

        from postel.plot1d import plot1d

        #Open experimental data
        data = np.loadtxt('data/newton_run1.txt')

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_1:hydro_perm_res.opt', 'mascaret')
        varnames = ['Cote de l eau', 'Cote du fond']
        reach_id = 1  # first reach

        time_index = 0  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, reach_id, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_init'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()

        varnames = ['Cote du fond']

        time_index = [0, 1, 7, -1]  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            cpt = 0
            for i in time_index:
                var_pos = masc_file.get_position_var(varname)
                values = masc_file.get_values_at_reach(i, reach_id, var_pos)
                time = [0, 1, 4, 24]
                plot1d(ax,
                       reach.get_section_pk_list(),
                       values,
                       plot_label='%i h' % time[cpt],
                       x_label='Distance (m)',
                       y_label='Cote (m)')
                cpt += 1
            plot1d(ax,
                   data[:, 0],
                   data[:, 1],
                   plot_label='1 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='+',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 2],
                   plot_label='4 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='*',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 3],
                   plot_label='24 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='o',
                   linestyle='None',
                   color='black')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_T_sarap'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
        del masc_file

        masc_file, _ = self.get_study_res('vnv_2:hydro_fluvial_res.opt', 'mascaret')
        time_index = [0, 5, 23, -1]  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            cpt = 0
            for i in time_index:
                var_pos = masc_file.get_position_var(varname)
                values = masc_file.get_values_at_reach(i, reach_id, var_pos)
                time = [0, 1, 4, 24]
                plot1d(ax,
                       reach.get_section_pk_list(),
                       values,
                       plot_label='%i h' % time[cpt],
                       x_label='Distance (m)',
                       y_label='Cote (m)')
                cpt += 1
            plot1d(ax,
                   data[:, 0],
                   data[:, 1],
                   plot_label='1 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='+',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 2],
                   plot_label='4 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='*',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 3],
                   plot_label='24 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='o',
                   linestyle='None',
                   color='black')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_T_rezodt'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
        del masc_file

        masc_file, _ = self.get_study_res('vnv_3:hydro_torrent_res.opt', 'mascaret')
        time_index = [0, 3, 15, -1]  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(8, 6))

        for varname in varnames:
            cpt = 0
            for i in time_index:
                var_pos = masc_file.get_position_var(varname)
                values = masc_file.get_values_at_reach(i, reach_id, var_pos)
                time = [0, 1, 4, 24]
                plot1d(ax,
                       reach.get_section_pk_list(),
                       values,
                       plot_label='%i h' % time[cpt],
                       x_label='Distance (m)',
                       y_label='Cote (m)')
                cpt += 1
            plot1d(ax,
                   data[:, 0],
                   data[:, 1],
                   plot_label='1 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='+',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 2],
                   plot_label='4 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='*',
                   linestyle='None',
                   color='black')
            plot1d(ax,
                   data[:, 0],
                   data[:, 3],
                   plot_label='24 h exp',
                   x_label='Distance (m)',
                   y_label='Cote (m)',
                   marker='o',
                   linestyle='None',
                   color='black')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_T_mascaret'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
        del masc_file
