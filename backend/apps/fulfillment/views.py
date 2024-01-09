from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

from apps.core.views import CoreUploadCSVView
from apps.fulfillment.imports import import_fulfillment_center_zipcodes_from_csv


@method_decorator(staff_member_required, name='dispatch')
class UploadFulfillmentCenterZipcodes(CoreUploadCSVView):
    template_name = 'uploads/fulfillment-center-zipcodes.html'
    async_function = import_fulfillment_center_zipcodes_from_csv
    view_name = 'upload-fulfillment-center-zipcodes-csv'

    # Uncomment this line for testing locally
    # def post(self, request, *args, **kwargs):
    #     csv_file = request.FILES['csv_file']
    #     decoded_file = csv_file.read().decode('utf-8').splitlines()
    #     self.async_function(decoded_file)
    #     messages.add_message(request=request, level=messages.SUCCESS, message='File Will be processed shortly!')
    #     return redirect(reverse(self.view_name))
