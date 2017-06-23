"""Summary
"""
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, BaseRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
# from utils import swagger_tools
from .permissions import IsOwner, IsOwnerOrReadOnly
from api import models
from django.contrib.auth.models import User
from api import serializers
# from collections import OrderedDict

# Create your views here.

# from openapi_codec import OpenAPICodec


# class SwaggerRenderer(BaseRenderer):
#     media_type = 'application/openapi+json'
#     format = 'swagger'

#     def render(self, data, media_type=None, renderer_context=None):
#         codec = OpenAPICodec()
#         return codec.dump(data)


class IsReadOnly(permissions.BasePermission):
    """
    Custom permission to allow anyone to view schema.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True


# CBF
class ProcessList(GenericAPIView):
    """
    List all processes, or create a new process.

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        renderer_classes (TYPE): Description
        serializer_class (TYPE): Description
    """
    serializer_class = serializers.ProcessSerializer
    queryset = models.Process.objects.all()
    renderer_classes = (JSONRenderer,
                        BrowsableAPIRenderer,
                        OpenAPIRenderer,
                        SwaggerUIRenderer, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        """Summary

        Args:
            request (TYPE): Description
            format (None, optional): Description

        Returns:
            TYPE: Description
        """
        processes = models.Process.objects.all()
        serializer = serializers.ProcessSerializer(processes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Summary

        Args:
            request (TYPE): Description
            format (None, optional): Description

        Returns:
            TYPE: Description
        """
        serializer = serializers.ProcessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessDetail(GenericAPIView):
    """
    Retrieve, update or delete a process instance.

    Attributes:
        permission_classes (TYPE): Description
        renderer_classes (TYPE): Description
        serializer_class (TYPE): Description
    """
    serializer_class = serializers.ProcessSerializer
    renderer_classes = (JSONRenderer,
                        BrowsableAPIRenderer,
                        OpenAPIRenderer,
                        SwaggerUIRenderer, )
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_object(self, id):
        """Summary

        Args:
            id (TYPE): Description

        Returns:
            TYPE: Description

        Raises:
            Http404: Description
        """
        try:
            return models.Process.objects.get(id=id)
        except models.Process.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        """Summary

        Args:
            request (TYPE): Description
            id (TYPE): Description
            format (None, optional): Description

        Returns:
            TYPE: Description
        """
        process = self.get_object(id)
        serializer = serializers.ProcessSerializer(process)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """Summary

        Args:
            request (TYPE): Description
            id (TYPE): Description
            format (None, optional): Description

        Returns:
            TYPE: Description
        """
        process = self.get_object(id)
        serializer = serializers.ProcessSerializer(process, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """Summary

        Args:
            request (TYPE): Description
            id (TYPE): Description
            format (None, optional): Description

        Returns:
            TYPE: Description
        """
        process = self.get_object(id)
        process.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# FBV
# class MyOpenAPIRenderer(OpenAPIRenderer):
#     def get_customizations(self):
#         data = super(MyOpenAPIRenderer, self).get_customizations()
#         data['paths'] = custom_data['paths']
#         data['info'] = custom_data['info']
#         data['basePath'] = custom_data['basePath']
#         return data


@api_view()
@renderer_classes([SwaggerUIRenderer,
                   OpenAPIRenderer])
@permission_classes([IsReadOnly])
def swagger_schema_view(request):
    generator = SchemaGenerator(title='Rasterbucket API')
    return Response(generator.get_schema(request=request))


# https://stackoverflow.com/questions/43627748/django-rest-framework-how-to-enable-swagger-docs-for-function-based-views#
# Custom query params in swagger
# See https://github.com/hackoregon/emergency-response-backend/issues/21
# No way to document parameters
# See https://github.com/marcgibbons/django-rest-swagger/issues/549
# @swagger_tools.additional_schema(
#     OrderedDict([
#         ('input_data', {
#             'name': 'input_data',
#             'required': True,
#             'location': 'body',
#             'type': 'string',
#             'description': 'input_data',
#         }),
#         ('output_data', {
#             'name': 'output_data',
#             'required': False,
#             'location': 'body',
#             'type': 'string',
#             'description': 'output_data',
#         }),
#     ])
# )
# @api_view(['GET', 'POST'])
# @renderer_classes([JSONRenderer,
#                    BrowsableAPIRenderer,
#                    OpenAPIRenderer,
#                    SwaggerUIRenderer])
# @permission_classes((permissions.IsAuthenticated, IsOwner, ))
# def process_list(request):
#     """
#     Return the processed requests with input and output values
#     The user can submit a process by doing a POST request
#     """
#     if request.method == 'GET':
#         processes = models.Process.objects.all()
#         serializer = serializers.ProcessSerializer(processes, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = serializers.ProcessSerializer(data=request.data)
#         if serializer.is_valid():  # TODO add more validation
#         # see https://richardtier.com/2014/03/24/json-schema-validation-with-django-rest-framework/
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# @renderer_classes([JSONRenderer,
#                    BrowsableAPIRenderer,
#                    OpenAPIRenderer,
#                    SwaggerUIRenderer])
# @permission_classes((permissions.IsAuthenticated, IsOwner, ))
# def process_detail(request, id):
#     """
#     Return the process detail with input and output dictionaries.
#     """
#     process = get_object_or_404(models.Process, pk=id)

#     if request.method == 'GET':
#         serializer = serializers.ProcessSerializer(process)
#         return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = serializers.ProcessSerializer(process, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         process.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class RasterbucketCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new rasterbucket.

        Args:
            serializer (TYPE): Description
        """
        serializer.save(owner=self.request.user)


class RasterbucketDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE request
    view with Read, Update and Delete

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)


class RasterbucketServiceCreateView(generics.ListCreateAPIView):
    """Defines the rasterbucket service creation behavior

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.RasterbucketService.objects.all()
    serializer_class = serializers.RasterbucketServiceSerializer

    def perform_create(self, serializer):
        """
        Args:
            serializer (TYPE): Description
        """
        pk = self.kwargs.get('pk_bucket')
        rasterbucket = get_object_or_404(
            models.Rasterbucket,
            pk=pk,
            owner=self.request.user)
        serializer.save(
            rasterbucket=rasterbucket,
            owner=self.request.user)


class RasterbucketServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable rasterbucket service view
    with Read, Update and Delete

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.RasterbucketService
    serializer_class = serializers.RasterbucketServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
        `retrieve`, `destroy` actions

        Returns:
            TYPE: Description
        """
        return get_object_or_404(
            models.RasterbucketService,
            pk=self.kwargs.get('pk_service'))


class MapServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable map service view
    with Read, Update and Delete

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.BaseServiceModel
    serializer_class = serializers.MapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
        `retrieve`, `destroy` actions

        Returns:
            TYPE: Description
        """
        return get_object_or_404(
            models.BaseServiceModel,
            pk=self.kwargs.get('pk_map'))


class GEEMapServiceCreateView(generics.ListCreateAPIView):
    """Defines the GEE map service creation behavior

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.GEEMapService.objects.all()
    serializer_class = serializers.GEEMapServiceSerializer

    def perform_create(self, serializer):
        """
        Args:
            serializer (TYPE): Description
        """
        pk = self.kwargs.get('pk_service')
        rasterbucketservice = get_object_or_404(
            models.RasterbucketService,
            pk=pk,
            owner=self.request.user)
        serializer.save(
            rasterbucketservice=rasterbucketservice,
            owner=self.request.user)


class GEEMapServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable GEE map service view
    with Read, Update and Delete

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.GEEMapService
    serializer_class = serializers.GEEMapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
        `retrieve`, `destroy` actions

        Returns:
            TYPE: Description
        """
        return get_object_or_404(
            models.GEEMapService,
            pk=self.kwargs.get('pk_map'))


class TileMapServiceCreateView(generics.ListCreateAPIView):
    """Defines the Tile map service creation behavior

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.TileMapService.objects.all()
    serializer_class = serializers.TileMapServiceSerializer

    def perform_create(self, serializer):
        """
        Args:
            serializer (TYPE): Description
        """
        pk = self.kwargs.get('pk_service')
        rasterbucketservice = get_object_or_404(
            models.RasterbucketService,
            pk=pk,
            owner=self.request.user)
        serializer.save(
            rasterbucketservice=rasterbucketservice,
            owner=self.request.user)


class TileMapServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable Tile map service view
    with Read, Update and Delete

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = models.TileMapService
    serializer_class = serializers.TileMapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
        `retrieve`, `destroy` actions

        Returns:
            TYPE: Description
        """
        return get_object_or_404(
            models.TileMapService,
            pk=self.kwargs.get('pk_map'))


class UserView(generics.ListAPIView):
    """View to list the user queryset.

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """View to retrieve a user instance.

    Attributes:
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
