from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("home", views.home, name="home"),
    path("video_feed/", views.video_feed, name="video_feed"),
    path("latest_counts/", views.latest_counts, name="latest_counts"),  # new
    path("contact", views.contact_view, name="contact"),  
    path("about", views.about, name="about"),  
    path("history", views.history, name="history"),  
    path("faq", views.faq, name="faq"),  
    path("feedback", views.feedback, name="feedback"),  
    path("logout", views.logout_view, name="logout"),  
]
