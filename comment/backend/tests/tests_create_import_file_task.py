import json
import os
from unittest import mock

from django.test import TestCase, override_settings

from backend.factories import PageCommentFactory, PageFactory, UserFactory
from backend.tasks import create_import_file


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CreateImportFileTaskTestCase(TestCase):
    def setUp(self):
        super(CreateImportFileTaskTestCase, self).setUp()
        self.QUERY_WITH_LEVEL = 'SELECT "backend_comment"."id", "backend_comment"."user_id", "backend_comment"."created", "backend_comment"."content_type_id", "backend_comment"."object_id", "backend_comment"."parent_id", "backend_comment"."level", "backend_comment"."ancestors", "backend_comment"."text" FROM "backend_comment" WHERE "backend_comment"."level" = 0 ORDER BY "backend_comment"."level" ASC, "backend_comment"."created" DESC'
        self.QUERY_WITH_CONTENT_TYPE = 'SELECT "backend_comment"."id", "backend_comment"."user_id", "backend_comment"."created", "backend_comment"."content_type_id", "backend_comment"."object_id", "backend_comment"."parent_id", "backend_comment"."level", "backend_comment"."ancestors", "backend_comment"."text" FROM "backend_comment" WHERE ("backend_comment"."content_type_id" = {0} AND "backend_comment"."object_id" = {1}) ORDER BY "backend_comment"."level" ASC, "backend_comment"."created" DESC'

    @mock.patch('builtins.open')
    def test_return_is_dict_with_needed_fields(self, open):
        task = create_import_file.delay(self.QUERY_WITH_LEVEL)

        self.assertIsInstance(task.result, dict, task.result)
        self.assertTrue(all(map(lambda f: f in task.result, ('filename', 'media_type', 'format'))), task.result)

    @mock.patch('builtins.open')
    def test_return_correctly_filename(self, open):
        task = create_import_file.delay(self.QUERY_WITH_LEVEL)
        expected_filename = '{0}.xml'.format(task.id)

        self.assertEqual(task.result['filename'], expected_filename, task.result['filename'])
        open.assert_called_with('/tmp/{0}'.format(expected_filename), 'w')

    @mock.patch('builtins.open')
    def test_return_correctly_format_and_media_type_for_xml(self, open):
        expected_format = 'xml'
        expected_media_type = 'application/xml'

        task = create_import_file.delay(self.QUERY_WITH_LEVEL, 'xml')

        self.assertEqual(task.result['format'], expected_format, task.result['format'])
        self.assertEqual(task.result['media_type'], expected_media_type, task.result['media_type'])

    @mock.patch('builtins.open')
    def test_return_correctly_format_and_media_type_for_json(self, open):
        expected_format = 'json'
        expected_media_type = 'application/json'

        task = create_import_file.delay(self.QUERY_WITH_LEVEL, 'json')

        self.assertEqual(task.result['format'], expected_format, task.result['format'])
        self.assertEqual(task.result['media_type'], expected_media_type, task.result['media_type'])

    @mock.patch('builtins.open')
    def test_failed_with_unsupported_format(self, open):
        task = create_import_file.delay(self.QUERY_WITH_LEVEL, 'unsupported_format')
        self.assertIsInstance(task.result, NotImplementedError)

    def test_file_created(self):
        task = create_import_file.delay(self.QUERY_WITH_LEVEL)
        expected_filepath = '/tmp/{0}'.format(task.result['filename'])

        self.assertTrue(os.path.exists(expected_filepath), 'Path does not exist')
        self.assertTrue(os.path.isfile(expected_filepath), 'It is not a file')

        os.remove(expected_filepath)

    def test_xml_file_have_valid_data(self):
        user = UserFactory()
        page = PageFactory(user=user)

        root = PageCommentFactory(user=user, root=page)
        root_created_date = root.created.isoformat().replace('+00:00', 'Z')
        children1 = PageCommentFactory(user=user, parent=root)
        children1_created_date = children1.created.isoformat().replace('+00:00', 'Z')

        expected_xml = '''<?xml version="1.0" encoding="utf-8"?>\n<root><list-item><id>{root.id}</id><user_id>{root.user.id}</user_id><ancestors></ancestors><created>{root_created_date}</created><object_id>{page.id}</object_id><level>0</level><text>{root.text}</text><user>{root.user.id}</user><content_type>10</content_type><parent></parent></list-item><list-item><id>{children1.id}</id><user_id>{children1.user.id}</user_id><ancestors><list-item>{children1.parent.id}</list-item></ancestors><created>{children1_created_date}</created><object_id>{page.id}</object_id><level>1</level><text>{children1.text}</text><user>{children1.user.id}</user><content_type>10</content_type><parent>{children1.parent.id}</parent></list-item></root>'''.format(
            page=page, root=root, children1=children1, root_created_date=root_created_date,
            children1_created_date=children1_created_date)

        task = create_import_file.delay(self.QUERY_WITH_CONTENT_TYPE.format(10, page.id))
        filepath = '/tmp/{0}'.format(task.result['filename'])

        with open(filepath, 'r') as f:
            self.assertXMLEqual(f.read(), expected_xml)

        os.remove(filepath)

    def test_json_file_have_valid_data(self):
        user = UserFactory()
        page = PageFactory(user=user)

        root = PageCommentFactory(user=user, root=page)
        root_created_date = root.created.isoformat().replace('+00:00', 'Z')
        children1 = PageCommentFactory(user=user, parent=root)
        children1_created_date = children1.created.isoformat().replace('+00:00', 'Z')

        expected_data = [
            {
                'id': root.id,
                'user_id': root.user.id,
                'ancestors': [],
                'created': root_created_date,
                'object_id': root.root.id,
                'level': root.level,
                'text': root.text,
                'user': root.user.id,
                'content_type': 10,
                'parent': None
            },
            {
                'id': children1.id,
                'user_id': children1.user.id,
                'ancestors': [children1.parent.id],
                'created': children1_created_date,
                'object_id': children1.root.id,
                'level': children1.level,
                'text': children1.text,
                'user': children1.user.id,
                'content_type': 10,
                'parent': children1.parent.id
            }
        ]
        expected_json = json.dumps(expected_data)

        task = create_import_file.delay(self.QUERY_WITH_CONTENT_TYPE.format(10, page.id), 'json')
        filepath = '/tmp/{0}'.format(task.result['filename'])

        with open(filepath, 'r') as f:
            self.assertJSONEqual(f.read(), expected_json)

        os.remove(filepath)
