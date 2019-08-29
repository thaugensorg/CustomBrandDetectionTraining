import logging
import os
import json
import requests

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        # Get Cognitive Services Environment Variables
        projectID = os.environ["projectID"]
        trainingKey = os.environ['trainingKey']
        predictionKey = os.environ['predictionKey']
        clientEndpoint = "https://westus2.api.cognitive.microsoft.com"

        trainer = CustomVisionTrainingClient(trainingKey, endpoint=clientEndpoint)
        iterations = trainer.get_iterations(projectID)
        currentIteration = iterations[0]
        currentIterationName = currentIteration.publish_name

        httpEndpoint = "https://westus2.api.cognitive.microsoft.com/customvision/v3.0/Prediction/" + projectID + "/classify/iterations/" + currentIterationName + "/url"

        headers = {'Prediction-Key': predictionKey, 'Content-Type': 'application/json'}
        data = {"url": name}
        response = requests.post(httpEndpoint, headers = headers,
                                json = data)
        response.raise_for_status()

        responseDictionary = response.json()
        Prediction = responseDictionary['predictions'][0]
        confidence = Prediction['probability']
        responseDictionary['confidence'] = confidence
            
        # Display the results.
        return func.HttpResponse(json.dumps(responseDictionary))
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
