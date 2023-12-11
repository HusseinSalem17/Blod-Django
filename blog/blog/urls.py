from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("bookStore.urls")),
]

# to show the images in the admin page (means to show the images in the database)
# static function takes two parameters: the url and the root of the images
# (the root of the images is the media root in the settings.py file
# and the url is the media url in the settings.py file)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
