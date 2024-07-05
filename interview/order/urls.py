from django.urls import path
from interview.order.views import (OrderListCreateView, OrderTagListCreateView,
    OrdersForOrderTagListView)


urlpatterns = [
    path('tags/', OrderTagListCreateView.as_view(), name='order-tags-list'),
    path('tags/<int:id>/orders/', OrdersForOrderTagListView.as_view(), name='order-for-tags-list'),
    path('', OrderListCreateView.as_view(), name='order-list'),

]
