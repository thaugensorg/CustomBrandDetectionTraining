import logging
import requests
import json
import os
import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

# https://2.python-requests.org//en/latest/api/
# https://stackoverflow.com/questions/9746303/how-do-i-send-a-post-request-as-a-json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ProjectID = req.params.get('projectID')
    if not ProjectID:
        return func.HttpResponse(
             "Please pass a projectID on the query string.",
             status_code=400
        )

    if ProjectID:
        LabelsJson = req.params.get('labelsJson')
        if not LabelsJson:
            LabelsJson = req.get_json()
            if not LabelsJson:
                return func.HttpResponse(
                    "Please pass JSON containing valid labels on the query string or in the request body.",
                    status_code=400
                )
        
        if LabelsJson:

            ENDPOINT = "https://westus2.api.cognitive.microsoft.com/customvision/v3.0/Training/"
            TrainingKey = os.environ['trainingKey']
            Trainer = CustomVisionTrainingClient(TrainingKey, endpoint=ENDPOINT)

            LabelDictionary = json.loads(LabelsJson)
            for i in LabelDictionary.values():
                Trainer.create_tag(ProjectID, LabelDictionary.values()[i])
                
            return func.HttpResponse("Loaded " + i + " labels into " + ProjectID)
    else:
        return func.HttpResponse(
             "Please pass a projectID and JSON containing valid labels on the query string and in the request body",
             status_code=400
        )
