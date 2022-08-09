from django.urls import include, path
from rest_framework import routers

from gxp.quickstart.views import UserViewSet, GroupViewSet
from gxp.raids.views import RaidsViewSet
from gxp.raiders.views import AltsViewSet, RaidersViewSet
from gxp.experience.views import ExperienceEventsViewSet, ExperienceGainsViewSet, ExperienceLevelsViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

router.register(r'raids', RaidsViewSet)

router.register(r'alts', AltsViewSet)
router.register(r'raiders', RaidersViewSet)

router.register(r'experienceEvents', ExperienceEventsViewSet)
router.register(r'experienceGains', ExperienceGainsViewSet)
router.register(r'experienceLevels', ExperienceLevelsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]