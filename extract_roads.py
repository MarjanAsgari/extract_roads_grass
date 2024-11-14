import os
import gc
import time
import uuid
import tempfile
import argparse
import subprocess
from pathlib import Path
from osgeo import gdal, osr
import platform

gdal.DontUseExceptions()
MAPSET="PERMANENT"

def cmd_interface(argv=None):
    
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-h HELP] use -h to get supported arguments.",
        description="Extract roads from a raster mask.",
    )
    parser.add_argument("-i", "--input", help="The path to the input road raster masks")
    parser.add_argument("-o", "--output", help="The path to the output road vector file")
    
    args = parser.parse_args()
    arguments = {
        "input": args.input,
        "output": args.output,
    }
    return arguments

def config_grass():
    
    
    result = subprocess.run(['where', 'grass84.bat'], capture_output=True, text=True, check=True)
    # Output will contain the path to grass84.bat
    grass8bin = result.stdout.strip()
    if grass8bin:
        print(f"Grass start script is added as: {grass8bin}")
    else:
        print("grass84.bat not found.")
    
    """ When working with Grass Session on windows there are two requirements --> 1- Setting up the grass bin 2- giving the grass lib path to the path"""
    # we have to set this path so that Grass_session has acess to libgrass_gis.7.8.dll 
    os.environ['PATH'] = r'C:\OSGeo4W\apps\grass\grass84\lib;' + os.environ['PATH']
    # we have to set this path so that Grass_session has acess to libgrass_gis.7.8.dll 
    return grass8bin


def road_extraction_grass(input_data, output_data):
    
    # Creating the geofile path for storing the results
    road_dataset_path = Path(input_data)
    road_dataset_name = road_dataset_path.stem
    road_geopackage = Path(output_data) / f"{road_dataset_name}.gpkg"

    # Getting the crs code of the layer
    road_dataset = gdal.Open(road_dataset_path)
    
    epsg=""
    if road_dataset is not None:
        # Get the CRS from the dataset
        projection = road_dataset.GetProjection()
        # Parse the projection information to get the EPSG code
        srs = osr.SpatialReference(wkt=projection)
        srs.AutoIdentifyEPSG()
        epsg = srs.GetAuthorityCode(None)   
    if epsg:

        start_time = time.time()
        with tempfile.TemporaryDirectory() as gisdb:
            
            location = str(uuid.uuid4())
            mapset = MAPSET
            
            if platform.system().lower()  == 'windows':
                gisrc = os.path.join(gisdb, location, mapset, ".grassrc")
                os.environ['GISRC'] = gisrc
            grass.create_project(os.path.join(gisdb, location), epsg=epsg)
            gsetup.init(gisdb, location, mapset)

            # Print current GRASS GIS environment
            print("--- GRASS GIS - Current version and environment ---")
            print(f"GRASS Version {grass.version().version}")
            print(grass.gisenv())
            
            output_name = "roads"
            grass.run_command('r.import', input=road_dataset_path, output=output_name, overwrite=True)
            grass.run_command('g.region', flags='p', raster=output_name)
            grass.run_command('r.to.vect', input=output_name, output='roads_v', type='line', flags='s')
            grass.run_command('v.generalize', input='roads_v', output='roads_v_smooth', method='chaiken', threshold=10)
            grass.run_command('v.clean', input='roads_v_smooth', output='roads_v_smooth_c', tool='break,rmdupl,rmsa')
            grass.run_command('v.clean', input='roads_v_smooth_c', output='roads_v_smooth_c_s', tool='snap', threshold=3)
            grass.run_command('v.out.ogr', 
                        input='roads_v_smooth_c_s', 
                        output=str(road_geopackage), 
                        format='GPKG', 
                        layer='roads_1', 
                        flags='c', 
                        overwrite=True)
            total_time = time.time() - start_time
            print(
                f"------------- Road Extraction for {road_dataset_name} Completed in {(total_time // 60):.0f}m {(total_time % 60):.0f}s -------------"
            )
            gc.collect()

    
if __name__ == "__main__":

    
    arguments = cmd_interface()
    if platform.system().lower() == 'windows':
        grass8bin = grass8bin_win = config_grass()
        os.environ['GRASSBIN'] = grass8bin

    # They should be imported here
    from grass_session import Session
    import grass.script as grass
    import grass.script.setup as gsetup
    road_extraction_grass(arguments["input"], arguments["output"])
