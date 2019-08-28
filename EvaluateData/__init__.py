import logging
import os
import json

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

        endpoint = "https://westus2.api.cognitive.microsoft.com"

        # Get Cognitive Services Environment Variables
        projectID = os.environ["projectID"]
        trainingKey = os.environ['trainingKey']
        predictionKey = os.environ['predictionKey']

        trainer = CustomVisionTrainingClient(trainingKey, endpoint=endpoint)
        predictor = CustomVisionPredictionClient(predictionKey, endpoint=endpoint)

        iterations = trainer.get_iterations(projectID)
        currentIteration = iterations[0]
        currentIterationName = currentIteration.publish_name
        results = predictor.classify_image_url(projectID, currentIterationName, name)

        # Display the results.
        resultsJson = json.dumps(results.predictions[0]])
        for prediction in results.predictions:
            print("\t" + prediction.tag_name +
                 ": {0:.2f}%".format(prediction.probability * 100))

        return func.HttpResponse(resultsJson)
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
