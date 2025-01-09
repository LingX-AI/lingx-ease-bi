from django_filters import rest_framework as filters


class BaseFilter(filters.FilterSet):

    class Meta:
        exclude = [
            "is_deleted",
            "created_at",
        ]
