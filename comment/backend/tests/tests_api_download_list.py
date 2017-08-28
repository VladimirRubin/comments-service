from django.test import override_settings, TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from backend.factories import UserFactory, PageCommentFactory


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class APIDownloadListCommentTestCase(TestCase):
    def test_get_file_for_user_without_date_filter(self):
        user = UserFactory()

        root1 = PageCommentFactory.create_batch(10, user=user)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-download'), {
            "user": user.id
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('content-type' in res._headers)
        self.assertEqual(res._headers['content-type'][1], 'application/xml')
        self.assertTrue('content-disposition' in res._headers)
        self.assertTrue('attachment; filename' in res._headers['content-disposition'][1])

    def test_get_file_for_user_with_date_filter(self):
        user = UserFactory()

        root1 = PageCommentFactory.create_batch(10, user=user)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-download'), {
            "user": user.id,
            "created_gte": '2017-08-26'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('content-type' in res._headers)
        self.assertEqual(res._headers['content-type'][1], 'application/xml')
        self.assertTrue('content-disposition' in res._headers)
        self.assertTrue('attachment; filename' in res._headers['content-disposition'][1])
