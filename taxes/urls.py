from django.urls import path
from .views import PreviewReturnView
urlpatterns = [ path("returns/preview/", PreviewReturnView.as_view(), name="returns-preview") ]
