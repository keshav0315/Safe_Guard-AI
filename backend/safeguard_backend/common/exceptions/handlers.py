# Centralized exception handling - consistent error responses

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    DRF ka exception handler override karna.
    Consistent error format return karna sab endpoints se.
    """
    # Pehle DRF ka default handler call karo
    response = exception_handler(exc, context)

    if response is not None:
        # Error response format standardize karo
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': _extract_message(response.data),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
            }
        }
        response.data = custom_response_data
    else:
        # Unhandled exception - 500 return karo, but sensitive info mat dikhao
        logger.exception(f'Unhandled exception in {context.get("view", "unknown")}')
        response = Response(
            {
                'success': False,
                'error': {
                    'code': 500,
                    'message': 'An internal server error occurred.',
                    'details': {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response

def _extract_message(data):
    """Error data se human-readable message nikalna"""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        # Pehla error message le lo
        for key, value in data.items():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    return 'Request failed.'
