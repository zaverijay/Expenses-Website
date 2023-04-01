from  django.urls import path
from . import views



urlpatterns = [
    path('index', views.index, name="expanses_index"),
    path('add-expanses', views.add_expanses, name="expanses")
]