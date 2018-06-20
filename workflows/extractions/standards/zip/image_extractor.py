import os
import sys
import zipfile


def extract_images_from_zip(
    input_path,
    target_folder,
    page_limit=False,
    image_on_page_limit=False
):
    r"""
    Extract all images from a given ZIP or DOCX
    """
    z = zipfile.ZipFile(input_path)

    # print all files in zip archive
    file_list = z.namelist()

    # Get all files in word/media/ directory
    image_list = [x for x in file_list if x.startswith('word/media/') and x.endswith(tuple(cp.ALLOWED_IMAGE_EXTENSION_LIST))]

    # Extract images
    extracted_image_list = list()
    for image in image_list:
        target_path = os.path.join(target_folder, image)
        extracted_image_list.append(image)
        z.extract(image, target_path)

    return extracted_image_list
