import factory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory

from .models import Page, BlogArticle, Comment


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'user{0}'.format(n))


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    user = factory.SubFactory(UserFactory)
    title = factory.Faker('text')


class BlogArticleFactory(DjangoModelFactory):
    class Meta:
        model = BlogArticle

    user = factory.SubFactory(UserFactory)
    title = factory.Faker('text')


class BaseCommentFactory(DjangoModelFactory):
    class Meta:
        exclude = ['root']
        abstract = True

    user = factory.SubFactory(UserFactory)
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.root))
    object_id = factory.SelfAttribute('root.id')
    text = factory.Faker('text')


class PageCommentFactory(BaseCommentFactory):
    class Meta:
        model = Comment

    root = factory.SubFactory(PageFactory)


class BlogArticleCommentFactory(BaseCommentFactory):
    class Meta:
        model = Comment

    root = factory.SubFactory(BlogArticleFactory)
