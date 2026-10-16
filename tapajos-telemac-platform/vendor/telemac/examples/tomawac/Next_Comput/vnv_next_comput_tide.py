
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

#       Construct the tidal file with user_anamar
        self.add_study('vnv_1',
                       'tomawac',
                       'tom_maketide.cas')

#       constructs the reference result
        self.add_study('vnv_2',
                       'tomawac',
                       'tom_makeref_tide.cas')

#       construct the initial solution
        self.add_study('vnv_3',
                       'tomawac',
                       'tom_makeini_tide.cas')

#
        self.add_study('vnv_4',
                       'tomawac',
                       'tom_next_tide.cas')

        cas =  TelemacCas('tom_next_tide.cas', get_dico('tomawac'))
        cas.set('PARALLEL PROCESSORS', 4)
        self.add_study('vnv_4p',
                       'tomawac',
                       'tom_next_tide.cas',
                       cas=cas)
        del cas

    def _check_results(self):
        """
        Post-treatment processes
        """

        # Comparison between tide file and the one constructed with user_anamar.
        self.check_epsilons('vnv_1:WACRES',
                            'tide.slf',
                            eps=[1e-9])
        # Comparison between init file and the one constructed tomawac.
        self.check_epsilons('vnv_3:WACRBI',
                            'fom_ini_tide.glo',
                            eps=[1e-9])
        # Comparison with reference file calculated directly with the 100 time step.
        self.check_epsilons('vnv_4:WACRES',
                            'vnv_2:WACRES',
                            eps=[1e-9])
        # Comparison between sequential and parallel run.
        self.check_epsilons('vnv_4:WACRES',
                            'vnv_4p:WACRES',
                            eps=[1e-9])

    def _post(self):
        """
        Post-treatment processes
        """
        tide = self.get_study_file('vnv_3:WACMAB')
        restide = TelemacFile(tide)
        depth = restide.get_timeseries_on_nodes("WATER DEPTH", [0])
        currx = restide.get_timeseries_on_nodes("VELOCITY U", [0])
        curry = restide.get_timeseries_on_nodes("VELOCITY V", [0])
        normcurr=(currx**2+curry**2)**0.5
        timetide=restide.times.transpose()

        fileini = self.get_study_file('vnv_3:WACRES')
        resini = TelemacFile(fileini)
        timeini=resini.times.transpose()
        depthini=resini.get_timeseries_on_nodes("WATER DEPTH",[0])
        currxini=resini.get_timeseries_on_nodes("VELOCITY U",[0])
        curryini=resini.get_timeseries_on_nodes("VELOCITY V",[0])
        normcurrini=(currxini**2+curryini**2)**0.5

        glo = self.get_study_file('vnv_3:WACRBI')
        glores = TelemacFile(glo)
        timeglo = glores.times
        depthglo = glores.get_data_on_horizontal_plane("DEPTH", -1, 0)
        currxglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 0)
        curryglo = glores.get_data_on_horizontal_plane("CURRENT-WIND", -1, 1)
        normcurrglo=(currxglo**2+curryglo**2)**0.5

        filenext = self.get_study_file('vnv_4:WACRES')
        resnext= TelemacFile(filenext)
        timenext=resnext.times.transpose()
        depthnext=resnext.get_timeseries_on_nodes("WATER DEPTH",[0])
        currxnext=resnext.get_timeseries_on_nodes("VELOCITY U",[0])
        currynext=resnext.get_timeseries_on_nodes("VELOCITY V",[0])
        normcurrnext=(currxnext**2+currynext**2)**0.5

        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeini, depthini[0,:],'.' , label='Current before hot start')
        axe.plot(timenext, depthnext[0,:],'.' , label='Current after hot start')
        axe.plot(timetide, depth[0,:],'x', label='Current read')
        axe.plot(timeglo[-1], depthglo[0],'go', markersize=8, label='Hot start')
        axe.legend()
        print('        ~> Plotting img/waterdepth.png')
        plt.savefig('img/waterdepth.png')
        _, axe = plt.subplots(figsize=(10, 8))
        axe.plot(timeini, normcurrini[0,:],'.' , label='Water depth before hot start')
        axe.plot(timenext, normcurrnext[0,:],'.' , label='Water depth after hot start')
        axe.plot(timetide, normcurr[0,:],'x', label='Water depth read')
        axe.plot(timeglo[-1], normcurrglo[0],'go', markersize=8, label='Hot start')
        axe.legend()
        print('        ~> Plotting img/normcurr.png')
        plt.savefig('img/normcurr.png')
