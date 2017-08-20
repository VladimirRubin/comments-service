from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import BlogArticle, Page, Comment


class BlogArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogArticle
        fields = ('id', 'title')


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'title')


class CommentHistorySerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    def get_reason(self, obj):
        if obj.history_type == '+':
            return 'Created'
        elif obj.history_type == '-':
            return 'Deleted'
        elif obj.history_type == '~':
            return 'Modified'
        return obj.history_type

    class Meta:
        model = Comment.history.model
        fields = ('id', 'history_user_id', 'history_date', 'reason', 'text')


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True, required=False)
    ancestors = serializers.ListField(child=serializers.IntegerField(), read_only=True)

    def validate(self, data):
        user_id = int(data.get('user_id', 0))
        if user_id:
            if not get_user_model().objects.filter(id=user_id).exist():
                raise serializers.ValidationError('This field must be valid user id.')
        return data

    class Meta:
        model = Comment
        fields = ('__all__')
