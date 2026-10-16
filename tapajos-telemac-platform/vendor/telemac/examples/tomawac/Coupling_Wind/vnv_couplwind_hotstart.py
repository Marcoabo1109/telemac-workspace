
"""
Validation script for Next_Comput
"""
from vvytel.vnv_study import AbstractVnvStudy
from execution.telemac_cas import TelemacCas, get_dico
from data_manip.extraction.telemac_file import TelemacFile
from postel.plot_vnv import vnv_plot2d
import matplotlib.pyplot as plt

class VnvStudy(AbstractVnvStudy):
    """
    Class for validation
    """

    def _init(self):
        """
        Defines the general parameter
        """
        self.rank = 2
        self.tags = ['tomawac']

    def _pre(self):
        """
        Defining the studies
        """
        self.add_study('vnv_1',
                       'telemac2d',
                       't2d_makeref.cas')
        self.add_study('vnv_2',
                       'telemac2d',
                       't2d_makeini.cas')
        self.add_study('vnv_3',
                       'telemac2d',
                       't2d_next.cas')

        cas =  TelemacCas('t2d_next.cas', get_dico('telemac2d'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('vnv_3p',
                       'telemac2d',
                       'tom_next_par.cas',
                       cas=cas)
        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison with reference file and calculated directly with the 100 time step.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_1:T2DRES',
                            eps=[3e-7, 8e-8, 4e-8, 4e-8, 1e-10, 1e-10, 1e-10])
        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_3:T2DRES',
                            'vnv_3p:T2DRES',
                            eps=[1e-9])

        # Comparison with reference file and calculated directly with the 100 time step.
        self.check_epsilons('vnv_3:WACRES',
                            'vnv_1:WACRES',
                            eps=[3e-8, 5e-6, 1e-10, 4e-8, 3e-7, 5e-8, 1e-10, 1e-10, 5e-9, 2e-8, 2e-5])
        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_3:WACRES',
                            'vnv_3p:WACRES',
                            eps=[1e-9])

    def _post(self):
        """
        Post-treatment processes
        """
        wind = self.get_study_file('vnv_1:T2DRES')
        reswind = TelemacFile(wind)
        windx = reswind.get_timeseries_on_nodes("WIND ALONG X", [0])
        windy = reswind.get_timeseries_on_nodes("WIND ALONG Y", [0])
        normwind=(windx**2+windy**2)**0.5
        timewind=reswind.times.transpose()

        fileini = self.get_study_file('vnv_2:WACRES')
        resini = TelemacFile(fileini)
        timeini=resini.times.transpose()
        windxini=resini.get_timeseries_on_nodes("WIND ALONG X",[0])
        windyini=resini.get_timeseries_on_nodes("WIND ALONG Y",[0])
        normwindini=(windxini**2+windyini**2)**0.5

        glo = self.get_study_file('vnv_2:WACRBI')
        glores = TelemacFile(glo)
        timeglo = glores.times
        windxglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 2)
        windyglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 3)
        normwindglo=(windxglo**2+windyglo**2)**0.5

        filenext = self.get_study_file('vnv_3:WACRES')
        resnext= TelemacFile(filenext)
        timenext=resnext.times.transpose()
        windxnext=resnext.get_timeseries_on_nodes("WIND ALONG X",[0])
        windynext=resnext.get_timeseries_on_nodes("WIND ALONG Y",[0])
        normwindnext=(windxnext**2+windynext**2)**0.5

        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeini, normwindini[0,:],'.' , label='Wind wac before hot start')
        axe.plot(timenext, normwindnext[0,:],'.' , label='Wind wac after hot start')
        axe.plot(timewind, normwind[0,:],'x', label='Wind ref T2D')
        axe.plot(timeglo[-1], normwindglo[0], 'go', markersize=8, label='Hot start')
        plt.title('Wind (m/s) before and after a hot start')
        axe.legend()
        print('        ~> Plotting img/wind.png')
        plt.savefig('img/wind.png')

        waveheight= resnext.get_timeseries_on_nodes("WAVE HEIGHT HM0",[1053])
        ref = self.get_study_file('vnv_1:WACRES')
        resref=TelemacFile(ref)
        timeref=resref.times.transpose()        
        whref=resref.get_timeseries_on_nodes("WAVE HEIGHT HM0",[1053])
        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeref, whref[0,:],'.' , label='reference of wave height')
        axe.plot(timenext, waveheight[0,:],'.' , label='after a hot start')
        plt.title('Wave height (m) at point 1053')
        axe.legend()
        print('        ~> Plotting img/waveheight.png')
        plt.savefig('img/waveheight.png')
