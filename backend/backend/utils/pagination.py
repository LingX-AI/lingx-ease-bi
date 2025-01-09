from django.db.models import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class UniversalPageNumberPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_query_param = "page"  # Name of the page query parameter, default is 'page'
    page_size_query_param = "page_size"  # Name of the page size query parameter
    max_page_size = 10000

    @staticmethod
    def generate_universal_pagination_response(queryset: QuerySet, viewset_instance):
        """
        Generate a unified pagination response
        :param queryset:
        :param viewset_instance:
        :return: Response
        """

        # Use the viewset's built-in paginator to paginate the queryset
        page = viewset_instance.paginate_queryset(queryset)

        if page is not None:
            # If the request is paginated, serialize the paginated data
            serializer = viewset_instance.get_serializer(page, many=True)
            return viewset_instance.get_paginated_response(serializer.data)

        # If the request is not paginated, serialize the original queryset
        serializer = viewset_instance.get_serializer(queryset, many=True)
        return Response(serializer.data)
