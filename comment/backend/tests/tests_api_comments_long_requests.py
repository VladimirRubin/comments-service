from django.test import override_settings, TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from backend.factories import PageFactory, PageCommentFactory, UserFactory


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class APILongRequestsCommentsTestCase(TestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_get_comments_tree_for_page(self):
        page = PageFactory()

        root1 = PageCommentFactory.create_batch(10, root=page)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-list'), {
            'content_type': 10,
            'object_id': page.id,
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 60)
        self.assertTrue(all(map(lambda c: 'ancestors' in c, res.data['result'])), 'Can not build tree structure')

    def test_get_comments_tree_for_depth_comment(self):
        page = PageFactory()

        root1 = PageCommentFactory.create_batch(10, root=page)
        comment_for_get_tree = None
        for root in root1:
            parent = root
            for i, _ in enumerate(range(5)):
                parent = PageCommentFactory(parent=parent)
                if i == 0:
                    comment_for_get_tree = parent

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-list'), {
            'parent': comment_for_get_tree.id
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 4)
        self.assertTrue(all(map(lambda c: 'ancestors' in c, res.data['result'])), 'Can not build tree structure')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_get_comments_history_for_user(self):
        user = UserFactory()

        root1 = PageCommentFactory.create_batch(10, user=user)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-list'), {
            'user': user.id
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 10)
        self.assertTrue(all(map(lambda c: c['user'] == user.id, res.data['result'])),
                        'Result comments not just for expected user')

    def test_get_comments_history_for_unavailable_user(self):
        root1 = PageCommentFactory.create_batch(10)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        user = UserFactory()
        res = self.client.get(reverse('comment-list'), {
            'user': user.id
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 0)

    def test_get_comments_history_with_date_filer_gte(self):
        user = UserFactory()

        root1 = PageCommentFactory.create_batch(10, user=user)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-list'), {
            'user': user.id,
            'created_gte': '2017-08-20'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 10)

    def test_get_comments_history_with_date_filer_gte(self):
        user = UserFactory()

        root1 = PageCommentFactory.create_batch(10, user=user)
        for root in root1:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        root2 = PageCommentFactory.create_batch(10)
        for root in root2:
            parent = root
            for _ in range(5):
                parent = PageCommentFactory(parent=parent)

        res = self.client.get(reverse('comment-list'), {
            'user': user.id,
            'created_lte': '2017-08-20'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue('task_id' in res.data)
        self.assertEqual(res.data['status'], 'SUCCESS')
        self.assertEqual(len(res.data['result']), 0)
