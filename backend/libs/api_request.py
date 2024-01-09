import requests
from dataclasses import dataclass
from typing import Dict, Any, Union

import requests_mock
from django.apps import apps
from furl import furl
import re
import json


@dataclass
class APIResponseDTO:
    status_code: int
    headers: Dict
    raw_body: Any
    parsed_body: Dict

    def __setattr__(self, name, value):
        if name == 'status_code':
            assert value > 99 and value < 600, f"value of {name} must be a valid HTTP status code: {value}"
        self.__dict__[name] = value


@dataclass
class APIRequestDTO:
    method: str
    url: str
    headers: Dict
    body: Dict
    metadata: Dict
    session: requests.Session
    response: APIResponseDTO
    object_type: Union[None, str] = None
    object_id: Union[None, str] = None

    def __setattr__(self, name, value):
        if name == 'method':
            assert re.match(r'(GET|POST|PUT|PATCH|OPTIONS|DELETE)', value, flags=re.IGNORECASE), \
                f"value of {name} must be a valid HTTP verb: {value}"
        self.__dict__[name] = value


def _inside_test():
    from django.conf import settings
    return settings.TESTING


def _register_mocked_routes(adapter):
    adapter.register_uri(requests_mock.ANY, 'https://loyalty.yotpo.com/api/v2/customers', json={
        'referral_code': {
            'code': 'RANDNUM',
        }
    })

    adapter.register_uri(requests_mock.POST, 'https://app.brightback.com/precancel', json={
        'valid': True,
        'url': 'https://brightback.com/fake_session'
    })


def _send_request(session: requests.Session, method: str, request_url: str, body=None):
    if body:
        api_response = getattr(session, method)(request_url, json=body)
    else:
        api_response = getattr(session, method)(request_url)

    return api_response


def make_api_request(
    url: str,
    method: str = 'get',
    headers: Dict = {},
    body: Dict = {},
    options: Dict = {},
    metadata: Dict = {},
    object_type: Union[str, None] = None,
    object_id: Union[str, None] = None
):
    session = requests.Session()
    session.headers.update(headers)
    request_url = furl(url).add(options).url

    if _inside_test():
        with requests_mock.Mocker(real_http=False) as adapter:
            _register_mocked_routes(adapter)
            api_response = _send_request(session, method, request_url, body)
    else:
        api_response = _send_request(session, method, request_url, body)

    response_body = api_response.content if api_response.content else '{}'
    api_response_object = APIResponseDTO(
        status_code=api_response.status_code,
        headers=api_response.headers,
        raw_body=response_body,
        parsed_body=json.loads(response_body)
    )
    api_request_object = APIRequestDTO(
        method=method,
        url=request_url,
        headers=headers,
        body=body,
        metadata=metadata,
        session=session,
        response=api_response_object,
        object_type=object_type,
        object_id=object_id,
    )
    return api_request_object


def make_logged_api_request(**kwargs):
    api_request = make_api_request(
        url=kwargs.get('url'),
        method=kwargs.get('method', 'get'),
        headers=kwargs.get('headers', {}),
        options=kwargs.get('options', {}),
        body=kwargs.get('body', {}),
        object_type=kwargs.get('object_type', None),
        object_id=kwargs.get('object_id', None),
    )
    APIRequestLog = apps.get_model('core', 'APIRequestLog')
    APIRequestLog.objects.create_from_logged_request(api_request)
    return api_request
