"""
Validation script for steering_file
"""
from os import path
from glob import glob
from vvytel.vnv_study import AbstractVnvStudy
from execution.mascaret_cas import MascaretCas

from utils.exceptions import TelemacException

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 0
        self.tags = ['python3']

    def _pre(self):
        """
        Defining the studies
        """
        from execution.telemac_dico import TelemacDico
        from config import CFGS
        from os import getcwd, sep, mkdir
        import shutil

        xcas_files = glob(path.join(CFGS.get_root(), "examples",
                          "mascaret", "*", "*.xcas"))
        dico_name = path.join(CFGS.get_root(), "sources",
                                  "mascaret", "mascaret.dico")
        current_folder = getcwd()

        ## Translate test case
        for xcas_file in xcas_files:
            vnv_folder = path.join(current_folder, "vnv_mascaret_xcas_cas")
            if path.exists(vnv_folder):
                shutil.rmtree(vnv_folder)
                mkdir(vnv_folder)
            else:
                mkdir(vnv_folder)

            case = MascaretCas(xcas_file, dico_name, check_files=False)

            fr_filename = path.join(vnv_folder,
                    case.cas_filename.split(sep)[-1].split('.')[0] + '_fr.cas')
            case.write_case_file(cas_filename=fr_filename, lang='fr')

            en_filename = path.join(vnv_folder,
                    case.cas_filename.split(sep)[-1].split('.')[0] + '_en.cas')
            case.write_case_file(cas_filename=en_filename, lang='en')

    def _check_results(self):
        """
        Post-treatment processes
        """


    def _post(self):
        """
        Post-treatment processes
        """
