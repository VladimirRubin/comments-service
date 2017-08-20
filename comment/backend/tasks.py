from __future__ import absolute_import, unicode_literals
from celery import task

from .renderer import get_renderer_class
from .models import Comment
from .serializers import CommentSerializer


@task()
def get_comments(query):
    qs = Comment.objects.raw(query.replace('@> [', '@> ARRAY['))
    data = CommentSerializer(qs, many=True).data
    return data


@task(bind=True)
def create_import_file(self, query_params, format_suffix='xml'):
    renderer_class = get_renderer_class(format_suffix)
    renderer = renderer_class()
    qs = Comment.objects.filter(**query_params)
    data = CommentSerializer(instance=qs, many=True).data
    filename = "{0}.{1}".format(self.request.id, format_suffix)
    with open("/tmp/{0}".format(filename), "w") as f:
        file_data = renderer.render(data)
        f.write(file_data if not hasattr(file_data, 'decode') else file_data.decode())
        return {
            'filename': filename,
            'media_type': renderer.media_type,
            'format': format_suffix
        }
