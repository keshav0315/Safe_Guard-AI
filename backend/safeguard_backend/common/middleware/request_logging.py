# Request logging middleware - important requests track karna

import logging
import time
import uuid

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Har request ko log karna.
    Sensitive paths ko skip karna (auth tokens etc.)
    """
    SKIP_LOGGING_PATHS = ['/api/v1/health/', '/static/', '/media/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Request ID generate karo tracking ke liye
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        # Sensitive paths skip karo
        should_log = not any(request.path.startswith(p) for p in self.SKIP_LOGGING_PATHS)

        start_time = time.time()

        if should_log:
            logger.info(
                f'[{request_id}] {request.method} {request.path} '
                f'user={getattr(request.user, "id", "anonymous") if hasattr(request, "user") else "unknown"}'
            )

        response = self.get_response(request)

        if should_log:
            duration = (time.time() - start_time) * 1000
            logger.info(
                f'[{request_id}] {response.status_code} {request.method} {request.path} '
                f'{duration:.1f}ms'
            )

        return response
