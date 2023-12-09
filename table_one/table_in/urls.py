from django.urls import path, re_path
from . import views
from .views import StatusChange, CreateFields, UsersUpdate, UsersDelete, GeneratePdf, pdf_generate, list_category, CategoryUpdate, CategoryCreate, CategoryDelete
#
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path(r'pdf/', pdf_generate, name='pdf_url'),
    path(r'generate_pdf/', GeneratePdf.as_view(), name='generate_pdf'),
    path(r'create_fields/', CreateFields.as_view(), name='create_fields'),
    path(r'list_users/', views.list_users, name='list_users_url'),
    path(r'list_users/<int:pk>/edit/',
         UsersUpdate.as_view(), name='list_users_edit_url'),
    path(r'list_users/<int:pk>/delete/',
         UsersDelete.as_view(), name='users_delete_url'),
    path(r'status_change/', StatusChange.as_view(), name='status_change'),
    path(r'list_category/', views.list_category, name='list_category_url'),
    path(r'list_category/<int:pk>/edit/',
         CategoryUpdate.as_view(), name='list_category_edit_url'),
    path(r'list_category/<int:pk>/delete/',
         CategoryDelete.as_view(), name='category_delete_url'),
    path(r'create_category/', CategoryCreate.as_view(), name='create_category'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


