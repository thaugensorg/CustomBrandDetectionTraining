import logging
import time
import os

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    BlobUrl = req.params.get('blobUrl')
    Labels = req.params.get('labels')
    if not BlobUrl:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            BlobUrl = req_body.get('blobUrl')

    if BlobUrl:

        # https://pypi.org/project/custom_vision_client/
        # https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/blob/master/samples/vision/custom_vision_training_samples.py

        ENDPOINT = "https://westus2.api.cognitive.microsoft.com"

        # Get Cognitive Services Environment Variables
        TrainingKey = os.environ['trainingkey']

        Trainer = CustomVisionTrainingClient(TrainingKey, endpoint=ENDPOINT)

        Project = Trainer.create_project("CustomBrandDetection")

        print("Adding images...")

        # Set image_url to the URL of the image that will be analyzed
        ImageUrl = BlobUrl

        # ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[hemlock_tag.id])

        upload_result = Trainer.create_images_from_urls(Project.project_id, ImageUrl, tag_ids=[Labels])
        # upload_result = Trainer.create_images_from_files(Project.id, images=image_list)

    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
