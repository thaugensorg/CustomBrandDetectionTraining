import logging
import time
import os
import requests
import json

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function AddLabeledDataClient processed a request.')

    try:
        # retrieve the parameters from the multi-part form http request
        image_url = req.form.get('ImageUrl')
        image_labeling_json = req.form.get('DataLabels')
    except:
        return func.HttpResponse(
            "Please pass JSON containing the labeled regions associated with this image on the query string or in the request body.",
            status_code=400
        )

    # validate both parameters were passed into the function
    if image_url and image_labeling_json:
        labels = []
        count_of_labels_applied_to_image = 0

        endpoint = os.environ['ClientEndpoint']

        # Get Cognitive Services Environment Variables
        project_id = os.environ["ProjectID"]
        training_key = os.environ['TrainingKey']

        # load labeled image regions passed in request into dictionary
        image_labeling_data = json.loads(image_labeling_json)

        # instanciate custom vision client
        trainer = CustomVisionTrainingClient(training_key, endpoint=endpoint)

        # retrieve tags from project and loop through them to find tag ids for tags that need to be applied to the image
        tags = trainer.get_tags(project_id)
        image_label = image_labeling_data["label"]
        for tag in tags:
            if tag.name == image_label:
                labels.append(tag.id)
                count_of_labels_applied_to_image = count_of_labels_applied_to_image + 1
                break
        
        # create the image from a url and attach the appropriate tags as labels.
        upload_result = trainer.create_images_from_urls(project_id, [ImageUrlCreateEntry(url=image_url, tag_ids=labels) ])
        if upload_result.is_batch_successful:
            return func.HttpResponse(str(count_of_labels_applied_to_image) + " Tag(s) applied to image at url: " + image_url)
        else:
            return func.HttpResponse("Upload of " + image_url + " failed.")

    else:
        return func.HttpResponse(
            "Please pass a URL to a blob file containing the image to be added to training in this request on the query string.",
            status_code=400
        )