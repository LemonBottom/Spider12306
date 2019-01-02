# Create time:2018-12-29 23:44
# Author:Chen

from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path('12306/', views.main_view),
    path('12306/search_ajax/', views.search_ajax),
    # path('receiveSMS/', views.receive_SMS),
    path('12306/ticket_order/', views.ticket_order_view),
    path('12306/ticket_order_ajax/', views.ticket_order_ajax),
    path('12306/ticket_order/action/', views.order_action_ajax),
    path('12306/ticket_order/scramble/', views.scramble_ticket_ajax)
]