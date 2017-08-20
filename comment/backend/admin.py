from django.contrib import admin

from .models import Page, BlogArticle, Comment


class PageModelAdmin(admin.ModelAdmin):
    pass


class BlogArticleModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(Page, PageModelAdmin)
admin.site.register(BlogArticle, BlogArticleModelAdmin)
admin.site.register(Comment)
