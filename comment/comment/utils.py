from random import randint

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Count
from faker import Factory

fake = Factory.create()
USER_MODEL = get_user_model()


def get_sql(qs):
    sql, params = qs.query.sql_with_params()
    with connection.cursor() as cursor:
        cursor.execute('EXPLAIN ' + sql, params)
        last_query = cursor.db.ops.last_executed_query(cursor, sql, params)
        return last_query.replace('EXPLAIN ', '')


def get_random_instance(qs):
    count = qs.aggregate(ids=Count('id'))['ids']
    random_index = randint(0, count - 1)
    return qs.all()[random_index]


def create_dummy_user():
    username = fake.user_name()
    while USER_MODEL.objects.filter(username=username).exists():
        username = fake.user_name()
    user = USER_MODEL.objects.create_user(username,
                                          email=fake.email(),
                                          password=fake.password(8))
    return user


def create_dummy_article():
    user = get_random_instance(USER_MODEL.objects.filter(is_staff=False))
    BlogArticle = django_apps.get_model('backend', 'BlogArticle')
    article = BlogArticle.objects.create(user=user,
                                         title=fake.text())
    return article


def create_dummy_page():
    user = get_random_instance(USER_MODEL.objects.filter(is_staff=False))
    Page = django_apps.get_model('backend', 'Page')
    page = Page.objects.create(user=user,
                               title=fake.text())
    return page


def create_dummy_user_list(count):
    for i in range(count):
        create_dummy_user()


def create_dummy_article_list(count):
    for i in range(count):
        create_dummy_article()


def create_dummy_page_list(count):
    for i in range(count):
        create_dummy_page()


def create_dummy_root_comment(instance):
    user = get_random_instance(USER_MODEL.objects.filter(is_staff=False))
    Comment = django_apps.get_model('backend', 'Comment')
    if isinstance(instance, Comment):
        raise TypeError('instance object must be one of'
                        'the next types: (BlogArticle, Page)')
    root_comment = Comment.objects.create(user=user,
                                          root=instance,
                                          text=fake.text())
    return root_comment


def create_dummy_nested_comment(parent):
    user = get_random_instance(USER_MODEL.objects.filter(is_staff=False))
    Comment = django_apps.get_model('backend', 'Comment')
    if not isinstance(parent, Comment):
        raise TypeError('parent object must be Comment')
    nested_comment = Comment.objects.create(user=user,
                                            parent=parent,
                                            text=fake.text())
    return nested_comment


def create_dummy_comment_list():
    Page = django_apps.get_model('backend', 'Page')
    BlogArticle = django_apps.get_model('backend', 'BlogArticle')
    article_root_comments = []
    page_root_comments = []

    for i in range(20000):
        article = get_random_instance(BlogArticle.objects.all())
        article_comment = create_dummy_root_comment(article)
        article_root_comments.append(article_comment)

        page = get_random_instance(Page.objects.all())
        page_comment = create_dummy_root_comment(page)
        page_root_comments.append(page_comment)

        for root_comment in article_root_comments:
            comment = root_comment
            for _ in range(120):
                comment = create_dummy_nested_comment(comment)

        for root_comment in page_root_comments:
            comment = root_comment
            for _ in range(120):
                comment = create_dummy_nested_comment(comment)
