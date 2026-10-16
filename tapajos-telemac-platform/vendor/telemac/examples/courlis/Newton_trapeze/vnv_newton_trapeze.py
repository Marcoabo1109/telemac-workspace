
"""
Validation script for Newton_trapeze
"""
from vvytel.vnv_study import AbstractVnvStudy


TESTED_KERNELS = ['sarap', 'rezodt', 'mascaret']


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
        for kernel in TESTED_KERNELS:
            self.add_study(kernel, 'mascaret', kernel+'_courlis.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        for kernel in TESTED_KERNELS:
            self.check_epsilons(kernel+':listing_courlis',
                                kernel+'_ref.listingcourlis',
                                eps=[1.E-4],
                                masc=True)

    def _post(self):
        """
        Post-treatment processes for longitudinal profile
        """
        from os import path
        import numpy as np
        import matplotlib.pyplot as plt
        from data_manip.formats.mascaret_file import MascaretFile

        reach_id = 1  # first reach
        for kernel in TESTED_KERNELS:
            # Post-treatment processes for longitudinal profile
            # from opt file
            masc_file = MascaretFile(
                path.join(self.get_vnv_working_dir(kernel), 'hydro_res.opt'))
            reach = masc_file.reaches[reach_id]
            x = reach.get_section_pk_list()
            var_pos = masc_file.get_position_var('Cote du fond')
            zini = masc_file.get_values_at_reach(0, reach_id, var_pos)
            zfin = masc_file.get_values_at_reach(-1, reach_id, var_pos)

            # plot
            fig, ax1 = plt.subplots(figsize=(8, 6))
            ax1.plot(x, zini, label='Init', color='black')
            ax1.plot(x, zfin, label='Final', color='blue')
            ax1.set_xlabel('X (m)')
            ax1.set_ylim([0, 9.25])
            ax1.set_xticks(np.arange(0, 10, 2))
            ax1.set_ylabel('$Z_{Ref}$ (m)')
            ax1.set_ylim([-0.06, 0.04])
            ax1.set_yticks(np.arange(-0.06, 0.041, 0.02))

            # gather all legends
            fig.legend(loc='upper right', bbox_to_anchor=(0.8, 0.8))

            # Showing figure
            fig_name = 'img/'+kernel+'_plong'
            print(" "*8+'~> Plotting '+fig_name)
            plt.savefig(fig_name)
            plt.close()

            del masc_file

            # Post-treatment processes for tranversal profile
            # from ptravers file
            ptravers_file = MascaretFile(
                path.join(self.get_vnv_working_dir(kernel), 'resu.ptravers'))
            section_vars = [0, 1]  # Y - Zref

            # Extracting section variables
            _, zini = \
                ptravers_file.get_values(0,
                                         get_section_values=True,
                                         section_vars_indexes=section_vars)
            _, zfin = \
                ptravers_file.get_values(-1,
                                         get_section_values=True,
                                         section_vars_indexes=section_vars)

            # plot
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_xlabel('Y (m)')
            ax.set_xlim([-0.05, 0.35])
            ax.set_xticks(np.arange(0, 0.31, 0.1))
            ax.set_ylabel('$Z - Z_{Ref}^{Init}$ (m)')
            ax.set_ylim([-0.02, 0.03])
            ax.set_yticks(np.arange(-0.02, 0.031, 0.01))

            # init profile
            section_id = 0
            ax.plot(zini[reach_id][section_id][0],
                    zini[reach_id][section_id][1],
                    label='Init', color='black', marker='*')
            # x = 1
            section_id = 5
            zmin = np.min(zini[reach_id][section_id][1])
            ax.plot(zfin[reach_id][section_id][0],
                    zfin[reach_id][section_id][1] - zmin,
                    label='X = 1', color='red')
            # x = 2
            section_id = 9
            zmin = np.min(zini[reach_id][section_id][1])
            ax.plot(zfin[reach_id][section_id][0],
                    zfin[reach_id][section_id][1] - zmin,
                    label='X = 2', color='green')
            # x = 4
            section_id = 17
            zmin = np.min(zini[reach_id][section_id][1])
            ax.plot(zfin[reach_id][section_id][0],
                    zfin[reach_id][section_id][1] - zmin,
                    label='X = 4', color='blue')
            # gather all legends
            ax.legend(loc='upper center')

            # Showing figure
            fig_name = 'img/'+kernel+'_ptravers'
            print(" "*8+'~> Plotting '+fig_name)
            plt.savefig(fig_name)
            plt.close()

            del ptravers_file
