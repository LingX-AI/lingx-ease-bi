from django.db.models import Q
from django_filters import rest_framework as filters
from backend.apps.core.filters import BaseFilter

from .models import Message


class MessageFilter(BaseFilter):
    search = filters.CharFilter(method="filter_by_all_fields")
    question = filters.CharFilter(field_name="question", lookup_expr="icontains")
    created_date = filters.DateFromToRangeFilter(field_name="created_at", lookup_expr="date")

    class Meta:
        model = Message
        exclude = BaseFilter.Meta.exclude + [
            "received_sql_list",
            "valid_sql",
            "answer",
            "query_result",
            "completed_at",
            "step_times",
        ]

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(Q(question__icontains=value) | Q(answer__icontains=value))
