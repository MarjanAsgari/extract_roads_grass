# Extract Roads using GRASS GIS

## Installation

Install GRASS GIS using OSGeo4W installer. You can use [https://download.osgeo.org/osgeo4w/osgeo4w-setup-x86_64-v1.exe](https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe)

In the OSGeo4W installer pop-up, you’ll be given a choice to choose the installation mode. Choose the "Express Desktop Install" option, and check 1- GRASS and 2-GDAL and continue.

Note: We do not need any conda or pip env.

## Execution 

When the installation is finished, search for "OSGEO4W Shell" on your computer. Now the python script should be run in this shell to have access to both gdal and grass.

```bash
python extract_roads.py -i <input> -o <output>
```
- `-i`, `--input_csv`: The path to csv file that has one column in which we have all the skeletons that we want to run the extract tool on.
- `-o`, `--work_dir`: Working Directory
