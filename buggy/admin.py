from django.contrib import admin

from buggy.models import Bug, Comment, Project


class ProjectAdmin(admin.ModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)


class CommentInline(admin.StackedInline):
    model = Comment


class BugAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to')
    inlines = [
        CommentInline,
    ]

admin.site.register(Bug, BugAdmin)
