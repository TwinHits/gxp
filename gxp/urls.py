from django.urls import include, path
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from gxp.quickstart.views import UserViewSet, GroupViewSet
from gxp.raids.views import LogsViewSet, RaidsViewSet
from gxp.raiders.views import AliasesViewSet, RaidersViewSet, SpecialistRolesViewSet
from gxp.experience.views import (
    ExperienceEventsViewSet,
    ExperienceGainsViewSet,
    ExperienceLevelsViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)

router.register(r"raids", RaidsViewSet)
router.register(r"logs", LogsViewSet)

router.register(r"raiders", RaidersViewSet)
router.register(r"aliases", AliasesViewSet)
router.register(r"specialistroles", SpecialistRolesViewSet)

router.register(r"experienceEvents", ExperienceEventsViewSet)
router.register(r"experienceGains", ExperienceGainsViewSet)
router.register(r"experienceLevels", ExperienceLevelsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
