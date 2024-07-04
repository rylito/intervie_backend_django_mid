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


class DeactivateOrderView(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_url_kwarg = 'id'

    def patch(self, request: Request, *args, **kwargs) -> Response:

        # check to make sure object with the given id exists. If not, the generic view will return a 404
        order = self.get_object()

        Order.deactivate(order.pk)

        # need to refresh the object since .deactivate() operates on the model as a bulk operation
        # so that the correct updated is_active value is serialized
        order.refresh_from_db()

        serializer = self.serializer_class(order)

        return Response(serializer.data, status=200)
