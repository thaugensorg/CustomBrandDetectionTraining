import logging
import requests

import azure.functions as func

# https://2.python-requests.org//en/latest/api/
# https://stackoverflow.com/questions/9746303/how-do-i-send-a-post-request-as-a-json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ProjectID = req.params.get('projectID')
    if not ProjectID:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('projectID')

    if ProjectID:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('projectID')
    else:
        return func.HttpResponse(
             "Please pass a projectID and JSON containing valid labels on the query string and in the request body",
             status_code=400
        )
