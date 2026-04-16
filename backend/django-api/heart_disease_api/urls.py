from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.utils import timezone


def health_check(_request):
    from django.conf import settings

    return JsonResponse(
        {
            "ok": True,
            "service": "heart-disease-api",
            "version": settings.SERVICE_VERSION,
            "time": timezone.localtime(timezone.now()).isoformat(),
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health_check),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/dashboard/", include("apps.analytics.urls_dashboard")),
    path("api/analysis/", include("apps.analytics.urls_analysis")),
    path("api/model/", include("apps.analytics.urls_model")),
    path("api/", include("apps.prediction.urls")),
    path("api/system/", include("apps.system.urls")),
]
