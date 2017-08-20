from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework_xml.renderers import XMLRenderer


def get_renderer_class(format_suffix='xml'):
    if format_suffix == 'xml':
        return XMLRenderer
    elif format_suffix == 'json':
        return JSONRenderer
    return BaseRenderer
