import logging
import requests
import json
import os
import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
# from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntr
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

# https://2.python-requests.org//en/latest/api/
# https://stackoverflow.com/questions/9746303/how-do-i-send-a-post-request-as-a-json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ProjectID = req.params.get('projectID')
    if not ProjectID:
        return func.HttpResponse(
             "Please pass a projectID and JSON containing valid labels on the query string and in the request body",
             status_code=400
        )

    if ProjectID:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            ENDPOINT = "https://westus2.api.cognitive.microsoft.com"
            TrainingKey = os.environ['trainingkey']
            Trainer = CustomVisionTrainingClient(TrainingKey, endpoint=ENDPOINT)

            LabelDictionary = json.loads(req_body)
            for i in LabelDictionary.values():
                Label = Trainer.create_tag(ProjectID, LabelDictionary.values()[i])
                
            return func.HttpResponse("Loaded " + i + " labels into " + ProjectID)
    else:
        return func.HttpResponse(
             "Please pass a projectID and JSON containing valid labels on the query string and in the request body",
             status_code=400
        )
