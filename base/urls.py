from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("privacy/", views.Privacy.as_view(), name="privacy"),
    path("terms/", views.Terms.as_view(), name="terms"),
    path("consult/", views.Consult.as_view(), name="consult"),
    path("requests-list/", views.RequestsList.as_view(), name="requests_list"),
    path(
        "unknown-requests-list/",
        views.UnknownRequestsList.as_view(),
        name="unknown_requests_list",
    ),
    path("history/", views.RequestsHistory.as_view(), name="requests_history"),
    path("request/<str:id>/", views.RequestDetails.as_view(), name="request_details"),
    path(
        "whatsapp_reply/<str:id>/<str:number>/<str:device>/",
        views.WhatsappReply.as_view(),
        name="whatsapp_reply",
    ),
    path("direct_reply/<str:id>/", views.DirectReply.as_view(), name="direct_reply"),
    path("request/delete/<str:id>/", views.RequestDelete.as_view(), name="delete_request"),
    path("rules/", views.Rules.as_view(), name="rules"),
]
