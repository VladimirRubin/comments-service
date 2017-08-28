from random import choice

from django.db import ProgrammingError
from django.test import TestCase, override_settings

from backend.factories import PageCommentFactory, PageFactory
from backend.models import Comment
from backend.serializers import CommentSerializer
from backend.tasks import get_comments


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class GetCommentsTaskTestCase(TestCase):
    def test_without_query_param(self):
        with self.assertRaises(TypeError):
            get_comments()

    def test_with_invalid_sql_query(self):
        with self.assertRaises(ProgrammingError):
            get_comments('What the string is this???')

    def test_with_valid_query_simple_query(self):
        root1 = PageCommentFactory()
        children1 = PageCommentFactory(parent=root1)
        children11 = PageCommentFactory(parent=children1)
        children111 = PageCommentFactory(parent=children11)

        root2 = PageCommentFactory()
        children2 = PageCommentFactory(parent=root2)

        query = 'SELECT "backend_comment"."id", "backend_comment"."user_id", "backend_comment"."created", "backend_comment"."content_type_id", "backend_comment"."object_id", "backend_comment"."parent_id", "backend_comment"."level", "backend_comment"."ancestors", "backend_comment"."text" FROM "backend_comment" ORDER BY "backend_comment"."level" ASC, "backend_comment"."created" DESC'
        expected_qs_orm_analog = Comment.objects.all()
        comments = get_comments(query)

        self.assertIsInstance(comments, list, comments)
        self.assertEqual(len(comments), 6)
        self.assertListEqual(comments, CommentSerializer(Comment.objects.raw(query), many=True).data, comments)
        self.assertListEqual(comments, CommentSerializer(expected_qs_orm_analog, many=True).data, comments)
        self.assertQuerysetEqual(Comment.objects.raw(query), [o.__repr__() for o in expected_qs_orm_analog[:]])
        self.assertQuerysetEqual(Comment.objects.raw(query),
                                 [root2.__repr__(),
                                  root1.__repr__(),
                                  children2.__repr__(),
                                  children1.__repr__(),
                                  children11.__repr__(),
                                  children111.__repr__()])

    def test_with_valid_query_root_level_only(self):
        page1 = PageFactory()

        root1 = PageCommentFactory(root=page1)
        children1 = PageCommentFactory(parent=root1)
        children11 = PageCommentFactory(parent=children1)
        children111 = PageCommentFactory(parent=children11)

        children2 = PageCommentFactory(parent=root1)

        roots3 = PageCommentFactory.create_batch(10, root=page1)

        query = 'SELECT "backend_comment"."id", "backend_comment"."user_id", "backend_comment"."created", "backend_comment"."content_type_id", "backend_comment"."object_id", "backend_comment"."parent_id", "backend_comment"."level", "backend_comment"."ancestors", "backend_comment"."text" FROM "backend_comment" WHERE ("backend_comment"."object_id" = {0} AND "backend_comment"."content_type_id" = 10 AND "backend_comment"."level" = 0) ORDER BY "backend_comment"."level" ASC, "backend_comment"."created" DESC'.format(
            page1.id)
        expected_qs_orm_analog = Comment.objects.filter(object_id=page1.id, content_type_id=10, level=0)
        comments = get_comments(query)

        self.assertIsInstance(comments, list, comments)
        self.assertEqual(len(comments), 11)
        self.assertListEqual(comments, CommentSerializer(Comment.objects.raw(query), many=True).data, comments)
        self.assertListEqual(comments, CommentSerializer(expected_qs_orm_analog, many=True).data, comments)
        self.assertQuerysetEqual(Comment.objects.raw(query), [o.__repr__() for o in expected_qs_orm_analog[:]])

    def test_with_valid_query_with_ancestors(self):
        page = PageFactory()

        root1 = PageCommentFactory(root=page)
        childrens1 = PageCommentFactory.create_batch(15, parent=root1)
        childrens11 = PageCommentFactory.create_batch(10, parent=choice(childrens1))
        childrens111 = PageCommentFactory.create_batch(5, parent=choice(childrens11))

        root2 = PageCommentFactory()
        children2 = PageCommentFactory.create_batch(10, parent=root2)
        children22 = PageCommentFactory.create_batch(5, parent=choice(children2))

        query = 'SELECT "backend_comment"."id", "backend_comment"."user_id", "backend_comment"."created", "backend_comment"."content_type_id", "backend_comment"."object_id", "backend_comment"."parent_id", "backend_comment"."level", "backend_comment"."ancestors", "backend_comment"."text" FROM "backend_comment" WHERE ("backend_comment"."object_id" = {0} AND "backend_comment"."content_type_id" = 10 AND "backend_comment"."ancestors" @> ARRAY[{1}]::integer[]) ORDER BY "backend_comment"."level" ASC, "backend_comment"."created" DESC'.format(
            page.id, root1.id)
        expected_qs_orm_analog = Comment.objects.filter(object_id=page.id, content_type_id=10,
                                                        ancestors__contains=[root1.id])
        comments = get_comments(query)

        self.assertIsInstance(comments, list, comments)
        self.assertEqual(len(comments), 30)
        self.assertListEqual(comments, CommentSerializer(Comment.objects.raw(query), many=True).data, comments)
        self.assertListEqual(comments, CommentSerializer(expected_qs_orm_analog, many=True).data, comments)
        self.assertQuerysetEqual(Comment.objects.raw(query), [o.__repr__() for o in expected_qs_orm_analog[:]])
