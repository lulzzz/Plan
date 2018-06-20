import os
from datetime import datetime
from dateutil import parser

from django.conf import settings as cp
from django.urls import reverse_lazy


def get_current_date_id():
    r"""
    Convert current date into dim_date_id
    """
    return int(datetime.today().strftime('%Y%m%d'))


def is_ascii(s):
    r"""
    String encoding
    """
    try:
        s.encode('ascii');
        return True
    except UnicodeEncodeError:
        return False


def handle_uploaded_file(upload_dir, f):
    r"""
    Upload file handler
    """
    file_path = os.path.join(cp.MEDIA_ROOT, upload_dir, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def get_weekday_list():
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def millions_formatter(num, m=1000000):
    # If the number evenly divides 1000000, you can convert its division of 1000000 to an integer
    if num % m == 0:
        num = int(num/m)
    else:
        # Otherwise use a floating representation
        num = float(num/m)
    return '{0:.2f}M'.format(num)

def convert_float_to_percentage(x, decimal_number=0):
    percentage_format = '{:.' + str(decimal_number) + '%}'
    return percentage_format.format(x)

def percentage_to_float(x):
    try:
        float(x)
        return x
    except ValueError:
        return float(str(x).strip('%'))/100

# TODO
def check_list_depth(l, counter, counter_list=list()):
    counter += 1
    counter_list.append(counter)
    for item in l:
        if type(item) is list:
            check_list_depth(item, counter, counter_list=counter_list)

    return counter, counter_list

def check_list_depth_flat(l):
    for item in l:
        if type(item) is list:
            return False
    return True

def get_all_fields_from_form(instance):
    r"""
    Return names of all available fields from given Form instance.

    :arg instance: Form instance
    :returns list of field names
    :rtype: list
    """

    fields = list(instance().base_fields)

    for field in list(instance().declared_fields):
        if field not in fields:
            fields.append(field)
    return fields

def get_clean_list_of_dict(input_list):
    r"""
    Return input list without dict items for which all values are empty
    """
    output_list = list()
    for item in input_list:
        if not all(xstr(value) is None for value in item.values()):
            output_list.append(item)
    return output_list


def convert_list_of_dicts_into_list_of_lists(list_of_dicts):
    r"""
    Return input list of dicts into a list of lists
    E.g. [{a: 1, b: 2}}, {a: 10, b: 20}}] returns [[1, 2], [10, 20]]
    """
    list_of_lists = list()
    for d in list_of_dicts:
        list_of_lists.append(list(d.values()))

    return list_of_lists


def adjust_dict_key_values(json, form_field_names_list):
    r"""
    Return list of dict with right dict keys
    Converts list of dicts with keys as verbose field name into name keys
    Converts list of lists into list of dicts with right dict keys
    """
    output_list = list()

    # Iterate through json list
    for item in json:
        temp_dict = dict()

        # item is list
        if type(item) is list:
            for idx, sub_item in enumerate(item):
                temp_dict[form_field_names_list[idx]] = sub_item
            output_list.append(temp_dict)

        # item is dict
        if type(item) is dict:
            counter = 0
            for k, v in item.items():
                temp_dict[form_field_names_list[counter]] = v
                counter += 1
            output_list.append(temp_dict)

    return output_list


def xstr(s):
    r"""
    Return None if string is empty
    """
    if s is None:
        return None
    if str(s).join(str(s).split()) == '':
        return None
    return str(s)


def xint(s):
    r"""
    Return 0 if not an integer
    """
    try:
        int(s)
        return s
    except (ValueError, TypeError) as e:
        return None



def create_user_repository(username):
    r"""
    Create repository of user if not existant
    """
    if not os.path.exists(cp.STATIC_FILE_PATH + username + '/'):
        os.makedirs(cp.STATIC_FILE_PATH + username + '/')


def write_to_file(file_path, text, with_time_stamp=True, clean_file=False):
    filename = file_path

    if clean_file: # Eventually empty the file
        open(filename, 'w').close()

    if with_time_stamp: # Eventually add timestamp
        text = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': ' + text + '\n'

    f = open(filename, 'a')
    f.write(text)
    f.close()


def read_from_file(file_path):
    filename = file_path
    if os.path.exists(filename):
        fp = open(filename)
        data = fp.read()
    else:
        data = filename
    return str(data)


def compare_two_lists(firstlist, secondlist):
    # Check if two lists given in arguments are equal element by element at same index position
    if firstlist is None or secondlist is None or len(firstlist) != len(secondlist):
        return False
    else:
        if [idx for idx, pair in enumerate(zip(firstlist, secondlist)) if pair[0] == pair[1]]:
            return True
        else:
            return False


def str_to_date(var):
    try:
        return parser.parse(var)
    except ValueError:
        return None

def date_to_str(dt, default):
    if dt is None:
        return default
    else:
        return str(dt)

def format_date(var):
    if var:
        if len(var) >= 10:
            return str(var)[:10]
    return var

def rewrite_with_functional_convention(input_obj):
    r'''
    Returns the input list with Capital letters and spaces instead of underscores
    '''
    if type(input_obj) is dict:
        return {str(k).replace('_', ' ').title(): v for k, v in input_obj.items()}
    elif type(input_obj) is list:
        return [str(x).replace('_', ' ').title() for x in input_obj]
    else:
        return str(input_obj).replace('_', ' ').title()



def format_as_percentage(var):
    r'''
    Returns numeric value formatted as percentage
    '''
    return "{0:.0f}%".format(var*100)


def str_to_list(var):
    r'''
    Returns text or numeric value as list object
    '''
    if type(var) is list:
        if all(x.isdigit() for x in var):
            return [int(i) for i in var]
        return var
    else:
        if isinstance(var, int):
            return [int(var)]
        return [var]


def transpose_table_horizontally(data_list):
    r'''
    Returns transposed list
    '''
    return list(map(list, zip(*data_list)))


def remove_json_duplicates(json_list, key_duplicate=None):
    r'''
    Returns list of dictionaries without duplicates
    '''
    if key_duplicate:
        return_list = list()
        value_memory_list = list()
        for item in json_list:
            if item[key_duplicate] not in value_memory_list:
                value_memory_list.append(item[key_duplicate])
                return_list.append(item)
        return return_list
    return [dict(t) for t in set([tuple(d.items()) for d in json_list])]


def generate_serialized_list(model, modelserializer, search_field_list, query, search_type='icontains'):
    r'''
    Returns serialized list
    TODO: eventually delete and replace with generate_search_list
    '''
    serializer_combined = list()

    for search_field in search_field_list:
        search_filter = search_field + '__' + search_type
        queryset = model.objects.filter(**{search_filter: query}).distinct().order_by(search_field)
        serializer = modelserializer(
            queryset,
            many=True,
            context={'label_field': search_field}
        )
        serializer_combined = serializer_combined + serializer.data

    return serializer_combined


def generate_search_list(query, query_list_of_dict, limit=15):
    r'''
    Returns search list
    '''
    search_list = list()
    label_track = list()
    for query_dict in query_list_of_dict:
        if len(search_list) >= limit:
            break

        search_filter = {
            query_dict['search_field'] + '__' + query_dict['search_type']: query
        }
        if query_dict.get('additional_filter'):
            search_filter = {**search_filter, **query_dict.get('additional_filter')}

        queryset = query_dict['model'].objects.filter(**search_filter).distinct().order_by(query_dict['search_field'])[:limit]
        for item in queryset:

            if query_dict['is_unique']:
                item_id = item.id
                item_url = getattr(item, 'url')
            else:
                item_id = 'item'
                item_url = reverse_lazy(
                    query_dict['search_tab'],
                    kwargs={'keyword': getattr(item, query_dict['search_field'])}
                ).replace('/', '#', 1)

            item_name = query_dict['search_tab'] + str(getattr(item, query_dict['search_field']))
            item_label = str(getattr(item, query_dict['search_field'])) + ' [' + query_dict['search_field_label'] + ']'

            if item_label not in label_track:
                label_track.append(item_label)
                search_list.append({
                    'id': item_id,
                    'name': item_name,
                    'label': item_label,
                    'url': item_url
                })

    return search_list[:limit]
