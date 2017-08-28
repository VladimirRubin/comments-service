from django.test import TestCase
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework_xml.renderers import XMLRenderer

from backend.renderer import get_renderer_class


class GetRendererTestCase(TestCase):
    def test_without_format(self):
        renderer = get_renderer_class()

        self.assertIs(renderer, XMLRenderer, renderer)

    def test_with_unsupported_format(self):
        renderer = get_renderer_class('unsupported_format')

        self.assertIs(renderer, BaseRenderer)

    def test_with_xml_format(self):
        renderer = get_renderer_class('xml')

        self.assertIs(renderer, XMLRenderer, renderer)

    def test_with_json_format(self):
        renderer = get_renderer_class('json')

        self.assertIs(renderer, JSONRenderer, renderer)
