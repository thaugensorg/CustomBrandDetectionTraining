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

    dataBlobUrl = req.params.get('dataBlobUrl')
    if not dataBlobUrl:
        return func.HttpResponse(
                "Please pass a URL to a blob containing the image to be added to training in this request on the query string.",
                status_code=400
        )

    if dataBlobUrl:
        ImageLabels = req.params.get('imageLabels')
        if not ImageLabels:
            try:
                ImageLabels = req.get_json()
            except:
                return func.HttpResponse(
                    "Please pass JSON containing the labels associated with this image on the query string or in the request body.",
                    status_code=400
                )
                
        if ImageLabels:
            # https://pypi.org/project/custom_vision_client/
            # https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/blob/master/samples/vision/custom_vision_training_samples.py

            Labels = []
            CountOfTagsAppliedToTimage = 0
            Endpoint = os.environ['clientEndpoint']

            # Get Cognitive Services Environment Variables
            ProjectID = os.environ["projectID"]
            TrainingKey = os.environ['trainingKey']

            # strip out list of Image Labels passed in request
            ImageLabels = json.loads(ImageLabels)

            # retrieve tags from project and loop through them to find tag ids for tags that need to be applied to the image
            Trainer = CustomVisionTrainingClient(TrainingKey, endpoint=Endpoint)
            Tags = Trainer.get_tags(ProjectID)
            for ImageLabel in ImageLabels:
                for Tag in Tags:
                    if Tag.name == ImageLabel:
                        Labels.append(Tag.id)
                        CountOfTagsAppliedToTimage = CountOfTagsAppliedToTimage + 1
                        break
            
            # create the image from a url and attach the appropriate tags as labels.
            Trainer.create_images_from_urls(ProjectID, [ImageUrlCreateEntry(url=dataBlobUrl, tag_ids=Labels) ])

            return func.HttpResponse(str(CountOfTagsAppliedToTimage) + " Tag(s) applied to image at url: " + dataBlobUrl)


    else:
        return func.HttpResponse(
            "Please pass a URL to a blob file containing the image to be added to training in this request on the query string.",
            status_code=400
        )