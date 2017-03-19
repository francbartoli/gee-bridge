from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from .permissions import IsOwner
from api import models
from django.contrib.auth.models import User
from api import serializers

# Create your views here.


class RasterbucketCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api"""
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new rasterbucket."""
        serializer.save(owner=self.request.user)


class RasterbucketDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE request
        view with Read, Update and Delete"""
    queryset = models.Rasterbucket.objects.all()
    serializer_class = serializers.RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)


class RasterbucketServiceCreateView(generics.ListCreateAPIView):
    """Defines the rasterbucket service creation behavior"""
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.RasterbucketService.objects.all()
    serializer_class = serializers.RasterbucketServiceSerializer

    def perform_create(self, serializer):
        """"""
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
       with Read, Update and Delete"""
    queryset = models.RasterbucketService
    serializer_class = serializers.RasterbucketServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            models.RasterbucketService,
            pk=self.kwargs.get('pk_service'))


class MapServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable map service view
       with Read, Update and Delete"""
    queryset = models.BaseServiceModel
    serializer_class = serializers.MapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            models.BaseServiceModel,
            pk=self.kwargs.get('pk_map'))


class GEEMapServiceCreateView(generics.ListCreateAPIView):
    """Defines the GEE map service creation behavior"""
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.GEEMapService.objects.all()
    serializer_class = serializers.GEEMapServiceSerializer

    def perform_create(self, serializer):
        """"""
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
       with Read, Update and Delete"""
    queryset = models.GEEMapService
    serializer_class = serializers.GEEMapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            models.GEEMapService,
            pk=self.kwargs.get('pk_map'))


class TileMapServiceCreateView(generics.ListCreateAPIView):
    """Defines the Tile map service creation behavior"""
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = models.TileMapService.objects.all()
    serializer_class = serializers.TileMapServiceSerializer

    def perform_create(self, serializer):
        """"""
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
       with Read, Update and Delete"""
    queryset = models.TileMapService
    serializer_class = serializers.TileMapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            models.TileMapService,
            pk=self.kwargs.get('pk_map'))


class UserView(generics.ListAPIView):
    """View to list the user queryset."""
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """View to retrieve a user instance."""
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
