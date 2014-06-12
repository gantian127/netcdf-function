__author__ = 'Tian Gan'

"""
nc_meta python module extracts metadata from NetCDF file and return the metadata as dictionary or json string.

"""
import json
import netCDF4

def get_nc_meta_dict(nc_file_name):
    nc_data = get_nc_data(nc_file_name)
    dublin_core_meta = get_dublin_core_meta(nc_data)
    type_specific_meta = get_type_specific_meta(nc_data)
    nc_meta_dict = get_nc_meta_dict(dublin_core_meta, type_specific_meta)
    return nc_meta_dict


def get_nc_data(nc_file_name):
    nc_data = netCDF4.Dataset(nc_file_name, 'r')
    return nc_data


def get_dublin_core_meta(nc_data):
    pass


def get_type_specific_meta(nc_data):
    pass


def get_nc_meta_dict(dublin_core_meta, type_specific_meta):
    pass



def get_nc_meta_json(nc_file_name):
    nc_meta_dict = get_nc_meta_dict(nc_file_name)
    nc_meta_json = json.dump(nc_meta_dict)
    return nc_meta_json
