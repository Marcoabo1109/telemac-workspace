
"""
Validation script for VanRijn
"""
from vvytel.vnv_study import AbstractVnvStudy

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of VanRijn
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
        # VanRijn test case
        self.add_study('vnv_1',
                       'mascaret',
                       'VR.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        self.check_epsilons('vnv_1:listing_courlis',
                            'VR_ref.listingcourlis',
                            eps=[1.E-13],
                            masc=True)
    def _post(self):
        """
        Post-treatment processes
        """
        import matplotlib.pyplot as plt

        from postel.plot1d import plot1d
        import numpy as np

        #Open experimental data
        data = np.loadtxt('data/data.txt.csv', delimiter=',')

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_1:resu.listingcourlis', 'mascaret')
        varnames = ['Cote de l eau', 'Cote du fond']
        reach_id = 1  # first reach

        time_index = 0  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(5, 4))

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

        time_index = -1  # last frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(5, 4))

        for varname in varnames:
            var_pos = masc_file.get_position_var(varname)
            values = masc_file.get_values_at_reach(time_index, reach_id, var_pos)
            plot1d(ax,
                   reach.get_section_pk_list(),
                   values,
                   plot_label='%s' % varname,
                   x_label='Distance (m)',
                   y_label='Cote (m)')
            if varname == 'Cote du fond':
                plot1d(ax,
                       data[:, 0],
                       data[:, 1],
                       plot_label='Experience',
                       x_label='Distance (m)',
                       y_label='Cote (m)',
                       marker='+',
                       linestyle='None',
                       color='black')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile_final'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
