import json
import logging

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class JsonErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.exception("Unhandled exception in %s %s", request.method, request.path)
            body = json.dumps({"error": f"Internal server error: {e}"})
            response = HttpResponse(
                body,
                status=500,
                content_type="application/json",
            )
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response
