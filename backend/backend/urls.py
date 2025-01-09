from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from backend.apps.application import views as application_views
from backend.apps.authentication import views as authentication_views
from backend.apps.chat import views as chat_views


class NoSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super(NoSlashRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = NoSlashRouter()
router.register(r"auth", authentication_views.ChatAuthView, basename="chat_auth")
router.register(r"app", application_views.ApplicationViewSet, basename="app")
router.register(
    r"app_table", application_views.ApplicationTableViewSet, basename="app_table"
)
router.register(
    r"app_table_column",
    application_views.ApplicationTableColumnViewSet,
    basename="app_table_column",
)
router.register(
    r"app_document",
    application_views.ApplicationDatabaseDocumentViewSet,
    basename="app_document",
)
router.register(
    r"app_prompt", application_views.ApplicationPromptViewSet, basename="app_prompt"
)
router.register(
    r"fine_tuning_example",
    application_views.FineTuningExampleViewSet,
    basename="fine_tuning_example",
)
router.register(
    r"fine_tuning_model",
    application_views.FineTuningModelViewSet,
    basename="fine_tuning_model",
)
router.register(r"message", chat_views.MessageViewSet, basename="message")
router.register(
    r"application-suggested-questions",
    application_views.ApplicationSuggestedQuestionViewSet,
    basename="application-suggested-questions",
)

API_BASE = "api/v1/"

urlpatterns = (
    [
        path(f"{API_BASE}schema", SpectacularAPIView.as_view(), name="schema"),
        path(
            f"{API_BASE}schema/swagger-ui",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            f"{API_BASE}schema/redoc",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path(f"{API_BASE}admin/login/", authentication_views.login),
        path(
            f"{API_BASE}oauth/",
            include("oauth2_provider.urls", namespace="oauth2_provider"),
        ),
        path(f"{API_BASE}convert_model", application_views.convert_model),
        path(f"{API_BASE}deployment_model", application_views.deployment_model),
        path(f"{API_BASE}chat_stream", chat_views.chat_stream),
        path(f"{API_BASE}generate_chart", chat_views.generate_chart),
        path(f"{API_BASE}cancel_chat", chat_views.cancel_chat),
        path(API_BASE, include(router.urls)),
        path("admin", admin.site.urls),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
