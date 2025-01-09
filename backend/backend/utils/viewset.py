from rest_framework import status, viewsets
from rest_framework.response import Response


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet
    """

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to implement soft delete
        :param request: HTTP request
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: Response with success code
        """
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"code": 0}, status=status.HTTP_200_OK)


class BaseUndeletedModelViewSet(BaseModelViewSet):
    """
    Base ViewSet with global filter for undeleted records
    """

    def get_queryset(self):
        """
        Returns a queryset containing only undeleted records
        """
        return super().get_queryset().filter(is_deleted=False)


class BaseNotDisabledModelViewSet(BaseModelViewSet):
    """
    Base ViewSet with global filter for enabled records
    """

    def get_queryset(self):
        """
        Returns a queryset containing only enabled and undeleted records
        """
        return (
            super()
            .get_queryset()
            .filter(
                is_deleted=False,
                is_enabled=True,
            )
        )
