from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from apps.core.views import CoreUploadCSVView
from apps.discounts.tasks import import_discount_codes_from_file


class ImportDiscountCodesView(CoreUploadCSVView):
    template_name = 'uploads/discount_codes.html'
    async_function = import_discount_codes_from_file
    view_name = 'upload_discount_codes'
