from __future__ import absolute_import, unicode_literals

from celery import task

from .models import Comment
from .renderer import get_renderer_class
from .serializers import CommentSerializer


@task()
def get_comments(query):
    qs = Comment.objects.raw(query)
    data = CommentSerializer(qs, many=True).data
    return data


@task(bind=True)
def create_import_file(self, query, format_suffix='xml'):
    renderer_class = get_renderer_class(format_suffix)
    renderer = renderer_class()
    qs = Comment.objects.raw(query)
    data = CommentSerializer(instance=qs, many=True).data
    filename = '{0}.{1}'.format(self.request.id, format_suffix)
    with open('/tmp/{0}'.format(filename), "w") as f:
        file_data = renderer.render(data)
        if hasattr(file_data, 'decode'):
            file_data = file_data.decode()
        f.write(file_data)
        return {
            'filename': filename,
            'media_type': renderer.media_type,
            'format': format_suffix
        }
