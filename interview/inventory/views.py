import pytz
import datetime

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from interview.inventory.models import Inventory, InventoryLanguage, InventoryTag, InventoryType
from interview.inventory.schemas import InventoryMetaData
from interview.inventory.serializers import InventoryLanguageSerializer, InventorySerializer, InventoryTagSerializer, InventoryTypeSerializer


class InventoryListCreateView(APIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            metadata = InventoryMetaData(**request.data['metadata'])
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        
        request.data['metadata'] = metadata.dict()
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=201)
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        after_date = request.query_params.get('after_date')

        timestamp = None

        if after_date:
            try:
                timestamp = datetime.datetime.strptime(after_date, '%Y-%m-%d')
            except ValueError:
                # If I had more time, I'd implement better error handling, but
                # for the sake of this exercise, just ignore values that don't parse to a date
                pass
            else:
                # make aware, assume utc to avoid DB warning
                timestamp = timestamp.replace(tzinfo=pytz.timezone('utc'))

        serializer = self.serializer_class(self.get_queryset(timestamp), many=True)

        return Response(serializer.data, status=200)

    def get_queryset(self, after_date=None):
        filter_args = {}

        if after_date is not None:
            filter_args = {'created_at__gt': after_date}

        return self.queryset.filter(**filter_args)


class InventoryRetrieveUpdateDestroyView(APIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory)
        
        return Response(serializer.data, status=200)
    
    def patch(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=200)
    
    def delete(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        inventory.delete()
        
        return Response(status=204)
    
    def get_queryset(self, **kwargs):
        return self.queryset.get(**kwargs)


class InventoryTagListCreateView(APIView):
    queryset = InventoryTag.objects.all()
    serializer_class = InventoryTagSerializer
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=201)
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(self.get_queryset(), many=True)
        
        return Response(serializer.data, status=200)
    
    def get_queryset(self):
        return self.queryset.all()


class InventoryTagRetrieveUpdateDestroyView(APIView):
    queryset = InventoryTag.objects.all()
    serializer_class = InventoryTagSerializer
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        inventory_tag = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory_tag)
        
        return Response(serializer.data, status=200)
    
    def patch(self, request: Request, *args, **kwargs) -> Response:
        inventory_tag = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory_tag, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=200)
    
    def delete(self, request: Request, *args, **kwargs) -> Response:
        inventory_tag = self.get_queryset(id=kwargs['id'])
        inventory_tag.delete()
        
        return Response(status=204)

    def get_queryset(self, **kwargs):
        return self.queryset.get(**kwargs)


class InventoryLanguageListCreateView(APIView):
    queryset = InventoryLanguage.objects.all()
    serializer_class = InventoryLanguageSerializer
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=201)
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(self.get_queryset(), many=True)
        
        return Response(serializer.data, status=200)
    
    def get_queryset(self):
        return self.queryset.all()


class InventoryLanguageRetrieveUpdateDestroyView(APIView):
    queryset = InventoryLanguage.objects.all()
    serializer_class = InventoryLanguageSerializer
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory)
        
        return Response(serializer.data, status=200)
    
    def patch(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=200)
    
    def delete(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        inventory.delete()
        
        return Response(status=204)
    
    def get_queryset(self, **kwargs):
        return self.queryset.get(**kwargs)
    

class InventoryTypeListCreateView(APIView):
    queryset = InventoryType.objects.all()
    serializer_class = InventoryTypeSerializer
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=201)
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(self.get_queryset(), many=True)
        
        return Response(serializer.data, status=200)
    
    def get_queryset(self):
        return self.queryset.all()


class InventoryTypeRetrieveUpdateDestroyView(APIView):
    queryset = InventoryType.objects.all()
    serializer_class = InventoryTypeSerializer
    
    def get(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory)
        
        return Response(serializer.data, status=200)
    
    def patch(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        serializer = self.serializer_class(inventory, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response(serializer.data, status=200)
    
    def delete(self, request: Request, *args, **kwargs) -> Response:
        inventory = self.get_queryset(id=kwargs['id'])
        inventory.delete()
        
        return Response(status=204)
    
    def get_queryset(self, **kwargs):
        return self.queryset.get(**kwargs)
