from django.urls import path
from interview.order.views import (OrderListCreateView, OrderTagListCreateView,
    OrderTagForOrderListViewApproach1, OrderTagForOrderListViewApproach2)


urlpatterns = [
    path('tags/', OrderTagListCreateView.as_view(), name='order-tags-list'),

    # I've added 2 endpoints to demonstrate 2 different approaches (see views.py for addtl. comments)
    path('<int:id>/tags-1/', OrderTagForOrderListViewApproach1.as_view(), name='tags-for-order-list-approach-1'),
    path('<int:id>/tags-2/', OrderTagForOrderListViewApproach2.as_view(), name='tags-for-order-list-approach-2'),

    path('', OrderListCreateView.as_view(), name='order-list'),

]
