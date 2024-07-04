import datetime

from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from interview.order.models import Order, OrderTag
from interview.order.serializers import OrderSerializer, OrderTagSerializer

# Create your views here.
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # This implementation is modeled on the slice behavior in Python:
        #
        # The start value is INCLUSIVE and the end value is EXCLUSIVE.
        # An omitted start value selects a range beginning (and including) the 1st value of an iterable.
        # An omitted end value selects a range ending (and including) the last value of an iterable.
        # If both start and end values are omitted, all items in the iterable are returned.
        #
        # For example:
        #
        # '012345'[:] = '012345'
        # '012345'[:4] = '0123'
        # '012345'[2:] = '2345'
        # '012345'[2:4] = '23'
        #
        # This method mimics the same behavior depending on whether start_date and/or embargo date values
        # are passed as optional querystring parameters. This allows for flexible querying of date ranges.

        slice_model = []

        for param_name in ('start_date', 'embargo_date'):
            param_val = self.request.query_params.get(param_name)

            if param_val is not None:
                param_val = datetime.datetime.strptime(param_val, '%Y-%m-%d')

            slice_model.append(param_val)

        start_date, embargo_date = slice_model

        filter_args = {}

        if start_date is not None:
            filter_args['start_date__gte'] = start_date

        if embargo_date is not None:
            filter_args['embargo_date__lt'] = embargo_date

        return super().get_queryset().filter(**filter_args)

    def list(self, request, *args, **kwargs):
        # Since the get_queryset method returns a queryset and not a Response, catch any
        # value errors here and return a 400 rather than a 500
        try:
            return super().list(request, args, kwargs)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

class OrderTagListCreateView(generics.ListCreateAPIView):
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer
