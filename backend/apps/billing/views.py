from apps.core.views import CoreUploadCSVView
from apps.billing.tasks import import_refunds_from_file


class ImportRefundView(CoreUploadCSVView):
    template_name = 'uploads/refunds.html'
    async_function = import_refunds_from_file
    view_name = 'bulk_upload_refunds'
