"""
python module extracts metadata from NetCDF file and return the metadata as a dictionary or json string.

"""
__author__ = 'Tian Gan'


import json
import netCDF4
import re


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
    nc_dataset.close

    return nc_meta_dict


def get_nc_dataset(nc_file_name):
    """
    (string)-> object

    Return: the netCDF dataset
    """

    nc_data = netCDF4.Dataset(nc_file_name, 'r')
    return nc_data


def get_dublin_core_meta(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF dublin core metadata
    """

    nc_global_meta = extract_nc_global_meta(nc_dataset)
    nc_temporal_meta = extract_nc_temporal_meta(nc_dataset)
    nc_spatial_meta = extract_nc_spatial_meta(nc_dataset)
    dublin_core_meta = dict(nc_global_meta.items() + nc_spatial_meta.items()+nc_temporal_meta.items())

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


def extract_nc_temporal_meta(nc_dataset):
    """
    (object)->dict

    Return netCDF time start and end info
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    if nc_coordinate_variables.has_key('T'):
        nc_time_variable = nc_coordinate_variables['T']
        nc_time_data = nc_time_variable[:].tolist()
        nc_time_calendar = nc_time_variable.calendar if hasattr(nc_time_variable, 'calendar') else 'standard'
        start = str(netCDF4.num2date(nc_time_data[0], units=nc_time_variable.units, calendar=nc_time_calendar))
        end = str(netCDF4.num2date(nc_time_data[-1], units=nc_time_variable.units, calendar=nc_time_calendar))
        nc_temporal_meta = {'time_start': start, 'time_end': end}
    else:
        nc_temporal_meta = {}

    return nc_temporal_meta


def extract_nc_spatial_meta(nc_dataset):
    """
    (object)->dict

    Return netCDF spatial boundary info
    """
    nc_spatial_meta = {}

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    if nc_coordinate_variables.has_key('X') and nc_coordinate_variables.has_key('Y'):
        nc_x_variable = nc_coordinate_variables['X']
        nc_y_variable = nc_coordinate_variables['Y']
        nc_spatial_meta = {
            'x_min': nc_x_variable[:].tolist()[0],
            'x_max': nc_x_variable[:].tolist()[-1],
            'x_units': nc_x_variable.units if hasattr(nc_x_variable, 'units') else '',
            'y_min': nc_y_variable[:].tolist()[0],
            'y_max': nc_y_variable[:].tolist()[-1],
            'y_units': nc_y_variable.units if hasattr(nc_y_variable, 'units') else ''
        }

    if nc_coordinate_variables.has_key('X_bounds') and nc_coordinate_variables.has_key('Y_bounds'):
        nc_x_bound_variable = nc_coordinate_variables['X_bounds'][:].tolist()
        nc_y_bound_variable = nc_coordinate_variables['Y_bounds'][:].tolist()
        nc_spatial_meta['x_min'] = nc_x_bound_variable[0][0]
        nc_spatial_meta['x_max'] = nc_x_bound_variable[-1][-1]
        nc_spatial_meta['y_min'] = nc_y_bound_variable[0][0]
        nc_spatial_meta['y_max'] = nc_y_bound_variable[-1][-1]

    return nc_spatial_meta


def get_type_specific_meta(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF type specific metadata
    """

    nc_data_variables = get_nc_data_variables(nc_dataset)
    type_specific_meta = extract_nc_data_variables_meta(nc_data_variables)

    return type_specific_meta


def get_nc_data_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF variable objects which don't represent coordinate
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_data_variables = {}
    nc_all_variables = nc_dataset.variables
    for var_name, var_obj in nc_all_variables.items():
        if (var_obj not in nc_coordinate_variables.values()) and (len(var_obj.shape) > 1):
            nc_data_variables[var_name] = var_obj

    return nc_data_variables


def get_nc_coordinate_variables(nc_dataset):
    """
    (object)-> dict

    Return: the netCDF variables objects which represent coordinates and variables related to coordinates.
            (lat, lon, time, vertical, lat_bnd, lon_bnd, etc...)
    """

    nc_coordinate_variables = {}
    nc_dimension_variables = get_nc_dimension_variables(nc_dataset)
    for var_name, var_obj in nc_dimension_variables.items():
        coordinate_name = get_coordinate_name(var_obj)
        if coordinate_name:
            nc_coordinate_variables[coordinate_name] = var_obj
        else:
            nc_coordinate_variables[var_name] = var_obj

    nc_all_variables = nc_dataset.variables
    for var_name, var_obj in nc_coordinate_variables.items():
        if hasattr(var_obj, u'bounds'):
            nc_coordinate_variables[var_name + u'_bounds'] = nc_all_variables[var_obj.bounds]

    return nc_coordinate_variables


def get_nc_dimension_variables(nc_dataset):
    """
    (object)-> dict

    Return netCDF 1D dimension variables whose dimension names are identical to their variable names
    """

    nc_all_variables = nc_dataset.variables
    nc_dimension_variables = {}
    for var_name, var_obj in nc_all_variables.items():
        if len(var_obj.shape) == 1 and var_name == var_obj.dimensions[0]:
            nc_dimension_variables[var_name] = var_obj

    return nc_dimension_variables


def get_coordinate_name(nc_variable):
    """
    (object)-> string

    Return the coordinate name that the netCDF variable represents in one of the four names: X, Y, Z, T.
    If not discerned as X, Y, Z, T
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


def extract_nc_data_variables_meta(nc_data_variables):
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
