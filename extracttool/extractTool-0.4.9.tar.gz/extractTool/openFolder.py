import click    # used to print something
import os            # used to get the location of the testdata   # used to navigate through the folder
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo # used for the specific functions to extract the spatial and temporal information

"""
Function for extracting the spatial extent or temporal extent from a directory of files

:param filepath: path to the directory of the files
:param detail: specifies the level of detail of the geospatial extent (bbox or convex hull)
:param time: boolean variable, if it is true the user gets the temporal extent instead of the spatial extent
:returns: spatial extent as a bbox in the format [minlon, minlat, maxlon, maxlat]
"""
def openFolder(filepath, detail , time):
    # arrays for the spatial and temporal extent
    folder_bbox_array=[]
    folder_conv_hull_array=[]
    folder_time_array=[]
    
    folderpath= filepath
    docs=os.listdir(folderpath) 
    # docs now contains the files of the folder 
    # tries to extract the bbox of each file 
    for x in docs:  
        doc_path= folderpath +"/"+ x
        try:
            result_folder=getShapefileInfo.getShapefilebbx(doc_path, detail , time)
        except Exception as e:
            try:
                result_folder=getGeoJsonInfo.getGeoJsonbbx(doc_path, detail , time)
            except Exception as e:
                try:
                    click.echo(e)
                    result_folder=getNetCDFInfo.getNetCDFbbx(doc_path, detail , time)
                except Exception as e:
                    try:
                        result_folder=getCSVInfo.getCSVbbx(doc_path, detail , time)
                    except TypeError as e:
                        try:
                            result_folder=getGeoTiffInfo.getGeoTiffbbx(doc_path, detail , time)
                        except Exception as e:
                            try:
                                result_folder=getGeoPackageInfo.getGeopackagebbx(doc_path, detail , time)
                                print("after geopackage")
                            except Exception as e:
                                try:
                                    result_folder=getIsoInfo.getIsobbx(doc_path, detail , time)
                                except Exception as e:
                                    try:
                                        result_folder=openFolder(doc_path, detail , time)
                                    except Exception as e:
                                        click.echo ("invalid file format in folder!")
                                        result_folder=None                               
        if (result_folder[0]!=[None]):
            folder_bbox_array=folder_bbox_array+[result_folder[0]]
        if (result_folder[1]!= [None]):
            folder_conv_hull_array=folder_conv_hull_array+[result_folder[1]]
        if (result_folder[2]!=[None]):
            folder_time_array=folder_time_array+[result_folder[2]]
    
    ret_value_folder=[] 
    # compute the bounding box of the entire folder                           
    if detail=='bbox':
        bboxes=folder_bbox_array
        min_lon_list=[min_lon for min_lon, min_lat, max_lon, max_lat in bboxes]
        for x in min_lon_list:
            try:
                if x<min_lon_all:
                    min_lon_all=x
            except NameError:
                min_lon_all = x

        min_lat_list=[min_lat for min_lon, min_lat, max_lon, max_lat in bboxes]
        for x in min_lat_list:
            try:
                if x<min_lat_all:
                    min_lat_all=x
            except NameError:
                min_lat_all = x

        max_lon_list=[max_lon for min_lon, min_lat, max_lon, max_lat in bboxes]
        for x in max_lon_list:
            try:
                if x>max_lon_all:
                    max_lon_all=x
            except NameError:
                max_lon_all=x

        max_lat_list=[max_lat for min_lon, min_lat, max_lon, max_lat in bboxes]
        for x in max_lat_list:
            try:
                if x>max_lat_all:
                    max_lat_all=x
            except NameError:
                max_lat_all=x

        # bounding box of the entire folder
        folderbbox=[min_lon_all, min_lat_all, max_lon_all, max_lat_all]
        ret_value_folder.append(folderbbox)
    else:
        ret_value_folder.append([None])

    if detail=='convexHull':
        click.echo("There is no convex hull for directories.")
        ret_value_folder.append([None])
    else:
        ret_value_folder.append([None])

    # compute the time extend of the entire folder
    if (time):
        times=folder_time_array
        start_dates=[]
        end_dates=[]
        for z in times:
            start_dates.append(z[0])
            end_dates.append(z[1])
        min_date=min(start_dates)
        max_date=max(end_dates)
        folder_timeextend=[min_date, max_date]

        if (times):
            ret_value_folder.append(folder_timeextend)
        else:
            ret_value_folder.append([None])
    else:
        ret_value_folder.append([None])
    return ret_value_folder

if __name__ == '__main__':
    openFolder()