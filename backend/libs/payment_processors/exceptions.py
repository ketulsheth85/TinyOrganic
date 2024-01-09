class CouldNotChargeOrderError(Exception):
    ...


class CouldNotProcessChargeError(Exception):
    ...


class CouldNotFetchPaymentMethodError(Exception):
    ...


class CouldNotAttachPaymentMethodToProcessorCustomerError(Exception):
    ...


class CouldNotCreateSetupIntentError(Exception):
    ...


class CouldNotFetchProcessorCustomerError(Exception):
    ...


class CouldNotProcessRefundError(Exception):
    ...
