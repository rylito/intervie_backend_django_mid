from django.shortcuts import render
from django.http import Http404

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


# NOTE: I've offered 2 solutions below demonstrating the trade-off between code
# simplicity and database hits. Both views return the same results except in the
# cases of an Order object that has no related tags and a non-existent Order Id


# Requires 2 DB hits, but benefits from built-in error handling if
# order with given id doesn't exist making the code less verbose and results more
# explicit. This approach CAN differentiate between an order not existing and one
# that exists but has no related tags.
class OrderTagForOrderListViewApproach1(generics.GenericAPIView):

    # Slight optimization: only need 1 field on Order since we're only checking
    # if it exists, and we can prefetch the M2M field, although in this case
    # it results in 2 DB hits either way. We cannot use .select_related()
    # here since tags is a M2M relationship.
    queryset = Order.objects.only('pk').prefetch_related('tags')

    serializer_class = OrderTagSerializer
    lookup_url_kwarg = 'id'

    def get(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.serializer_class(instance.tags.all(), many=True)
        return Response(serializer.data, status=200)


# Requires only 1 DB hit, but need to implement a custom get_queryset() method.
# A disadvantage to this approach is it CANNOT differentiate between an Order
# object not existing, or 1 that exists but has no related tags without an
# additional DB hit.
class OrderTagForOrderListViewApproach2(generics.GenericAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer
    lookup_url_kwarg = 'id'
    lookup_field = 'orders'

    def get(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()

        # I've added this query_param to demonstrate 2 different behaviors of this
        # approach:
        #
        # tags_required=True: Orders are required to have tags. An empty queryset
        #                     will be treated as an invalid Order ID and raise a 404
        #
        # tags_required=False: Orders can have 0 tags and the view will return
        #                      empty lists. The tradeoff is that invalid order
        #                      IDs will also return empty lists rather than
        #                      a 404. In some cases, this might be acceptable
        #                      or preferable rather than raising an error/exception
        #                      (i.e. like the .get() method on python dicts).

        tags_required = request.query_params.get('tags_required', '').lower() in ('1', 'true')

        if tags_required and not queryset:
            raise Http404()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def get_queryset(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        # We could just hardcode the lookup_field here, but doing it this
        # way preserves the behavior of the generic view, and allows for
        # easier editing in the future since the attributes can be changed
        # on the class instead of having to search the code for 'magic'
        # hard-coded values
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        queryset = super().get_queryset().filter(**filter_kwargs)

        return queryset
