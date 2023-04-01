from  django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name="expanses"),
    path('add-expanses', views.add_expanses, name="expanses")
]