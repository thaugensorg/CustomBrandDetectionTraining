import logging
import time

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntr
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

        # https://pypi.org/project/custom_vision_client/

        ENDPOINT = "https://westus2.api.cognitive.microsoft.com"

        # Get Cognitive Services Environment Variables
        training_key = os.environ['trainingKey']
        prediction_key = os.environ['predictionKey']
        prediction_resource_id = os.environ['predictionID']

        publish_iteration_name = "prototypeModel"

        trainer = CustomVisionTrainingClient(training_key, endpoint=ENDPOINT)

        project = trainer.create_project("CustomBrandDetection")

        # Make two tags in the new project
        hemlock_tag = trainer.create_tag(project.id, "Hemlock")
        cherry_tag = trainer.create_tag(project.id, "Japanese Cherry")

        base_image_url = "<path to project>"

        print("Adding images...")

        image_list = []

        # Set image_url to the URL of the image that will be analyzed
        image_url = name

        for image_num in range(1, 11):
            file_name = "hemlock_{}.jpg".format(image_num)
            with open(base_image_url + "images/Hemlock/" + file_name, "rb") as image_contents:
                image_list.append(ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[hemlock_tag.id]))

        for image_num in range(1, 11):
            file_name = "japanese_cherry_{}.jpg".format(image_num)
            with open(base_image_url + "images/Japanese Cherry/" + file_name, "rb") as image_contents:
                image_list.append(ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[cherry_tag.id]))

        upload_result = trainer.create_images_from_urls()
        upload_result = trainer.create_images_from_files(project.id, images=image_list)
        if not upload_result.is_batch_successful:
            print("Image batch upload failed.")
            for image in upload_result.images:
                print("Image status: ", image.status)
            exit(-1)

        print ("Training...")
        iteration = trainer.train_project(project.id)
        while (iteration.status != "Completed"):
            iteration = trainer.get_iteration(project.id, iteration.id)
            print ("Training status: " + iteration.status)
            time.sleep(1)

        # The iteration is now trained. Publish it to the project endpoint
        trainer.publish_iteration(project.id, iteration.id, publish_iteration_name, prediction_resource_id)
        print ("Done!")

        # Now there is a trained endpoint that can be used to make a prediction
        predictor = CustomVisionPredictionClient(prediction_key, endpoint=ENDPOINT)

        with open(base_image_url + "images/Test/test_image.jpg", "rb") as image_contents:
            results = predictor.classify_image(
                project.id, publish_iteration_name, image_contents.read())

        # Display the results.
        for prediction in results.predictions:
            print("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))

    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
