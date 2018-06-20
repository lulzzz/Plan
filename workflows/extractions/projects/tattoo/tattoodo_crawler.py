import json
import requests

from workflows.extractions.standards.crawlers import image_crawler


def exploit_api(api_url, max_page, limit, output_directory):

    # Iterate through API pages
    for page in range(1, max_page + 1):
        params = dict(
            page=page,
            limit=limit
        )

        res = requests.get(url=api_url, params=params)
        json_data = res.json() # Check the JSON Response Content documentation below

        for idx, item in enumerate(json_data.get('data')):
            image_obj = item.get('image')
            image_crawler.save_image(image_obj.get('url'), output_directory, idx)
