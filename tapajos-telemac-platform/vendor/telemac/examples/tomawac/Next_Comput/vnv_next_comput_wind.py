
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

#       construct the wind file with user_anaven
        self.add_study('vnv_1',
                       'tomawac',
                       'tom_makewind.cas')
#       construct the reference file
        self.add_study('vnv_2',
                       'tomawac',
                       'tom_makeref_wind.cas')
#       construct the initial solution       
        self.add_study('vnv_3',
                       'tomawac',
                       'tom_makeini_wind.cas')
#       make the computation continuated         
        self.add_study('vnv_4',
                       'tomawac',
                       'tom_next_wind.cas')

        cas =  TelemacCas('tom_next_wind.cas', get_dico('tomawac'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('vnv_4p',
                       'tomawac',
                       'tom_next_wind_par.cas',
                       cas=cas)
        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison between wind file and the one constructed with user_anaven.
        self.check_epsilons('vnv_1:WACRES',
                            'wind.slf',
                            eps=[1e-9])
        
        # Comparison between init file and the one constructed tomawac.
        self.check_epsilons('vnv_3:WACRBI',
                            'glo_ini_wind.slf',
                            eps=[1e-9])
        
        # Comparison with reference file calculated directly with the 100 time step.
        self.check_epsilons('vnv_4:WACRES',
                            'vnv_2:WACRES',
                            eps=[4e-6, 4e-5, 1e-10, 1e-10, 2e-7, 1e-9])
        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_4:WACRES',
                            'vnv_4p:WACRES',
                            eps=[1e-9])

    def _post(self):
        """
        Post-treatment processes
        """
        wind = self.get_study_file('vnv_3:WACVEB')
        reswind = TelemacFile(wind)
        windx = reswind.get_timeseries_on_nodes("WIND ALONG X", [0])
        windy = reswind.get_timeseries_on_nodes("WIND ALONG Y", [0])
        normwind=(windx**2+windy**2)**0.5
        timewind=reswind.times.transpose()

        fileini = self.get_study_file('vnv_3:WACRES')
        resini = TelemacFile(fileini)
        timeini=resini.times.transpose()
        windxini=resini.get_timeseries_on_nodes("WIND ALONG X",[0])
        windyini=resini.get_timeseries_on_nodes("WIND ALONG Y",[0])
        normwindini=(windxini**2+windyini**2)**0.5

        glo = self.get_study_file('vnv_3:WACRBI')
        glores = TelemacFile(glo)
        timeglo = glores.times
        windxglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 2)
        windyglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 3)
        normwindglo=(windxglo**2+windyglo**2)**0.5

        filenext = self.get_study_file('vnv_4:WACRES')
        resnext= TelemacFile(filenext)
        timenext=resnext.times.transpose()
        windxnext=resnext.get_timeseries_on_nodes("WIND ALONG X",[0])
        windynext=resnext.get_timeseries_on_nodes("WIND ALONG Y",[0])
        normwindnext=(windxnext**2+windynext**2)**0.5

        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeini, normwindini[0,:],'.' , label='Wind before hot start')
        axe.plot(timenext, normwindnext[0,:],'.' , label='Wind after hot start')
        axe.plot(timewind, normwind[0,:],'x', label='Wind read')
        axe.plot(timeglo[-1], normwindglo[0], 'go', markersize=8, label='Hot start')
        axe.legend()
        print('        ~> Plotting img/wind.png')
        plt.savefig('img/wind.png')

        waveheight= resnext.get_timeseries_on_nodes("WAVE HEIGHT HM0",[0])
        ref = self.get_study_file('vnv_2:WACRES')
        resref=TelemacFile(ref)
        timeref=resref.times.transpose()        
        whref=resref.get_timeseries_on_nodes("WAVE HEIGHT HM0",[0])
        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeref, whref[0,:],'.' , label='reference of wave height')
        axe.plot(timenext, waveheight[0,:],'.' , label='after a hot start')
        axe.legend()
        print('        ~> Plotting img/waveheight.png')
        plt.savefig('img/waveheight.png')
