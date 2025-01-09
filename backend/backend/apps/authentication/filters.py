from django_filters import rest_framework as filters
from backend.apps.core.filters import BaseFilter

from .models import User


class UserFilter(BaseFilter):
    nickname = filters.CharFilter(field_name="nickname", lookup_expr="icontains")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    mobile = filters.CharFilter(field_name="mobile", lookup_expr="icontains")

    class Meta:
        model = User
        exclude = BaseFilter.Meta.exclude + []
