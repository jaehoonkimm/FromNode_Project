from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'node'
urlpatterns = [
    # path('node_list/<int:file_Code>', views.CreateTree, name="node_list"),
    path('node_list/<int:file_Code>', views.node_list, name="node_list"),
    path('node_detail/<str:node_Code>', views.node_detail, name="node_detail"),
    path('create_node/',views.create_node, name='create_node'),
]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)