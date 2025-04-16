from django.urls import path
from .views import landing_page, summary_page

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("summary", summary_page, name="Summary")
]