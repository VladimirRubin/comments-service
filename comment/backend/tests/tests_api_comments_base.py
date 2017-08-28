import json

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from backend.factories import UserFactory, BlogArticleFactory, BlogArticleCommentFactory


class APIBaseCommentTest(TestCase):
    def test_create_valid_root_comment(self):
        user = UserFactory()
        blog = BlogArticleFactory(user=user)

        res = self.client.post(reverse('comment-list'), {
            'user': user.id,
            'text': 'To Blog Article Comment',
            'object_id': blog.id,
            'content_type': 7
        })

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_root_comment(self):
        blog = BlogArticleFactory()

        res = self.client.post(reverse('comment-list'), {
            'text': 'To Blog Article Comment',
            'object_id': blog.id,
            'content_type': 7
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_root_level_comments_have_pagination(self):
        blog = BlogArticleFactory()

        res = self.client.get(reverse('comment-list'), {
            'content_type': 7,
            'object_id': blog.id,
            'level': 0
        })

        self.assertTrue('next' in res.data)
        self.assertTrue('previous' in res.data)
        self.assertTrue('count' in res.data)
        self.assertTrue('results' in res.data)

    def test_get_root_level_comments_for_blog_with_pagination_first_page(self):
        blog = BlogArticleFactory(id=3)

        root_blog_comments = BlogArticleCommentFactory.create_batch(15, root=blog)

        res = self.client.get(reverse('comment-list'), {
            'content_type': 7,
            'object_id': 3,
            'level': 0
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['next'], 'http://testserver/comments/?content_type=7&level=0&object_id=3&page=2')
        self.assertEqual(res.data['previous'], None)
        self.assertEqual(res.data['count'], 15)
        self.assertEqual(len(res.data['results']), 10)

    def test_get_root_level_comments_for_blog_with_pagination_second_page(self):
        blog = BlogArticleFactory(id=3)

        root_blog_comments = BlogArticleCommentFactory.create_batch(15, root=blog)

        res = self.client.get(reverse('comment-list'), {
            'content_type': 7,
            'object_id': 3,
            'level': 0,
            'page': 2
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['next'], None)
        self.assertEqual(res.data['previous'], 'http://testserver/comments/?content_type=7&level=0&object_id=3')
        self.assertEqual(res.data['count'], 15)
        self.assertEqual(len(res.data['results']), 5)

    def test_remove_comment_owner(self):
        root = BlogArticleCommentFactory()
        child1 = BlogArticleCommentFactory(parent=root)
        child11 = BlogArticleCommentFactory(parent=child1)

        res = self.client.delete(reverse('comment-detail', kwargs={'pk': child11.id}), data=json.dumps({
            'user_id': child11.user.id
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_comment_not_owner(self):
        comment = BlogArticleCommentFactory()

        user = UserFactory()
        res = self.client.delete(reverse('comment-detail', kwargs={'pk': comment.id}), data=json.dumps({
            'user_id': user.id
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_leaf_comment(self):
        root = BlogArticleCommentFactory()
        child1 = BlogArticleCommentFactory(parent=root)
        child11 = BlogArticleCommentFactory(parent=child1)

        res = self.client.delete(reverse('comment-detail', kwargs={'pk': child11.id}), data=json.dumps({
            'user_id': child11.user.id
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_not_leaf_comment(self):
        root = BlogArticleCommentFactory()
        child1 = BlogArticleCommentFactory(parent=root)
        child11 = BlogArticleCommentFactory(parent=child1)

        res = self.client.delete(reverse('comment-detail', kwargs={'pk': child1.id}), data=json.dumps({
            'user_id': child1.user.id
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_comment_owner(self):
        root = BlogArticleCommentFactory()

        res = self.client.patch(reverse('comment-detail', kwargs={'pk': root.id}), data=json.dumps({
            'user_id': root.user.id,
            'text': 'New Text'
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['text'], 'New Text')

    def test_edit_comment_not_owner(self):
        root = BlogArticleCommentFactory()
        user = UserFactory()

        res = self.client.patch(reverse('comment-detail', kwargs={'pk': root.id}), data=json.dumps({
            'user_id': user.id,
            'text': 'New Text'
        }), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
