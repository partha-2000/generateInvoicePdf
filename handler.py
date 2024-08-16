import json

from sciSurface import sciProcessData
from tcfsouthwest import combine_pdfs, getDataFromS3, processData


def hello(event, context):
    print("event:---->", event)
    if event["tenant"] == "tcfSouthWest":
        pdfNames = processData(
            event,
        )
        pdfNames_filtered = [name for name in pdfNames if name is not None]
        print("pdfNames:", pdfNames_filtered)
        if len(pdfNames_filtered) > 1:
            combine_pdfs(pdfNames_filtered, f"{event['invoice_ref_no']}.pdf")
    elif event["tenant"] == "sciSurface":
        pdfNames = sciProcessData(event)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
