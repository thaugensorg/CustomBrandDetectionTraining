import logging
import time
import os
import requests
import json

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function AddLabeledDataHttp processed a request.')

    # Get Cognitive Services Environment Variables
    ProjectID = os.environ["projectID"]
    TrainingKey = os.environ['trainingKey']

    if ProjectID:
        BlobUrl = req.params.get('dataBlobUrl')
        if not BlobUrl:
            return func.HttpResponse(
                    "Please pass a URL to a blob containing the image to be added to training in this request on the query string.",
                    status_code=400
            )

        if BlobUrl and ProjectID:
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

                BodyDictionary = json.loads(ImageLabels)
                BodyDictionary['images'][0]['url'] = BlobUrl

                Endpoint = "https://westus2.api.cognitive.microsoft.com/customvision/v3.0/Training/projects/" + ProjectID + "/images/urls"

                headers = {'Training-key': TrainingKey}
                response = requests.post(Endpoint, headers=headers,
                                        json=BodyDictionary)

                return func.HttpResponse(response.body)


        else:
            return func.HttpResponse(
                "Either the blob URL or the project ID is not properly provided.",
                status_code=400
            )
    else:
        return func.HttpResponse(
            "Please configure projectID in your environment variables.",
            status_code=400
        )

