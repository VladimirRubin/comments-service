from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from backend.constants import COMMENT_UPDATED_REASON, \
    COMMENT_CREATED_REASON, COMMENT_DELETED_REASON


class Page(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_('Page Owner'),
                             related_name='pages')
    title = models.CharField(_('Page Title'), max_length=250)

    def __str__(self):
        return self.title


class BlogArticle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_('Article Owner'),
                             related_name='articles')
    title = models.CharField(_('Article Title'), max_length=250)

    def __str__(self):
        return self.title


class Comment(models.Model):
    class Meta:
        ordering = ('level', '-created')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_('Comment Owner'),
                             related_name='comments')
    created = models.DateTimeField(_('Comment created at'),
                                   editable=False,
                                   default=now)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to=models.Q(app_label='backend', model='page') | models.Q(
                                         app_label='backend', model='blogarticle'))
    object_id = models.PositiveIntegerField()
    root = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', verbose_name=_('Comment Parent'),
                               related_name='children', blank=True, null=True,
                               db_index=True)
    level = models.PositiveIntegerField(db_index=True, editable=False)
    ancestors = ArrayField(models.PositiveIntegerField(), db_index=True)
    text = models.TextField(_('Comment Text'))
    history = HistoricalRecords(
        excluded_fields=['user', 'created', 'content_type', 'object_id',
                         'root', 'parent', 'level'])

    @property
    def _history_user(self):
        return self.user

    @_history_user.setter
    def _history_user(self, value):
        self.user = value

    @property
    def is_leaf_node(self):
        return not bool(self.children.exists())

    def save(self, *args, **kwargs):
        reason = COMMENT_UPDATED_REASON
        if not self.id:
            reason = COMMENT_CREATED_REASON
            if self.parent:
                self.root = self.parent.root
                self.level = self.parent.level + 1
                self.ancestors = self.parent.ancestors + [self.parent_id]
            else:
                self.level = 0
                self.ancestors = []
        super(Comment, self).save(*args, **kwargs)
        # from .serializers import CommentSerializer
        # notification_comment(self.content_type, self.object_id,
        #                      CommentSerializer(instance=self, many=False).data.update({'reason': reason}))

    def delete(self, *args, **kwargs):
        notification_params = {
            'content_type': self.content_type,
            'object_id': self.object_id,
            'data': {
                'id': self.id,
                'reason': COMMENT_DELETED_REASON
            }
        }
        super(Comment, self).delete(*args, **kwargs)
        # notification_comment(**notification_params)

    def __str__(self):
        return '{0} | {1}'.format(self.user.username, self.text)
