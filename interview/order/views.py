from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer

# Create your views here.
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    

class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer


# For Challenge 6, I demonstrated 2 different approaches. This challenge is
# essentially the same thing - just the reverse relation. See my solution
# to challenge 6 for a more in-depth analysis. For this challenge, I'm just
# going to use this 1 approach rather than repeating all the work I did on
# challenge 6 demonstrating 2 approaches.


class OrdersForOrderTagListView(generics.GenericAPIView):
    queryset = OrderTag.objects.only('pk').prefetch_related('orders')
    serializer_class = OrderSerializer
    lookup_url_kwarg = 'id'

    def get(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.serializer_class(instance.orders.all(), many=True)
        return Response(serializer.data, status=200)
