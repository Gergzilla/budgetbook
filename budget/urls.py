from django.urls import path
from .views import landing_page, summary_page, editor_page, report_page

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("summary", summary_page, name="summary_page"),
    path("reports", report_page, name="reports"),
    path("editor", editor_page, name="editor_page")
]