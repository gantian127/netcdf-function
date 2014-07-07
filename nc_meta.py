"""
Module extracts metadata from NetCDF file to complete the required HydroShare NetCDF Science Metadata
"""
__author__ = 'Tian Gan'

from nc_utils import *
import json
import netCDF4


def get_nc_meta_json(nc_file_name):
    """
    (string)-> json string

    Return: the netCDF Dublincore and Type specific Metadata
    """

    nc_meta_dict = get_nc_meta_dict(nc_file_name)
    nc_meta_json = json.dumps(nc_meta_dict)
    return nc_meta_json


def get_nc_meta_dict(nc_file_name):
    """
    (string)-> dict

    Return: the netCDF Dublincore and Type specific Metadata
    """

    if isinstance(nc_file_name, netCDF4.Dataset):
        nc_dataset = nc_file_name
    else:
        nc_dataset = get_nc_dataset(nc_file_name)

    dublin_core_meta = get_dublin_core_meta(nc_dataset)
    type_specific_meta = get_type_specific_meta(nc_dataset)
    nc_meta_dict = {'dublin_core_meta': dublin_core_meta, 'type_specific_meta': type_specific_meta}
    nc_dataset.close()

    return nc_meta_dict


def get_dublin_core_meta(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF dublin core metadata
    """

    nc_global_meta = extract_nc_global_meta(nc_dataset)
    nc_coverage_meta = extract_nc_coverage_meta(nc_dataset)
    dublin_core_meta = dict(nc_global_meta.items() + nc_coverage_meta.items())

    return dublin_core_meta


def extract_nc_global_meta(nc_dataset):
    """
    (object)->dict

    Return netCDF global attributes info which correspond to dublincore meta attributes
    """

    nc_global_meta = {}

    dublincore_vs_convention = {
        'creator_name': ['creator_name', 'creator_institution'],
        'creator_email': ['creator_email'],
        'creator_uri': ['creator_uri'],
        'contributor_name': ['contributor_name'],
        'convention': ['Conventions'],
        'title': ['title'],
        'subject': ['keywords'],
        'description': ['summary', 'comment', ],
        'rights': ['license'],
        'references': ['references'],
        'source': ['source']

    }  # key is the dublincore attributes, value is corresponding attributes from ACDD and CF convention

    for dublincore, convention in dublincore_vs_convention.items():
        for option in convention:
            if hasattr(nc_dataset, option):
                nc_global_meta[dublincore] = nc_dataset.__dict__[option]
                break

    return nc_global_meta


def extract_nc_coverage_meta(nc_dataset):
    """
    (object)->dict

    Return netCDF time start and end info
    """

    nc_coverage_meta = {}
    nc_coordinate_variables_detail = get_nc_coordinate_variables_detail(nc_dataset)

    for var_name, var_detail in nc_coordinate_variables_detail.items():
        coor_type = var_detail['coordinate_type']
        coor_info = {
            coor_type + '_start': var_detail['coordinate_start'],
            coor_type + '_end': var_detail['coordinate_end'],
            coor_type + '_units': var_detail['coordinate_units']
        }
        if coor_type == 'T':
            nc_coverage_meta['temporal'] = coor_info
        elif coor_type == 'X':
            nc_coverage_meta['spatial_x'] = coor_info
        elif coor_type == 'Y':
            nc_coverage_meta['spatial_y'] = coor_info
        ## ToDo consider the boundary variable info for spatial meta!

    return nc_coverage_meta


def get_type_specific_meta(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF type specific metadata
    """

    nc_data_variables = get_nc_data_variables(nc_dataset)
    type_specific_meta = extract_nc_data_variables_meta(nc_data_variables)

    return type_specific_meta


def extract_nc_data_variables_meta(nc_data_variables):
    """
    (dict) -> dict

    Return : the netCDF data variable metadata which are required by HS system.
    """
    nc_data_variables_meta = {}
    for var_name, var_obj in nc_data_variables.items():
        nc_data_variables_meta[var_name] = {
            'var_name': var_name,
            'var_units': var_obj.units if hasattr(var_obj, 'units') else '',
            'var_type': str(var_obj.dtype),
            'var_shape': str(zip(var_obj.dimensions, var_obj.shape)),
            'var_descriptive_name': var_obj.long_name if hasattr(var_obj, 'long_name') else '',
            'var_missing_value': str(var_obj.missing_value if hasattr(var_obj, 'missing_value') else '')
        }

    return nc_data_variables_meta



