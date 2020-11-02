import logging
import time
import os
import json
import requests

from datetime import datetime

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function TrainModel processed a request.')

    try: 
        # Get Cognitive Services Environment Variables
        project_id = os.environ["ProjectID"]
        training_key = os.environ['TrainingKey']
        client_endpoint = os.environ['ClientEndpoint']
        publish_iteration_name = "SampleTreeClassification"
        prediction_resource_id = os.environ['ResourceID']

    except Exception as e:
        message = str(e)
        logging.info(message)

        return func.HttpResponse(
            "Please ensure ProjectID, TrainingKey, ClientEndpoint, and ResourceID environment variables are correctly configured.",
            status_code=400
        )


    if project_id and training_key and client_endpoint and publish_iteration_name and prediction_resource_id:
        trainer = CustomVisionTrainingClient(training_key, endpoint=client_endpoint)

        try:
            #*****TODO***** add notification email
            iteration = trainer.train_project(project_id, force_train=True) #*****TODO***** turn off force train when releasing
            logging.info("turn off force train when releasing")
            iteration = trainer.get_iteration(project_id, iteration.id)
            logging.info("Training status: " + iteration.status)
            while (iteration.status != "Completed"):
                time.sleep(5) 
                iteration = trainer.get_iteration(project_id, iteration.id)
                logging.info("Training status: " + iteration.status)
                  

            # The iteration is now trained. Publish it to the project endpoint
            # Because we need to use HTTP calls for the Evaluate Data interface it must also be published via HTTP or evaluate fails until unpublished and republished via the CustomVision portal
            # trainer.publish_iteration(project_id, iteration.id, publish_iteration_name, prediction_resource_id)
            # Publish name must be unique or the publish fails
            http_endpoint = client_endpoint + "/customvision/v3.2/training/projects/" + project_id + "/iterations/" + iteration.id + "/publish?publishName="+ publish_iteration_name + "&predictionId=" + prediction_resource_id

            # add headers and body to the call and get the response
            headers = {'Training-key': training_key, 'Content-Type': 'application/json'}
            response = requests.post(http_endpoint, headers = headers)

            # Extract the json for the response
            response_dictionary = response.json()
            logging.info(response_dictionary)

            # Handle publishing errors by logging and returning to calling host
            if response.ok == False:
                logging.info(response_dictionary['message'])
                return func.HttpResponse(
                "Publishing failed for ProjectID: " + project_id + " could not be published with message: " + response_dictionary['message'],
                status_code=400)

        except Exception as e:
            message = str(e)
            logging.info(message)
            
            return func.HttpResponse(
                "Training failed for ProjectID: " + project_id + " could not be trained with message: " + message,
                status_code=400)

        return func.HttpResponse(
            "Training complete for ProjectID: " + project_id + " published under iteration name: " + publish_iteration_name,
            status_code=200)

    else:
        return func.HttpResponse(
            "Please ensure ProjectID, TrainingKey, ClientEndpoint, and ResourceID environment variables are correctly configured.",
            status_code=400
        )
