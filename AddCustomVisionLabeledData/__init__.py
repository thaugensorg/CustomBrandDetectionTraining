import logging
import time
import os

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry

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

                {
                    "images": [
                      {
                        "url": "string",
                        "tagIds": [
                          "string"
                        ],
                        "regions": [
                          {
                            "tagId": "string",
                            "left": 0.0,
                            "top": 0.0,
                            "width": 0.0,
                            "height": 0.0
                          }
                        ]
                      }
                    ],
                    "tagIds": [
                      "string"
                    ]
                  }

        if ImageLabels:
            # https://pypi.org/project/custom_vision_client/
            # https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/blob/master/samples/vision/custom_vision_training_samples.py

            Endpoint = "https://westus2.api.cognitive.microsoft.com/customvision/v3.0/Training/"

            # Get Cognitive Services Environment Variables
            TrainingKey = os.environ['trainingKey']

            Trainer = CustomVisionTrainingClient(TrainingKey, endpoint=Endpoint)

            Project = Trainer.create_project("CustomBrandDetection")

            print("Adding images...")

            # Set image_url to the URL of the image that will be analyzed
            ImageUrl = BlobUrl

            # ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[hemlock_tag.id])

            Trainer.create_images_from_urls(Project.project_id, ImageUrl, tag_ids=[ImageLabels])
            # upload_result = Trainer.create_images_from_files(Project.id, images=image_list)

    else:
        return func.HttpResponse(
            "Please pass a URL to a blob file containing the image to be added to training in this request on the query string.",
            status_code=400
        )
