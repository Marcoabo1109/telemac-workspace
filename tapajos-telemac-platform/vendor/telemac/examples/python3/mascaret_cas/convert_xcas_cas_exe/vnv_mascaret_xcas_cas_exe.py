"""
Validation script for steering_file
"""
from os import path
from vvytel.vnv_study import AbstractVnvStudy
from execution.mascaret_cas import MascaretCas

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 0
        self.tags = ['mascaret']

    def _pre(self):
        """
        Defining the studies
        """
        from execution.telemac_dico import TelemacDico
        from config import CFGS
        from os import sep, mkdir, getcwd
        import shutil

        xcas_file = path.join(CFGS.get_root(), "examples",
                          "mascaret", "Test23", "mascaret.xcas")
        dico_name = path.join(CFGS.get_root(), "sources",
                                  "mascaret", "mascaret.dico")

        current_folder = getcwd()

        ## Translate test case
        vnv_folder = path.join(current_folder, "vnv_mascaret_xcas_cas_exe")
        if path.exists(vnv_folder):
            shutil.rmtree(vnv_folder)
            mkdir(vnv_folder)
        else:
            mkdir(vnv_folder)

        case = MascaretCas(xcas_file, dico_name, check_files=False)

        en_filename = path.join(vnv_folder,
                    case.cas_filename.split(sep)[-1].split('.')[0] + '_en.cas')
        case.write_case_file(cas_filename=en_filename, lang='en')

        case.copy_cas_files(vnv_folder, verbose=True, copy_cas_file=True)

        self.add_command('vnv_manip_cas',
                         'mascaret.py ' + en_filename)

    def _check_results(self):
        """
        Post-treatment processes
        """


    def _post(self):
        """
        Post-treatment processes
        """
