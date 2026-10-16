"""
Validation script for bedload transport in Courlis
"""

import numpy as np
from vvytel.vnv_study import AbstractVnvStudy


class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of bedload transport in flume with Courlis
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 1
        # here, we are not testing this test-case in Mascaret validation because simulations are during only one
        # time-step and only Courlis' bedload transport formulae results are checked
        self.tags = ['courlis']

    def _pre(self):
        """
        Defining the studies
        """

        # SARAP kernel
        # ==== Transport law 1 : Meyer Peter Muller
        vnv_number = 000
        law = 'MPM'

        # 000) Base case 1% 100m3/s dm=0.05
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 011) Higher slope 2%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')

        # 012) Lower slope 0.5%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 021) Higher inflow 300m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')
        # 022) Lower inflow 20 m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 031) Different diameters dm=0.03m
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number).zfill(3) + '_' + law + '.xcas')

        # ==== Transport law 2 : Lefort 2014
        vnv_number = update_new_law(vnv_number)
        law = 'Lefort'
        # 100) Base case 1% 100m3/s dm=0.05
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 111) Higher slope 2%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        # 112) Lower slope 0.5%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 121) Higher inflow 300m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')
        # 122) Lower inflow 20 m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 131) Different diameters dm=0.03m
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        # ===== Transport law 3 : Recking 2013
        vnv_number = update_new_law(vnv_number)
        law = 'Recking2013'
        # 300) Base case 1% 100m3/s dm=0.05
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 311) Higher slope 2%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        # 312) Lower slope 0.5%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 321) Higher inflow 300m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')
        # 322) Lower inflow 20 m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 331) Different diameters dm=0.03m
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        # ===== Transport law 4 : Recking 2015
        vnv_number = update_new_law(vnv_number)
        law = 'Recking2015'
        # 400) Base case 1% 100m3/s dm=0.05
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 411) Higher slope 2%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        # 412) Lower slope 0.5%
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 421) Higher inflow 300m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')
        # 422) Lower inflow 20 m3/s
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

        vnv_number = update_new_case(vnv_number)
        # 431) Different diameters dm=0.03m
        vnv_number = update_change_parameter(vnv_number)
        self.add_study('vnv_' + str(vnv_number),
                       'mascaret',
                       str(vnv_number) + '_' + law + '.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """
        laws, n = get_studies()
        for i in range(n):
            _, _, num = what_law_what_case(i, laws)
            # Comparison with reference file
            self.check_epsilons('vnv_'+str(num)+':listing_courlis',
                                'ref_'+str(num)+'.listingcourlis',
                                eps=[1e-14],
                                var1='Flux massique de sable',
                                var2='Flux massique de sable',
                                masc=True)


    def _post(self):
        """
        Post-treatment processes
        """
        from postel.plot_vnv import vnv_plotbar

        qs_list = []
        sol_list = []
        diff_list = []
        num_list = []
        laws, N = get_studies()
        for i in range(N):
            _, _, num = what_law_what_case(i, laws)

            # Listing courlis file of study
            masc_file, _ = self.get_study_res(name='vnv_' + str(num) +':results.listingcourlis',
                                              module="mascaret")
            # Check
            qs, sol, diff = check_qs(masc_file, 'solution.txt', num)
            qs_list.append(qs)
            sol_list.append(sol)
            diff_list.append(diff)
            num_list.append(num)

        vnv_plotbar([qs_list, sol_list, diff_list],
                    fig_size=(12, 8),
                    legend_labels=['Computed', 'Solution', 'Relative error'],
                    x_labels=num_list,
                    fig_name="img/flux_error",
                    annotate_format='f',
                    annotate=False)



def get_bottom_results(masc_file):
    """
    Returns the initial, final, maximal and minimal bottom levels
    in 'masc_file'

    Parameters
    ----------
    masc_file : class MascaretFile
       Mascaret file

    Returns
    -------
    z_init, z_final, z_max, z_min: Numpy arrays
        Initial, final, maximal and minimal bottom levels

    """
    varname = 'Cote du fond'
    reach = masc_file.reaches[1]
    n_sect = reach.nsections
    var_pos = masc_file.get_position_var(varname)
    # Initialization
    z_init = np.zeros(n_sect)
    z_final = np.zeros(n_sect)
    z_max = np.zeros(n_sect)
    z_min = np.zeros(n_sect)

    for i_sect in range(n_sect):
        section = reach.sections[i_sect + 1]
        values = masc_file.get_series(1, section.id, [var_pos])
        z_init[i_sect] = values[0]
        z_final[i_sect] = values[-1]
        z_max[i_sect] = max(values)
        z_min[i_sect] = min(values)
    return z_init, z_final, z_max, z_min


def get_solution(file, num):
    """
    Returns the estimated bedload rate corresponding to case 'num'

    Parameters
    ----------
    file : str
        Results file
    num : int
        Study number

    Returns
    -------
    qs : float
        Bedload rate
    """
    sol = np.loadtxt(file, skiprows=1)
    ID = sol[:, 0]
    qs_all = sol[:, 1]
    index = np.where(ID == num)[0][0]
    return qs_all[index]


def check_qs(masc_file, solution_file, num):
    """
    Compare bedload inflow rate between listingcourlis and excel sheet results

    Parameters
    ----------
    masc_file : class MascaretFile
        listingcourlis file
    solution_file : str
        File name with excel results
    num : int
        Study number
    Returns
    -------
    None.

    """
#    epsilon = 1e-4
    qs = get_qs(masc_file)
    sol = get_solution(solution_file, num)
#    print('Courlis : {:.6f} m3/s'.format(qs))
#    print('Reference : {:.6f} m3/s'.format(sol))
    diff = 100 * (qs - sol) / sol
#    print('Relative error : {:.1e} % \n'.format(diff))
#    if abs(diff) > epsilon:
#        raise TelemacException('Excessive error for vnv {} !'.format(num))
    return qs, sol, diff


def get_studies():
    """
    Transport laws and study names of this check

    Returns
    -------
    laws : list of str
        Transport laws
    N : int
        Number of studies
    """
    laws = ['MPM', 'Lefort', 'Recking2013', 'Recking2015']
    N = 6 * len(laws)  # 6 studies per law

    return laws, N


def what_law_what_case(i, laws):
    """
    Return the law and the case corresponding to study number 'i'

    Parameters
    ----------
    i : int
        Study number
    laws : list of str
        Transport laws names

    Returns
    -------
    law : str
        Law name
    case : {'base', 'slope', 'inflow', 'diameter'}
        Case name
    num : int
        Vnv number
    """
    i_mod6 = i % 6
    law = laws[i // 6]
    num = (i // 6) * 100  # 000, 100, 200, 300, ...
    if i_mod6 == 0:
        case = 'base'
    elif i_mod6 in [1, 2]:
        case = 'slope'
        num += 10 + i_mod6
    elif i_mod6 in [3, 4]:
        case = 'inflow'
        num += 20
        num += i_mod6 - 2
    elif i_mod6 == 5:
        case = 'diameter'
        num += 30 + 1
    return law, case, num


def update_new_law(n):
    """
    Return the integer of the law
    """
    return int(round(n / 100, 0) * 100 + 100)


def update_new_case(n):
    """
    Return the integer of the case
    """
    return int(round(n / 10, 0) * 10 + 10)


def update_change_parameter(n):
    """
    Return the number +1
    """
    return int(n + 1)


def get_qs(masc_file):
    """
    Return the bedload rate upstream at last time step

    Parameters
    ----------
    file : Mascaret Class
        Mascaret file

    Returns
    -------
    qs : float
        Upstream bedload rate
    """
    # Import results from mascaret
    reach_id = 1  # first reach
    # reach = masc_file.reaches[reach_id]
    # x_mesh = reach.get_section_pk_list()
    # n_sections = len(x_mesh)
    # times = masc_file.times

    time_index = -1  # Last time step

    varname = 'Flux massique de vase'
    var_pos = masc_file.get_position_var(varname)
    values = masc_file.get_values_at_reach(time_index, reach_id, var_pos)
    del masc_file
    # débit solide amont = profil 1 du flux massique de vase pour l'instant
    return values[0]
