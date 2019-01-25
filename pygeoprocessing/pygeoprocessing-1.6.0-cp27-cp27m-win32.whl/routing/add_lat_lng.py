"""Add lat/lng to geometry."""
import os

import gdal


def add_lat_lng(geom_path, target_table_path):
    """Add lat/lng to geom vector and export to target table CSV."""
    mem_driver = gdal.GetDriverByName('Memory')

    geom_vector = gdal.OpenEx(geom_path, gdal.OF_VECTOR)
    geom_mem = mem_driver.CreateCopy(None, geom_vector)

if __name__ == '__main__':

    geom_path = r"C:\Users\rpsharp\Downloads\ipbes_pollination_summary_hg_2018-10-19_14%3A35_-0700_da484864278d.gpkg"
    target_table_path = os.path.basename(os.path.splitext(
        geom_path)[0]) + '.csv'

    #"C:\Users\rpsharp\Downloads\global_cv_risk_and_aggregate_analysis_md5_f05023fe2d2988113cdd1ef7a0301475.gpkg"
    #"C:\Users\rpsharp\Downloads\ipbes_ndr_summary_oct_24_md5_da95dbdccf6eaec2b4e1b05437d97b39.gpkg"
    add_lat_lng(geom_path, target_table_path)
