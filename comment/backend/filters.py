import django_filters
from rest_framework import filters

from .models import Comment


class CommentFilter(filters.FilterSet):
    created_gte = django_filters.DateTimeFilter(name='created',
                                                lookup_expr='gte')
    created_lte = django_filters.DateTimeFilter(name='created',
                                                lookup_expr='lte')

    class Meta:
        model = Comment
        fields = ('level', 'user', 'created_gte', 'created_lte',)


class CommentHistoryFilter(filters.FilterSet):
    from_date = django_filters.DateTimeFilter(name='history_date',
                                              lookup_expr='gte')
    to_date = django_filters.DateTimeFilter(name='history_date',
                                            lookup_expr='lte')

    class Meta:
        model = Comment.history.model
        fields = ('id', 'from_date', 'to_date', 'history_type',
                  'history_user_id')
