"""
Validation script for bedload transport in Courlis
"""

import numpy as np
from vvytel.vnv_study import AbstractVnvStudy


class VnvStudy(AbstractVnvStudy):
    """
    Class for validation of bedload transport Courlis in flume
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 2
        self.tags = ['courlis', 'mascaret']

    def _pre(self):
        """
        Defining the studies
        """
        # Transcritical kernel

        # ==== Transport law : Lefort 2014
        # 1) Progradation in flume
        # 1.0 SARAP (dt = 1s, dx = 10m)
        self.add_study('vnv_1_0',
                       'mascaret',
                       'prograd_lefort_sarap.xcas')
        # 1.1 SARAP with decentrement option (dt = 360s, dx = 50m)
        self.add_study('vnv_1_1',
                       'mascaret',
                       'prograd_lefort_sarap_dec.xcas')

    def _check_results(self):
        """
        Post-treatment processes
        """
        # Comparison with reference file
        self.check_epsilons('vnv_1_0:listing_courlis',
                            'ref_prograd_1_0.listingcourlis',
                            eps=[1.E-11],
                            var1='Cote du fond',
                            var2='Cote du fond',
                            masc=True)

        # Comparison with reference file
        self.check_epsilons('vnv_1_1:listing_courlis',
                            'ref_prograd_1_1.listingcourlis',
                            eps=[1.E-12],
                            var1='Cote du fond',
                            var2='Cote du fond',
                            masc=True)


    def _post(self):
        """
        Post-treatment processes
        """


def get_bottom_results(masc_file):
    """
    Returns the initial, final, maximal and minimal bottom levels
    in 'masc_file'

    Parameters
    ----------
    masc_file : class MascaretFile
        Results file

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


def get_cavalcade_results(file):
    """
    Returns the initial, final, maximal and minimal bottom levels
    obtained with Cavalcade and written in 'file'

    Parameters
    ----------
    file : str
        Results file

    Returns
    -------
    ID : Numpy array
        Section names (int)
    x : Numpy array
        Pks for each section
    z_init, z_final, z_max, z_min: Numpy arrays
        Initial, final, maximal and minimal bottom levels
    qs : Numpy array
        Bedload rate at different time steps for each section except the 0

    """
    sol = np.loadtxt(file, skiprows=1)
    ID = sol[:, 0]
    x = sol[:, 1]
    z_init = sol[:, 2]
    z_final = sol[:, 3]
    z_max = sol[:, 4]
    z_min = sol[:, 5]
    qs = sol[:, 5:]
    return x, ID, z_init, z_final, z_max, z_min, qs


def check_errors(masc_file, cavalcade_file):
    """
    Print the errors on bottom elevations and bedload rates between the
    mascaret results and the cavalcade ones

    Parameters
    ----------
    masc_file : class MascaretFile
        Mascaret results
    cavalcade_file : str
        File with Cavalcade results

    Returns
    -------
    None.

    """
    z_init, z_final, z_max, z_min = get_bottom_results(masc_file)

    _, _,\
        z_init_cav, z_final_cav,\
        z_max_cav, z_min_cav,\
        _ = get_cavalcade_results(cavalcade_file)
    error_init = z_init_cav - z_init
    error_final = z_final_cav - z_final
    error_max = z_max_cav - z_max
    error_min = z_min_cav - z_min

    print('Initial bottom level error : {:.2e}'.format(error_init))

    print('Final bottom level error : {:.2e}'.format(error_final))

    print('Maximal bottom level error : {:.2e}'.format(error_max))

    print('Minimal bottom level error : {:.2e}'.format(error_min))


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
    laws = ['Lefort ']

    N = 2 * len(laws)  # progradation + Progradation for each

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
    TS_case : {"progradation", "erosion"}
    TS_name : {'Progradation in a flume', 'progradation in a flume'}

    """
    if i % 2 == 0:
        TS_case = "progradation"
        TS_name = 'Progradation in a flume'
        i_law = i / 2
    else:
        TS_case = "progradation"
        TS_name = 'progradation in a flume'
        i_law = i - 1 / 2
    law = laws[i_law]

    return TS_case, TS_name, law
