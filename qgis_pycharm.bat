SET OSGEO4W_ROOT=C:\OSGeo4W64
SET QGISNAME=qgis
SET GRASSNAME=grass\grass-7.2.1
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
SET QGIS_PREFIX_PATH=%QGIS%
SET GRASS=%OSGEO4W_ROOT%\apps\%GRASSNAME%
SET PYCHARM="C:\Users\visitor\AppData\Roaming\JetBrains\PyCharm 2017.2.1\bin\pycharm64.exe"

CALL "%OSGEO4W_ROOT%"\bin\o4w_env.bat
call "%GRASS%"\etc\env.bat
path %PATH%;%QGIS%\bin
path %PATH%;%GRASS%\lib

set PYTHONPATH=%QGIS%\python;%PYTHONPATH%
set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages;%PYTHONPATH%

start "PyCharm aware of QGIS" /B %PYCHARM% %*