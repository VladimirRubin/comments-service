from copy import copy

from django.test import TestCase

from backend.factories import BlogArticleCommentFactory, PageCommentFactory


class CommentHistoryTestCase(TestCase):
    def test_check_created_comment_history_status(self):
        comment = BlogArticleCommentFactory()

        self.assertTrue(comment.history.exists(), comment)
        self.assertEqual(comment.history.count(), 1, comment)

        created_comment_history = comment.history.first()

        self.assertEqual(created_comment_history.id, comment.id, comment)
        self.assertEqual(created_comment_history.history_type, '+', comment)
        self.assertEqual(created_comment_history.history_user_id, comment.user.id, comment)

    def test_check_updated_comment_history_status(self):
        comment = BlogArticleCommentFactory()
        comment.text = 'New Comment Text'
        comment.save()

        self.assertTrue(comment.history.exists(), comment)
        self.assertEqual(comment.history.count(), 2, comment)

        updated_history_record = comment.history.first()

        self.assertEqual(updated_history_record.id, comment.id, comment)
        self.assertEqual(updated_history_record.history_type, '~', comment)
        self.assertEqual(updated_history_record.text, comment.text, comment)
        self.assertEqual(updated_history_record.history_user_id, comment.user.id, comment)

    def test_check_deleted_comment_history_status(self):
        comment = PageCommentFactory()
        initial_comment = copy(comment)

        comment.delete()

        self.assertTrue(initial_comment.history.exists(), comment)
        self.assertEqual(initial_comment.history.count(), 2, comment)

        deleted_history_record = initial_comment.history.first()

        self.assertEqual(deleted_history_record.id, initial_comment.id, initial_comment)
        self.assertEqual(deleted_history_record.history_type, '-', initial_comment)
        self.assertEqual(deleted_history_record.history_user_id, initial_comment.user.id, initial_comment)

    def test_count_history_records(self):
        comment = BlogArticleCommentFactory()

        comment.text = 'First changes'
        comment.save()

        comment.text = 'Second changes'
        comment.save()

        comment.text = 'Third changes'
        comment.save()

        self.assertEqual(comment.history.count(), 4)
