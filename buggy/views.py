from django.views.generic import DetailView, ListView

from buggy.models import Bug


class BugListView(ListView):
    model = Bug

bug_list = BugListView.as_view()


class BugDetailView(DetailView):
    queryset = Bug.objects.prefetch_related('comments')

bug_detail = BugDetailView.as_view()
