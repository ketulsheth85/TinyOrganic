from django.test import TestCase

from apps.fulfillment.imports import upload_fulfillment_center_zipcodes_from_csv
from apps.fulfillment.models import FulfillmentCenter, FulfillmentCenterZipcode


class FulfillmentCenterUploadCSVTestSuite(TestCase):

    def test_can_add_all_zipcodes_to_one_warehouse_from_csv(self):
        decoded_file = [
            {
                'Ship From': 'Wallace',
                'Zip Code': '33165'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '33167'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '33168'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '33169'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '33170'
            },
        ]

        zipcodes_from_csv = {line.get('Zip Code') for line in decoded_file}
        upload_fulfillment_center_zipcodes_from_csv(decoded_file)

        warehouse = FulfillmentCenter.objects.get(location='wallace')
        warehouse_zipcodes = {zipcode.zipcode for zipcode in warehouse.zipcodes.filter()}
        self.assertEquals(zipcodes_from_csv, warehouse_zipcodes)

    def test_can_add_zipcodes_when_multiple_warehouses_exist_in_csv(self):
        decoded_file = [
            {
                'Ship From': 'Wallace',
                'Zip Code': '11111'
            },
            {
                'Ship From': 'Kentucky',
                'Zip Code': '22222'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '33333'
            },
            {
                'Ship From': 'Kentucky',
                'Zip Code': '44444'
            },
            {
                'Ship From': 'Wallace',
                'Zip Code': '55555'
            },
        ]

        upload_fulfillment_center_zipcodes_from_csv(decoded_file)

        wallace_warehouse = FulfillmentCenter.objects.get(location='wallace')
        kentucky_warehouse = FulfillmentCenter.objects.get(location='kentucky')

        zipcodes_from_wallace = {zipcode.zipcode for zipcode in wallace_warehouse.zipcodes.filter()}
        zipcodes_from_kentucky = {zipcode.zipcode for zipcode in kentucky_warehouse.zipcodes.filter()}

        self.assertEquals(zipcodes_from_wallace, {'11111', '33333', '55555'})
        self.assertEquals(zipcodes_from_kentucky, {'22222', '44444'})

    def test_will_skip_lines_with_hashtag_n_a_warehouses(self):
        decoded_file = [
            {
                'Ship From': 'Orlando',
                'Zip Code': '99999'
            },
            {
                'Ship From': '#N/A',
                'Zip Code': '22222'
            },
            {
                'Ship From': 'Orlando',
                'Zip Code': '10100'
            },
        ]

        upload_fulfillment_center_zipcodes_from_csv(decoded_file)
        orlando_warehouse = FulfillmentCenter.objects.get(location='orlando')
        zipcodes_from_orlando = {zipcode.zipcode for zipcode in orlando_warehouse.zipcodes.filter()}
        self.assertEquals(zipcodes_from_orlando, {'99999', '10100'})

    def test_will_add_same_zipcode_to_multiple_warehouses(self):
        decoded_file = [
            {
                'Ship From': 'orlando',
                'Zip Code': '12345'
            },
            {
                'Ship From': 'kirkland',
                'Zip Code': '12345'
            },
        ]

        upload_fulfillment_center_zipcodes_from_csv(decoded_file)
        zipcode = FulfillmentCenterZipcode.objects.get(zipcode='12345')
        zipcodes_from_orlando = {warehouse.location for warehouse in zipcode.warehouses.filter()}
        self.assertEquals(zipcodes_from_orlando, {'orlando', 'kirkland'})
