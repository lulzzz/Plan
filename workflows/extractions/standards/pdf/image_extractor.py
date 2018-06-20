import sys
import os
# import logging
import io
from datetime import datetime
# logging.getLogger().setLevel(logging.DEBUG)

import PyPDF2
from PyPDF2 import PdfFileReader
from PIL import Image
from slugify import slugify


def extract_images_from_pdf(
    file_property,
    target_folder,
    page_limit=False,
    image_on_page_limit=False
):
    r"""
    Extract all images from a given PDF file
    """
    database_atoms = list()
    success_list = list()
    fail_list = list()

    # Read entire PDF document in memory
    pdf_full_name = file_property['name'] + file_property['extension']
    # logging.debug('file_property: ' + pdf_full_name)
    pdf_basename = file_property['name']

    try:
        pdf_obj = PdfFileReader(open(file_property['abs_path'], "rb"), strict=False)
    except (PyPDF2.utils.PdfReadError) as e:
        # logging.debug(pdf_full_name + ': EOF marker not found')
        return False
    except (OSError) as e:
        # logging.debug(pdf_full_name + ": File can't be read")
        return False

    if page_limit:
        total_pages = page_limit
    else:
        # Iterate through PDF document pages
        try:
            total_pages = pdf_obj.getNumPages()
        except (PyPDF2.utils.PdfReadError) as e:
            # logging.debug(pdf_full_name + ': Error getting number of pages')
            return False


    for page_count in range(total_pages):
        page_count_label = page_count + 1
        # logging.debug('Page: ' + str(page_count_label))
        page_obj = pdf_obj.getPage(page_count)

        # Check if page contains xObject metadata (implies it has an image)
        resources = page_obj.get('/Resources')
        # while True:
        try:
            xObject = resources.get('/XObject')
            xObject = xObject.getObject()
        except AttributeError as e:
            # logging.debug('No xObject on page')
            resources = resources.getObject()
            continue

        # Iterating through images on page
        for idx, obj in enumerate(xObject, 1):

            # Catch object instance
            item = xObject[obj]

            # Extracting image depending on format
            img_name = slugify(pdf_basename) + '_page' + str(page_count_label) + '_img' + str(idx)
            path_name = os.path.join(target_folder, img_name)
            # logging.debug('Scanning image: ' + str(img_name))

            # Get image object if contained within other objects (sub xObject)
            # if item.get('/Resources'):
            #     logging.debug('Resources loop')
            #     xObject_sub = item.get('/Resources').get('/XObject')
            #     xObject_sub = xObject_sub.getObject()
            #     for obj_sub in xObject_sub:
            #         item = xObject_sub[obj_sub]
            #         if item.get('/Subtype') == '/Image':
            #             break

            # Check if image exists on page
            if item['/Subtype'] == '/Image':
                size = (item['/Width'], item['/Height'])
                # logging.debug('Size: ' + str(size))

                # Loading data for png image
                try:
                    data = item.getData()
                except (NotImplementedError, AssertionError) as e:
                    # Loading data for jpeg image
                    try:
                        data = item._data
                    except (ValueError, AssertionError) as e:
                        # logging.debug('Issue loading image data: ' + e)
                        continue

                # Extracting color settings
                try:
                    mode = "RGB" if item['/ColorSpace'] == '/DeviceRGB' else "P"
                except KeyError as e:
                    mode = "P"


                img_name_full = False
                img_filter = item.get('/Filter')

                # In case of ArrayObject, get first value as PyPDF2.generic.NameObject
                if isinstance(img_filter, PyPDF2.generic.ArrayObject):
                    # logging.debug('Get NameObject from ArrayObject')
                    img_filter = img_filter[0]

                # logging.debug('img_filter: ' + str(img_filter))
                if img_filter== '/FlateDecode':
                    img_name_full = path_name + ".png"
                    try:
                        img = Image.frombytes(mode, size, data)
                        img.save(img_name_full)
                    except (ValueError) as e:
                        # logging.debug('Exception in /FlateDecode: ' + str(e))
                        # logging.warning('Data returned by image is the image itself not the RAW RGB data')
                        continue
                        # sys.exit()
                        # img = Image.open(io.BytesIO(data))
                        # img.save(img_name_full)
                elif img_filter == '/DCTDecode':
                    img_name_full = path_name + ".jpg"
                    img = open(img_name_full, "wb")
                    img.write(data)
                    img.close()
                elif img_filter == '/JPXDecode':
                    img_name_full = path_name + ".jp2"
                    img = open(img_name_full, "wb")
                    img.write(data)
                    img.close()


                if img_name_full:
                    success_list.append(img_name_full)
                    # logging.debug('Image extracted')

                    entry = {
                        'has_data': 1,
                        'source_master_name': slugify(file_property['name'], separator='_'),
                        'source_master_label': file_property['name'],
                        'source_master_reference': file_property['name'] + file_property['extension'],
                        'source_master_pattern': file_property['name'] + file_property['extension'],
                        'source_master_component_category': 'graphic',
                        'source_master_component_reference': img_name_full,
                        'source_master_component_name': img_name,
                        'source_master_component_label': 'Cover Sheet Graphic',
                        'source_metadata_field_format': file_property['extension'][1:],
                        'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
                        'source_metadata_last_modified_by': 'TBD',
                        'source_metadata_file_relative_path': file_property['rel_path'],
                        'source_metadata_file_absolute_path': file_property['abs_path'],
                        'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
                        'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
                        'source_metadata_file_company': 'Li & Fung Limited'
                    }

                    database_atoms.append(entry)
                else:
                    fail_list.append(img_name_full)

                # sys.exit()
            else:
                # logging.debug('No image on page')
                pass

            # Stop iterating if limit reached
            if image_on_page_limit == idx:
                break

    if not success_list:
        # logging.warning('No image extracted for file: ' + pdf_full_name)
        if not fail_list:
            fail_list.append(pdf_full_name)
        return False

    return database_atoms
