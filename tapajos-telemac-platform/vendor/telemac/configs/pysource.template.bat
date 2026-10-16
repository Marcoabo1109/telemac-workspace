@rem This file is a Windows environment file template
@rem Running it will position all the environment variables required
@rem to compile and run TELEMAC
@rem You only need to replace <your-systel-file>, <your-config> and
@rem <your-external-path> to reflect your own configuration
@rem
@rem Path to TELEMAC root directory
@for %%a in ("%~dp0.") do @set HOMETEL=%%~dpa
@rem Configuration file
@set SYSTELCFG=%HOMETEL%\configs\<your-systel-file>
@rem Name of the configuration to use
@set USETELCFG=<your-config>
@rem Path to this file
@set SOURCEFILE=%~f0
@rem Add TELEMAC Python scripts to PATH
@set PATH=%HOMETEL%\scripts\python3;%PATH%
@rem Add TELEMAC libraries to PATH
@set PATH=%HOMETEL%\builds\%USETELCFG%\lib
@rem Add TELEMAC Python scripts and extension modules to PYTHONPATH
@set PYTHONPATH=%HOMETEL%\scripts\python3;%PYTHONPATH%
@set PYTHONPATH=%HOMETEL%\builds\%USETELCFG%\wrap_api\lib;%PYTHONPATH%
@rem External libraries
@set EXTERNAL=<your-external-path>
@rem HDF5
@set HDF5HOME=%EXTERNAL%\hdf5-1.10.9
@set PATH=%HDF5HOME%\bin;%PATH%
@rem MED
@set MEDHOME=%EXTERNAL%\med-4.1.1
@set PATH=%MEDHOME%\bin;%PATH%
@rem METIS
@set METISHOME=%EXTERNAL%\metis-5.1.0
@set PATH=%METISHOME%\bin;%PATH%
@rem MSPMPI
@set MPIHOME=%EXTERNAL%\msmpi-10.1.2
@set PATH=%MPIHOME%\bin;%PATH%
@rem OPENBLAS, SCALAPACK and MUMPS
@set OPENBLASHOME=%EXTERNAL%\openblas-0.3.21
@set SCALAPACKHOME=%EXTERNAL%\scalapack-2.1.0
@set MUMPSHOME=%EXTERNAL%\mumps-5.2.1
@rem AED2
@set AEDHOME=%EXTERNAL%\libaed2-1.2.0
@rem GOTM
@set GOTMHOME=%EXTERNAL%\gotm-2019-06-14-opentelemac
@set PATH=%GOTMHOME%\bin;%PATH%*