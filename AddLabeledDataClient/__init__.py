import logging
import time
import os
import requests
import json

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ProjectID = req.params.get('projectID')
    if not ProjectID:
        return func.HttpResponse(
                "Please pass the custom vision project id from the custom vision portal as a query string.",
                status_code=400
        )

    BlobUrl = req.params.get('blobUrl')
    if not BlobUrl:
        return func.HttpResponse(
                "Please pass a URL to a blob containing the image to be added to training in this request on the query string.",
                status_code=400
        )

    if BlobUrl and ProjectID:
        ImageLabels = req.params.get('imageLabels')
        if not ImageLabels:
            ImageLabels = req.get_json()
            if not ImageLabels:
                return func.HttpResponse(
                    "Please pass JSON containing the labels associated with this image on the query string or in the request body.",
                    status_code=400
                )
                
        if ImageLabels:
            # https://pypi.org/project/custom_vision_client/
            # https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/blob/master/samples/vision/custom_vision_training_samples.py

            # BodyDictionary = json.loads(ImageLabels)
            # BodyDictionary['images'][0]['url'] = BlobUrl


            Labels = []
            CountOfTagsAppliedToTimage = 0
            Endpoint = "https://westus2.api.cognitive.microsoft.com"

            # Get Cognitive Services Environment Variables
            TrainingKey = os.environ['trainingKey']

            # strip out list of Image Labels passed in request
            LabelDictionary = json.loads(ImageLabels)
            ImageLabels = LabelDictionary['Labels']

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
            Trainer.create_images_from_urls(ProjectID, [ImageUrlCreateEntry(url=BlobUrl, tag_ids=Labels) ])

            return func.HttpResponse(str(CountOfTagsAppliedToTimage) + " Tages applied to image at url: " BlobUrl)


    else:
        return func.HttpResponse(
            "Please pass a URL to a blob file containing the image to be added to training in this request on the query string.",
            status_code=400
        )