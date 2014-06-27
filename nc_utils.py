"""
Module provides utility functions to manipulate netCDF dataset.
- classify variable types of coordinate, coordinate bound, grid mapping, scientific data, auxiliary coordinate
- show original metadata of a variable
-

"""
__author__ = 'Tian Gan'


import netCDF4
import re
from collections import OrderedDict


# Functions for General Purpose ##################################
def get_nc_dataset(nc_file_name):
    """
    (string)-> object

    Return: the netCDF dataset
    """

    nc_data = netCDF4.Dataset(nc_file_name, 'r')
    return nc_data


def get_nc_variable_original_meta(nc_dataset, nc_variable_name):
    """
    (object, string)-> OrderedDict

    Return: netCDF variable original metadata information defined in the netCDF file
    """

    nc_variable = nc_dataset.variables[nc_variable_name]

    nc_variable_original_meta = OrderedDict([('dimension', str(nc_variable.dimensions)),
                                             ('shape', str(nc_variable.shape)),
                                             ('data_type', str(nc_variable.dtype))])

    for key, value in nc_variable.__dict__.items():
        nc_variable_original_meta[key] = str(value)

    return nc_variable_original_meta


# Functions for Coordinate Variable#################################
def get_nc_coordinate_variables(nc_dataset):
    """
    (object)-> dict

    Return netCDF coordinate variable
    """

    nc_all_variables = nc_dataset.variables
    nc_coordinate_variables = {}
    for var_name, var_obj in nc_all_variables.items():
        if len(var_obj.shape) == 1 and var_name == var_obj.dimensions[0]:
            nc_coordinate_variables[var_name] = nc_dataset.variables[var_name]

    return nc_coordinate_variables


def get_nc_coordinate_variable_namelist(nc_dataset):
    """
    (object)-> list

    Return netCDF coordinate variable names
    """
    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_variable_namelist = list(nc_coordinate_variables.keys())

    return nc_coordinate_variable_namelist


def get_nc_coordinate_variable_typelist(nc_dataset):
    """
    (object)-> dict

    Return the coordinate name that the netCDF variable represents in one of the four names: X, Y, Z, T.
    If not discerned as X, Y, Z, T, none is returned
    """
    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_variable_typelist = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        nc_coordinate_variable_typelist[get_coordinate_variable_type(var_obj)] = var_name

    return nc_coordinate_variable_typelist


def get_coordinate_variable_type(nc_variable):
    """
    (object)-> string

    Return the coordinate name that the netCDF variable represents in one of the four names: X, Y, Z, T.
    If not discerned as X, Y, Z, T, Unknown is returned
    """

    if hasattr(nc_variable, 'axis'):
        return nc_variable.axis

    if hasattr(nc_variable, 'standard_name'):
        if re.match(nc_variable.standard_name, u'latitude', re.I):
            return u'Y'
        elif re.match(nc_variable.standard_name, u'longitude', re.I):
            return u'X'
        elif re.match(nc_variable.standard_name, u'time', re.I):
            return u'T'

    if hasattr(nc_variable, 'positive'):
        return u'Z'

    return 'Unknown'


# Functions for Coordinate Bound Variable ###########################################################################

def get_nc_coordinate_bounds_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF coordinate bound variable
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_bound_variables = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        if hasattr(var_obj, 'bounds'):
            nc_coordinate_bound_variables[var_obj.bounds] = nc_dataset.variables[var_obj.bounds]

    return nc_coordinate_bound_variables


def get_nc_coordinate_bounds_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF coordinate bound variable names
    """
    nc_coordinate_bound_variables = get_nc_coordinate_bounds_variables(nc_dataset)
    nc_coordinate_bound_variable_namelist = list(nc_coordinate_bound_variables.keys())

    return nc_coordinate_bound_variable_namelist

def get_nc_coordinate_bounds_variable_typelist(nc_dataset):
    """
    (object)-> dict

    Return the coordinate bound name that the netCDF variable represents X_bounds, Y_bounds, Z_bounds, T_bounds.
    If not discerned then Unknown_bounds is returned
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_bounds_variable_typelist = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        coordinate_variable_type = get_coordinate_variable_type(var_obj)
        if hasattr(var_obj, 'bounds'):
            nc_coordinate_bounds_variable_typelist[coordinate_variable_type + '_bounds'] = var_obj.bounds

    return nc_coordinate_bounds_variable_typelist

# Function for Auxiliary Coordinate Variable ########################################################################

def get_nc_auxiliary_coordinate_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF auxiliary coordinate variable names
    """

    nc_all_variables = nc_dataset.variables
    nc_auxiliary_coordinate_variable_namelist = []
    for var_name, var_obj in nc_all_variables.items():
        if hasattr(var_obj, 'coordinates'):
            nc_auxiliary_coordinate_variable_namelist = var_obj.coordinates.split(' ')
            break

    return nc_auxiliary_coordinate_variable_namelist


def get_nc_auxiliary_coordinate_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF auxiliary coordinate variable
    """

    nc_auxiliary_coordinate_variable_namelist = get_nc_auxiliary_coordinate_variable_namelist(nc_dataset)
    nc_auxiliary_coordinate_variables = {}
    for name in nc_auxiliary_coordinate_variable_namelist:
        nc_auxiliary_coordinate_variables[name] = nc_dataset.variables[name]

    return nc_auxiliary_coordinate_variables


# Function for Grid Mapping Variable ###############################################################################
def get_nc_grid_mapping_variables(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF grid mapping variable
    """

    nc_all_variables = nc_dataset.variables
    nc_grid_mapping_variables = {}
    for var_name, var_obj in nc_all_variables.items():
        if hasattr(var_obj, 'grid_mapping_name'):
            nc_grid_mapping_variables[var_name] = var_obj

    return nc_grid_mapping_variables


def get_nc_grid_mapping_variable_namelist(nc_dataset):
    """
    (object)-> list

    Return: the netCDF grid mapping variable names
    """
    nc_grid_mapping_variables = get_nc_grid_mapping_variables(nc_dataset)
    nc_grid_mapping_variables_namelist = list(nc_grid_mapping_variables.keys())

    return nc_grid_mapping_variables_namelist


def get_nc_projection_variable_detail():
    pass


# Function for Data Variable ##################################################################################
def get_nc_data_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF Data variables
    """

    nc_non_data_variables_namelist = get_nc_coordinate_variable_namelist(nc_dataset)\
                              + get_nc_coordinate_bounds_variable_namelist(nc_dataset)\
                              + get_nc_auxiliary_coordinate_variable_namelist(nc_dataset)
    nc_data_variables = {}
    for var_name, var_obj in nc_dataset.variables.items():
        if (var_name not in nc_non_data_variables_namelist) and (len(var_obj.shape) > 1):
            nc_data_variables[var_name] = var_obj

    return nc_data_variables


def get_nc_data_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF Data variables names
    """

    nc_data_variables = get_nc_data_variables(nc_dataset)
    nc_data_variable_namelist = list(nc_data_variables.keys())

    return nc_data_variable_namelist








