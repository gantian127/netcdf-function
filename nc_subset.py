"""
module used to extract data of a netCDF variable based on subset information.

"""

__author__ = 'Tian Gan'

from nc_meta import *
from nc_utils import *
from collections import OrderedDict


def get_nc_data_variable_subset_array(nc_file_name, nc_variable_subset_info):
    """
    (string, dict) -> array

    Return: the subset of the variable data array based on the subset information

    nc_variable_subset_info = {
    'variable_name': 'pr',
    'lon':[0,0],
    'lat':[0,1],
    'time':[0,0],
    }
    """

    nc_dataset = get_nc_dataset(nc_file_name)
    nc_variable = nc_dataset.variables[nc_variable_subset_info['variable_name']]
    nc_variable_data = nc_variable[:]
    nc_variable_dimension_namelist = nc_variable.dimensions
    slice_obj = []
    for dim_name in nc_variable_dimension_namelist:
        slice_start = nc_variable_subset_info[dim_name][0]
        slice_end = nc_variable_subset_info[dim_name][1]
        slice_obj.append(slice(slice_start, slice_end+1, 1))
    nc_variable_data_subset_array = nc_variable_data[tuple(slice_obj)]

    return nc_variable_data_subset_array



