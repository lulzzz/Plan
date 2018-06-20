import os
import requests

def save_image(url, output_directory, counter):
    image_file_path = os.path.join(output_directory, str(counter).zfill(4) + '_' + os.path.basename(url))

    # Check if image was already downloaded
    if not os.path.isfile(image_file_path):

        # Load image
        img_response = requests.get(url)
        img_response.raise_for_status()

        # Save image
        saved_file = open(image_file_path, 'wb')
        for chunk in img_response.iter_content(100000): # number of iterations per loop
            saved_file.write(chunk)
        saved_file.close()
        print(os.path.basename(url), 'downloaded')
        return True

    else:
        print(os.path.basename(url), 'already in folder')
