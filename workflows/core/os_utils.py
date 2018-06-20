import os
import re
import itertools
import operator
import pandas as pd
import datefinder
from datetime import datetime
from fuzzywuzzy import fuzz
from collections import Counter

from django.conf import settings as cp


##########################
#### File - related ####
##########################

def get_file_extension(file_path, keep_dot=True):
    extension = os.path.splitext(file_path)[1].lower()
    if not keep_dot:
        extension = extension.replace('.', '')
    return extension


def get_file_properties(
    folder,
    result_format='file_property_list',
    startswith=None,
    extension_list=None,
):
    r"""
    Function to put all files (file name, rel path, abs path and extensions)
    of main folder and sub folders into list of dict
    """

    file_property_list = list()
    file_property_dict = dict()
    abs_path_list = list()
    abs_path_dict = dict()

    if os.path.isdir(folder):
        os.chdir(folder)

        for root, dirs, files in os.walk('.'):
            for name in files:

                # Handle specific selections
                if startswith:
                    if not os.path.splitext(name)[0].lower().startswith(startswith.lower()):
                        continue

                if extension_list:
                    if get_file_extension(name, keep_dot=False) not in extension_list:
                        continue

                # Basic metadata
                temp_filename = os.path.splitext(name)[0]
                temp_abs_path = os.path.join(folder, root[2:], name)
                temp_dict = {
                    'name': temp_filename,
                    'rel_path': os.path.join(root, name),
                    'abs_path': temp_abs_path,
                    'extension': get_file_extension(name, keep_dot=False),
                    'size': get_file_size(temp_abs_path),
                    'last_modified_dt': get_modified_date(temp_abs_path),
                    'creation_dt': get_creation_date(temp_abs_path),
                }

                file_property_list.append(temp_dict)
                file_property_dict[temp_filename] = temp_dict
                abs_path_list.append(temp_abs_path)
                abs_path_dict[temp_filename] = temp_abs_path

    if result_format == 'file_property_list':
        return file_property_list
    elif result_format == 'file_property_dict':
        return file_property_dict
    elif result_format == 'abs_path_list':
        return abs_path_list
    elif result_format == 'abs_path_dict':
        return abs_path_dict
    else:
        return None


def rank_field_by_name(word_to_match, target_list):
    output_dict = dict()
    for base_word in target_list:
        output_dict[base_word] = fuzz.ratio(base_word.lower(), word_to_match.lower())

    return output_dict
    # sorted_matching_dict = sorted(matching_dict.items(), key=operator.itemgetter(1), reverse=True)
    # return sorted_matching_dict


def rank_field_by_dtype(dtype_to_match, new_metadata, success_points=0):
    output_dict = dict()
    for k, v in new_metadata.items():
        if v['dtype'] == dtype_to_match:
            output_dict[k] = success_points
        else:
            output_dict[k] = 0

    return output_dict


def rank_field_by_position(position_to_match, new_metadata):
    output_dict = dict()
    for k, v in new_metadata.items():
        if abs(v['position'] - position_to_match) == 0:
            output_dict[k] = 100
        elif abs(v['position'] - position_to_match) == 1:
            output_dict[k] = 60
        elif abs(v['position'] - position_to_match) == 2:
            output_dict[k] = 40
        elif abs(v['position'] - position_to_match) == 2:
            output_dict[k] = 20
        else:
            output_dict[k] = 0

    return output_dict


def rank_field_by_distinct_values(distinct_values_to_match, new_metadata):
    output_dict = dict()
    for k, v in new_metadata.items():
        output_dict[k] = int(len(list(set(v['distinct_values']) & set(distinct_values_to_match)))/len(v['distinct_values']) * 100)
    return output_dict


def find_delimiter(inputfile):
    r"""
    Read a flat file and returns the delimiter having the greatest number of occurences
    """

    delimiter_list = [',', ':', ';', '|', '\t', '^', '#', '+', '%', '~', '*', '-', '_', '!', '=', '&', '$']
    delimiter = Counter(
        [l for l in max_occurence_char_in_list(
            [l for l in read_file(inputfile)], delimiter_list)]
    ).most_common(1)[0][0]
    if delimiter:
        return delimiter[0]
    else:
        return None


#######################################
#### String manipulation - related ####
#######################################

def rewrite_with_technical_convention(string):
    r"""
    Remove any special characters, digits or spaces and replace by underscores
    Return lowercase string
    """
    tmp = re.sub('[^a-zA-Z0-9_ ]', '', str(string))
    tmp = re.sub(' +', '_', tmp)
    tmp = tmp.replace('-', '_')
    return tmp.lower().strip('_')


def rewrite_with_functional_convention(string, field_name = None, field_list_to_rewrite = None):
    r"""
    Returns the input string with Capital letters and spaces instead of underscores
    """
    if string:
        if field_list_to_rewrite is None or field_name in field_list_to_rewrite:
            if is_float(string) or is_integer(string):
                return locale.format("%d", string, grouping=True)
            elif is_integer(string):
                return string
            else:
                return string.replace('_', ' ').title()

    return string


def is_integer(string):
    r"""
    Returns True if the string parameter can be converted into an integer. False otherwise
    """
    if isinstance(string, int) or (not pd.isnull(string) and re.match(cp.FORMAT_INT, str(string))):
        return True
    else:
        return False


def is_float(string):
    r"""
    Returns True if the string parameter can be converted into a float. False otherwise
    """
    if isinstance(string, float) or (not pd.isnull(string) and re.match(cp.FORMAT_FLOAT, str(string))):
        return True
    else:
        return False


def get_list_value_if_index_exists(l, i, default=-1):
    r"""
    Return list value if the index exists
    """
    try:
        return l[i]
    except IndexError:
        return default


def normalize_numeric_format(string):
    r"""
    Remove the special characters in a numeric string
    """
    if not pd.isnull(string):
        return str(string).replace(',', '').strip('%')


def convert_string_to_int(string):
    r"""
    Convert the input string to integer format if possible
    Otherwise return the input string parameter
    """
    # Check if string can be converted to integer
    if is_integer(string):
        return int(normalize_numeric_format(string))
    else:
        return string


def convert_string_to_float(string):
    r"""
    Convert the input string to float format if possible
    Otherwise return the input string parameter
    """
    # Check if string can be converted to float
    if is_float(string):
        return float(normalize_numeric_format(string))
    else:
        return string


def is_datetime(string):
    r"""
    Returns True if the string parameter can be converted into a datetime. False otherwise
    """
    pattern = re.compile(r"""([^0-9/\-.:]+)""")
    if not pd.isnull(string) and [l for l in datefinder.find_dates(str(string))] and not(re.search(pattern, str(string))):
        return True
    else:
        return False


def add_month(mydatetime):
    r"""
    Adds one month to the datetime argument mydatetime.
    """
    try:
        then = (mydatetime + relativedelta(months=1)).replace(day=mydatetime.day)
    except ValueError:
        then = (mydatetime + relativedelta(months=2)).replace(day=1)
    return then


def normalize_date_format(string):
    r"""
    Appends 01 when the string is a month date format
    Removes special characters in a date string.
    """
    if not pd.isnull(string):
        format_regex = re.compile(cp.FORMAT_DATES['MONTH_DATE'])
        if re.search(format_regex, string):
            string = '01' + string
        format_regex = re.compile(cp.FORMAT_DATES['MONTH_DATE_ISO'])
        if re.search(format_regex, string):
            string = string + '01'
        return re.sub(r"""[./-]""", '', string)


def convert_string_to_datetime(string):
    r"""
    Converts the input string to datetime format if possible
    Otherwise returns the input string parameter
    """
    # Check if string can be converted to datetime
    if is_datetime(string):
        return [l for l in datefinder.find_dates(str(string))]
    else:
        return string


def identify_date_format(table, column):
    r"""
    Checks the datetime format by analysing ...
    """
    dict_count_format = {}
    for date_format in cp.FORMAT_DATES:
        format_regex = re.compile(cp.FORMAT_DATES[date_format])
        list_date_format = [[num, 1] if re.search(format_regex, c) else [num, 0] for num, c in enumerate(table[column]) if not pd.isnull(c)]
        dict_count_format[date_format] = sum(i[1] for i in list_date_format)
    # Count comparison
    final_format = max(dict_count_format, key=dict_count_format.get)
    return final_format


def get_pattern(filename, list_pattern):
    r"""
    Returns pattern if filename matches one and exactly one of the pattern from list_pattern
    Otherwise return None
    """
    test = [pattern for pattern in list_pattern if pattern.lower() in filename.lower()]
    if test:
        return max(test, key=len)
    else:
        return None


def get_modified_date(filename):
    r"""
    Return file last modified date
    """
    try:
        mtime = os.path.getmtime(filename)
    except OSError:
        mtime = 0
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")


def get_creation_date(filename):
    r"""
    Return file creation date
    """
    try:
        mtime = os.path.getctime(filename)
    except OSError:
        mtime = 0
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")


def get_file_size(filename):
    r"""
    Return file size
    """
    return os.path.getsize(filename)


def compare_two_lists(firstlist, secondlist):
    r"""
    Check if two lists given in arguments are equal element by element at same index position
    """
    if firstlist is None or secondlist is None or len(firstlist) != len(secondlist):
        return False
    else:
        if [idx for idx, pair in enumerate(zip(firstlist, secondlist)) if pair[0] == pair[1]]:
            return True
        else:
            return False


def get_nested_lists_intersection(nestedlist):
    r"""
    Generates the intersection between every lists inside a list
    """
    result = set(nestedlist[0])
    for s in nestedlist[1:]:
        result.intersection_update(s)
    return result


def flattern(nestedlist):
    rt = []
    for i in nestedlist:
        if isinstance(i, list):
            rt.extend(flattern(i))
        else:
            rt.append(i)
    return rt


def read_file(inputfile):
    r"""
    [Generator] Open and read the file line by line
    """
    with open(inputfile, 'r', encoding='ISO-8859-1') as f:
            for l in f:
                yield l


def max_occurence_char_in_list(inputlist, charlist):
    r"""
    [Generator] Count character occurences in inputlist foreach character in charlist
    Returns the character and occurences with max occurences
    """
    for line in inputlist:
        yield max([(d, line.count(d)) for d in charlist], key=lambda x: x[1])


def find_delimiter(inputfile):
    r"""
    Read a flat file and returns the delimiter having the greatest number of occurences
    """

    delimiter_list = [',', ':', ';', '|', '\t', '^', '#', '+', '%', '~', '*', '-', '_', '!', '=', '&', '$']

    delimiter = Counter(
        [l for l in max_occurence_char_in_list(
            [l for l in read_file(inputfile)], delimiter_list)]
    ).most_common(1)[0][0]
    if delimiter:
        return delimiter[0]
    else:
        return None


def map_parameters(string):
    r"""
    Read a flat file and returns the delimiter having the greatest number of occurences
    """
    pattern = re.compile(r"""<(iap_param_\w+)>""")
    m = re.search(pattern, str(string))
    if m:
        #lookup DICT_PARAMETER
        if m.group(1) in cp.DICT_PARAMETER:
            return cp.DICT_PARAMETER[m.group(1)]
    else:
        return string
