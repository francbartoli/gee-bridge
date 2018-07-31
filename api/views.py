"""Summary of api views for Rasterbucket models
"""
from api import models, serializers
from gee_bridge.settings import DEBUG
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi as yasg_openapi
from drf_yasg.views import get_schema_view as yags_get_schema_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import (
    api_view, permission_classes, renderer_classes
)
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import (
    BaseRenderer, BrowsableAPIRenderer,
    JSONRenderer)
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework_yaml.renderers import YAMLRenderer

# from utils import swagger_tools
from .permissions import (
    IsOpen,
    IsOwner,
    IsOwnerOrReadOnly
)
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)


# Create your views here.

api_schema_view = yags_get_schema_view(
    yasg_openapi.Info(
        title="Rasterbucket API",
        default_version='v1',
        description="""
This is a project for a GEE bridge [gee-bridge](https://github.com/francbartoli/gee-bridge)
based on the Django Rest Framework library.
The `swagger-ui` view can be found [here](/api/v1/livedoc/swagger).
The `ReDoc` view can be found [here](/api/v1/livedoc/redoc).
The swagger YAML document can be found [here](/api/v1/livedoc/swagger.yaml).
""", # noqa
        terms_of_service="https://www.google.com/policies/terms/",
        contact=yasg_openapi.Contact(email="xbartolone@gmail.com"),
        license=yasg_openapi.License(name="GPLv3 License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(AllowAny,),
)


# CBF


class ProcessList(GenericAPIView):
    """
    List all processes, or create a new process.

    Methods
    -------
    get
        Return a list of all created processes.

    post
        Create a processing instance.
    """
    if not DEBUG:
        swagger_schema = None
    serializer_class = serializers.ProcessSerializer
    queryset = models.Process.objects.all()
    renderer_classes = (JSONRenderer,
                        YAMLRenderer,
                        BrowsableAPIRenderer,
                        OpenAPIRenderer,
                        SwaggerUIRenderer, )
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_description="List all created processes",
        responses={200: serializers.ProcessSerializer(many=True)},
        security=[None]
    )
    def get(self, request, format=None):
        """List all created processes.

        Parameters
        ----------
        request : Request
            HTTP GET request
        format : str, optional
            Format for the rendered response (the default is None)

        Returns
        -------
        Response
            Return the response with all serialized processes
        """

        processes = models.Process.objects.all()
        serializer = serializers.ProcessSerializer(processes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a processing instance",
        request_body=yasg_openapi.Schema(
            type=yasg_openapi.TYPE_OBJECT,
            required=['name', 'input_data', 'output_data'],
            properties={
                'name': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_STRING
                ),
                'input_data': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_OBJECT
                ),
                'output_data': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_OBJECT
                )
            },
        ),
        responses={
            201: serializers.ProcessSerializer(many=False),
            400: "Bad Request"
        },
        security=[None]
    )
    def post(self, request, format=None):
        """Create a processing instance.

        Parameters
        ----------
        request : Request
            HTTP POST request
        format : str, optional
            Format for the rendered response (the default is None)

        Returns
        -------
        Response
            Return the response with the created serialized process
        """

        serializer = serializers.ProcessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessDetail(GenericAPIView):
    """Retrieve, update or delete a created process instance.

    Methods
    -------
    get
        Return a serialized process.

    put
        Update a process instance.

    delete
        Delete a process instance.

    Raises
    ------
    Http404
        HTTP error if the process doesn't exist

    """

    serializer_class = serializers.ProcessSerializer
    renderer_classes = (JSONRenderer,
                        YAMLRenderer,
                        BrowsableAPIRenderer,
                        OpenAPIRenderer,
                        SwaggerUIRenderer, )
    permission_classes = (IsAuthenticated, )

    def get_object(self, id):
        """Get the process object.

        Parameters
        ----------
        id : str
            Identifier of the process
        Raises
        ------
        Http404
            Return HTTP 404 error code if the object doesn't exist

        Returns
        -------
        dict
            Dictionary of the query result
        """

        try:
            return models.Process.objects.get(id=id)
        except models.Process.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description="Obtain a process instance by its identifier",
        responses={
            200: serializers.ProcessSerializer(many=False),
            404: "Object doesn't exist"
        },
        security=[None]
    )
    def get(self, request, id, format=None):
        """Obtain a process instance.

        Parameters
        ----------
        request : Request
            HTTP GET request
        id : str
            Identifier of the process
        format : str, optional
            Format for the rendered response (the default is None)

        Returns
        -------
        Response
            Return the response with the serialized process
        """
        process = self.get_object(id)
        serializer = serializers.ProcessSerializer(process)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a process instance by its identifier",
        request_body=yasg_openapi.Schema(
            type=yasg_openapi.TYPE_OBJECT,
            required=['name', 'input_data', 'output_data'],
            properties={
                'name': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_STRING
                ),
                'input_data': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_OBJECT
                ),
                'output_data': yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_OBJECT
                )
            },
        ),
        responses={
            200: serializers.ProcessSerializer(many=False),
            404: "Object doesn't exist"
        },
        security=[None]
    )
    def put(self, request, id, format=None):
        """Update a process instance.

        Parameters
        ----------
        request : Request
            HTTP GET request
        id : str
            Identifier of the process
        format : str, optional
            Format for the rendered response (the default is None)

        Returns
        -------
        Response
            Return the response with the serialized process
        """
        process = self.get_object(id)
        serializer = serializers.ProcessSerializer(process, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a process instance by its identifier",
        responses={
            204: "Operation completed with no content",
            404: "Object doesn't exist"
        },
        security=[None]
    )
    def delete(self, request, id, format=None):
        """Delete a process instance.

        Parameters
        ----------
        request : Request
            HTTP GET request
        id : str
            Identifier of the process
        format : str, optional
            Format for the rendered response (the default is None)

        Returns
        -------
        Response
            Return the response with the result code of the deletion
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
@renderer_classes([
    SwaggerUIRenderer,
    OpenAPIRenderer
])
@permission_classes([IsOpen])
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
#         if serializer.is_valid():  # TODO add more validation id:8 gh:14
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
    if not DEBUG:
        swagger_schema = None
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (IsAuthenticated, IsOwner)

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
    if not DEBUG:
        swagger_schema = None
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (IsAuthenticated, IsOwner)


class RasterbucketServiceCreateView(generics.ListCreateAPIView):
    """Defines the rasterbucket service creation behavior

    Attributes:
        permission_classes (TYPE): Description
        queryset (TYPE): Description
        serializer_class (TYPE): Description
    """
    if not DEBUG:
        swagger_schema = None
    permission_classes = (IsAuthenticated, IsOwner)
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
    if not DEBUG:
        swagger_schema = None
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
    if not DEBUG:
        swagger_schema = None
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
    if not DEBUG:
        swagger_schema = None
    permission_classes = (IsAuthenticated, IsOwner)
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
    if not DEBUG:
        swagger_schema = None
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
    if not DEBUG:
        swagger_schema = None
    permission_classes = (IsAuthenticated, IsOwner)
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
    if not DEBUG:
        swagger_schema = None
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
