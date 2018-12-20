"""Spider12306 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('12306/', view.main_view),
    path('search_ajax/', view.search_ajax),
    path('receiveSMS/', view.receive_SMS),
    path('ticket_order/', view.ticket_order_view),
    path('ticket_order_ajax/', view.ticket_order_ajax),
    path('order_action_ajax/', view.order_action_ajax),
    path('scramble_ticket_ajax/', view.scramble_ticket_ajax)
]
