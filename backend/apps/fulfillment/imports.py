import csv

from django.apps import apps
from celery_app import app


def upload_fulfillment_center_zipcodes_from_csv(reader):
    FulfillmentCenter = apps.get_model('fulfillment', 'FulfillmentCenter')
    FulfillmentCenterZipCode = apps.get_model('fulfillment', 'FulfillmentCenterZipCode')
    for line in reader:
        location = line.get('Ship From')
        zipcode = line.get('Zip Code')

        if '#N/A' in location:
            print(f'{zipcode} is not supported')
            continue

        fulfillment_center = FulfillmentCenter.objects.get_or_create(
            location=location.lower()
        )[0]
        fulfillment_center_zipcode = FulfillmentCenterZipCode.objects.get_or_create(
            zipcode=zipcode
        )[0]
        fulfillment_center_zipcode.warehouses.add(fulfillment_center)

    return "Zipcodes successfully uploaded"

@app.task
def import_fulfillment_center_zipcodes_from_csv(decoded_file):
    reader = csv.DictReader(decoded_file)

    upload_fulfillment_center_zipcodes_from_csv(reader)







