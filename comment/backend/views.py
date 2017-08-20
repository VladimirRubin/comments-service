from celery.result import AsyncResult
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.viewsets import GenericViewSet

from backend.permissions import IsOwnerOrReadOnly, IsLeafNodeOrNotDelete
from backend.tasks import create_import_file, get_comments
from .filters import CommentFilter, CommentHistoryFilter
from .models import BlogArticle, Page, Comment
from .serializers import BlogArticleSerializer, PageSerializer, CommentSerializer, CommentHistorySerializer


class BlogArticleViewSet(viewsets.ModelViewSet):
    queryset = BlogArticle.objects.all()
    serializer_class = BlogArticleSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class CommentHistoryViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    queryset = Comment.history.all()
    serializer_class = CommentHistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentHistoryFilter


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsOwnerOrReadOnly, IsLeafNodeOrNotDelete,)
    filter_class = CommentFilter

    @list_route()
    def download(self, request, **kwargs):
        query_params = request.query_params.copy()
        task_id = query_params.pop('task_id', [None])[0]
        if task_id is None:
            task_id = create_import_file.delay(query_params, kwargs.get('format', 'xml')).id
            return Response({'task_id': task_id})
        task = AsyncResult(task_id)
        status = task.status
        result = task.result
        response = {
            'task_id': task_id,
            'status': status
        }
        if isinstance(result, Exception):
            response['error'] = str(result)
        else:
            try:
                file = open("/tmp/{0}".format(result['filename']))
            except:
                return Response(status=HTTP_403_FORBIDDEN)
            else:
                response = HttpResponse(file, content_type=result['media_type'])
                response['Content-Disposition'] = 'attachment; filename=%s' % result['filename']
                return response
        return Response(response)

    def list(self, request, *args, **kwargs):
        if 'level' in request.query_params:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        query_params = request.query_params.copy()
        task_id = query_params.pop('task_id', [None])[0]
        if task_id is None:
            queryset = self.filter_queryset(self.get_queryset())
            task_id = get_comments.delay(str(queryset.query)).id
            return Response({'task_id': task_id})
        task = AsyncResult(task_id)
        status = task.status
        result = task.result
        response = {
            'task_id': task_id,
            'status': status
        }
        if isinstance(result, Exception):
            response['error'] = str(result)
        else:
            response['result'] = result
        return Response(response)

    def get_queryset(self):
        qs = super(CommentViewSet, self).get_queryset()
        if 'level' not in self.request.query_params:
            if 'parent' in self.request.query_params:
                parent = self.request.query_params.get('parent')
                qs = qs.filter(ancestors__contains=[parent])
            elif 'object_id' in self.request.query_params:
                qs = qs.filter(object_id=self.request.query_params.get('object_id'))
        return qs

    def paginate_queryset(self, queryset):
        if 'level' not in self.request.query_params:
            return None
        return super(CommentViewSet, self).paginate_queryset(queryset)
