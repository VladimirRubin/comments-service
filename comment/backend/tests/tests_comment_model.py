from django.db import IntegrityError
from django.test import TestCase

from backend.factories import UserFactory, PageFactory, PageCommentFactory, BlogArticleFactory, \
    BlogArticleCommentFactory
from backend.models import Comment


class CommentTestCase(TestCase):
    def test_comment_with_user(self):
        user = UserFactory()
        page = PageFactory()

        comment = PageCommentFactory(user=user, root=page)

        self.assertEqual(comment.user, user, comment)

    def test_comment_without_user(self):
        page = PageFactory()

        with self.assertRaises(IntegrityError):
            Comment.objects.create(root=page)

    def test_all_comments_have_created_field(self):
        comments = PageCommentFactory.create_batch(10)

        passed = [hasattr(o, 'created') for o in comments]
        expected = [True for _ in range(10)]

        self.assertListEqual(passed, expected, 'All comments must have created field')

    def test_create_root_comment_for_page(self):
        user = UserFactory()
        page = PageFactory(user=user)

        root_page_comment = PageCommentFactory(user=user, root=page)

        self.assertEqual(root_page_comment.root, page, root_page_comment)
        self.assertEqual(root_page_comment.user, user, root_page_comment)
        self.assertEqual(root_page_comment.level, 0, root_page_comment)
        self.assertEqual(root_page_comment.ancestors, [], root_page_comment)
        self.assertTrue(root_page_comment.is_leaf_node, root_page_comment)

    def test_create_root_comment_for_blog_article(self):
        user = UserFactory()
        blog_article = BlogArticleFactory(user=user)

        root_blog_article_comment = BlogArticleCommentFactory(user=user, root=blog_article)

        self.assertEqual(root_blog_article_comment.root, blog_article, root_blog_article_comment)
        self.assertEqual(root_blog_article_comment.user, user, root_blog_article_comment)
        self.assertEqual(root_blog_article_comment.level, 0, root_blog_article_comment)
        self.assertEqual(root_blog_article_comment.ancestors, [], root_blog_article_comment)
        self.assertTrue(root_blog_article_comment.is_leaf_node, root_blog_article_comment)

    def test_tree_structure(self):
        page = PageFactory()

        root_page_comment = PageCommentFactory(root=page)

        children1 = PageCommentFactory(parent=root_page_comment)

        self.assertListEqual(children1.ancestors, [root_page_comment.id], children1)
        self.assertTrue(children1.is_leaf_node, children1)
        self.assertEqual(children1.level, 1, children1)
        self.assertEqual(children1.parent, root_page_comment, children1)
        self.assertEqual(children1.root, page, children1)

        children11 = PageCommentFactory(parent=children1)

        self.assertListEqual(children11.ancestors, [root_page_comment.id, children1.id], children11)
        self.assertFalse(children1.is_leaf_node, children1)
        self.assertEqual(children11.level, 2, children11)
        self.assertEqual(children11.parent, children1, children11)
        self.assertEqual(children11.root, page, children11)

        children111 = PageCommentFactory(parent=children11)

        self.assertListEqual(children111.ancestors, [root_page_comment.id, children1.id, children11.id], children111)
        self.assertFalse(children1.is_leaf_node, children1)
        self.assertFalse(children11.is_leaf_node, children11)
        self.assertTrue(children111.is_leaf_node, children111)
        self.assertEqual(children111.level, 3, children111)
        self.assertEqual(children111.parent, children11, children111)
        self.assertEqual(children111.root, page)

    def test_comment_with_root(self):
        blog_article = BlogArticleFactory()

        comment = BlogArticleCommentFactory(root=blog_article)
        self.assertEqual(comment.root, blog_article, comment)

    def test_comment_without_root_and_without_parent(self):
        user = UserFactory()

        with self.assertRaises(IntegrityError):
            Comment.objects.create(user=user)

    def test_comment_without_root_but_with_parent(self):
        user = UserFactory()
        page = PageFactory()

        root_comment = PageCommentFactory(root=page)

        comment = Comment.objects.create(user=user, parent=root_comment)
        self.assertTrue(hasattr(comment, 'root'), comment)
        self.assertEqual(comment.root, page, comment)

    def test_collision_comment_with_root_and_with_parent(self):
        user = UserFactory()
        page1 = PageFactory()
        page2 = PageFactory()

        root_comment = PageCommentFactory(root=page1)

        comment = PageCommentFactory(user=user, root=page2, parent=root_comment)

        self.assertEqual(comment.root, page1, comment)
        self.assertEqual(comment.parent, root_comment, comment)
        self.assertEqual(comment.root, comment.parent.root, comment)
