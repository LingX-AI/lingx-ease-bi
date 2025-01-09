from rest_framework.response import Response
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class UnifiedResponseJsonRender(CamelCaseJSONRenderer):
    """
    Unified JSON renderer for standardized response format
    :return {
        "code": 0,
        "msg": "success", 
        "data": { ... }
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not renderer_context:
            return super().render(data, accepted_media_type, renderer_context)
        response = renderer_context.get('response', None)
        if not isinstance(response, Response):
            return super().render(data, accepted_media_type, renderer_context)
        # Set message based on status code, default to 'success' or 'error'
        if 200 <= response.status_code < 300:
            code = 0
            msg = 'success'
        else:
            code = 1
            msg = response.status_text or 'error'
        # Use code/msg from original data if present
        if isinstance(data, dict):
            msg = data.get('msg', msg)
            code = data.get('code', code)

        # Set new response format
        new_data = {
            'code': code,
            'msg': msg,
            'data': None if code else data,
        }
        return super().render(new_data, accepted_media_type, renderer_context)
