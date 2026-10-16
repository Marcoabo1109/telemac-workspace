
"""
Validation script for dambreak
"""
from vvytel.vnv_study import AbstractVnvStudy

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of dambreak
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 2
        self.tags = ['mascaret', 'courlis']
        self.listing = True

    def _pre(self):
        """
        Defining the studies
        """

        # Garonne Canal transcritical kernel
        self.add_study('vnv_1',
                       'mascaret',
                       'mascaret.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with reference file
        self.check_epsilons('vnv_1:listing_courlis',
                            'mascaret0_ref.listingcourlis',
                            eps=[1.E-8],
                            masc=True)


    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot1d import plot1d
        import matplotlib.pyplot as plt

        # Selection to display
        masc_file, _ = self.get_study_res('vnv_1:resu.listingcourlis', 'mascaret')
        varnames = ['Cote du fond']
        reach_id = 1  # first reach

        time_index = [0, -1]  # first frame
        reach = masc_file.reaches[reach_id]

        _, ax = plt.subplots(figsize=(5, 4))

        for varname in varnames:
            for time in time_index:
                var_pos = masc_file.get_position_var(varname)
                values = masc_file.get_values_at_reach(time, reach_id, var_pos)
                plot1d(ax,
                       reach.get_section_pk_list(),
                       values,
                       plot_label='%e s' % masc_file.times[time],
                       x_label='Distance (m)',
                       y_label='Cote (m)')

        # Displaying legend
        ax.legend()

        # Showing figure
        fig_name = 'img/profile'
        print(" "*8+'~> Plotting '+fig_name)
        plt.savefig(fig_name)

        plt.close()
