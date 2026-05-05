from django.urls import path

from .views import MetaLecturaDetail, MetaLecturaListCreate, ProgresoMetasView

urlpatterns = [
    path("", MetaLecturaListCreate.as_view(), name="metas-list-create"),
    path("<int:pk>/", MetaLecturaDetail.as_view(), name="metas-detail"),
    path("progreso/", ProgresoMetasView.as_view(), name="metas-progreso"),
]
