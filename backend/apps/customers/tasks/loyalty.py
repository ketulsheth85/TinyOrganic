from libs.yotpo_client import (
    YotpoClient,
    CouldNotCreateYotpoCustomerError,
    CouldNotUpdateYotpoCustomerError,
    LoyaltyProgramCustomer,
)
from sentry_sdk.utils import logger


def create_loyalty_customer(customer: 'Customer'):
    loyalty_customer = LoyaltyProgramCustomer(
        id=str(customer.id),
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name
    )
    client = YotpoClient()

    try:
        client.create_customer(loyalty_customer)
    except CouldNotCreateYotpoCustomerError as e:
        # maybe a celery task to create yotpo customer async?
        logger.error(e)


def update_to_loyalty_client(customer: 'Customer'):
    loyalty_customer = LoyaltyProgramCustomer(
        id=str(customer.id),
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name
    )
    client = YotpoClient()
    try:
        client.update_customer(loyalty_customer)
    except CouldNotUpdateYotpoCustomerError as e:
        # maybe a celery task to update yotpo customer async?
        logger.error(e)

