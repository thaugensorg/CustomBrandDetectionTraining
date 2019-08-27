import logging
import time
import os

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function TrainModel processed a request.')

    endpoint = "https://westus2.api.cognitive.microsoft.com"

    # Get Cognitive Services Environment Variables
    projectID = os.environ["projectID"]
    trainingKey = os.environ['trainingKey']
    publish_iteration_name = "classifyModel"
    prediction_resource_id = os.environ['predictionID']

    trainer = CustomVisionTrainingClient(trainingKey, endpoint=endpoint)

    try:
        iteration = trainer.train_project(projectID, force_train=True)
        while (iteration.status != "Completed"):
            iteration = trainer.get_iteration(projectID, iteration.id)
            logging.info("Training status: " + iteration.status)
            time.sleep(1)

    except Exception as e:
        message = str(e)
        logging.info(message)

    # The iteration is now trained. Publish it to the project endpoint
    trainer.publish_iteration(projectID, iteration.id, publish_iteration_name, prediction_resource_id)

    return func.HttpResponse(
        "Training complete for ProjectID: " + projectID,
        status_code=400)

