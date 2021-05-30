from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addNewPage", views.createPage, name="newPage"),
    path("randomPage", views.randPage, name="randPage"),
    path("wiki/<str:entry>", views.content,name="content"),
    path("wiki/<str:entry1>/editPage", views.editPage, name="editPage")
    
]
