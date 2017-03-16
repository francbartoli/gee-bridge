from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from .permissions import IsOwner
from .models import Rasterbucket, RasterbucketService, GEEMapService
from django.contrib.auth.models import User
from .serializers import RasterbucketSerializer, RasterbucketServiceSerializer, UserSerializer, GEEMapServiceSerializer

# Create your views here.


class CreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api"""
    queryset = Rasterbucket.objects.all()
    serializer_class = RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new rasterbucket."""
        serializer.save(owner=self.request.user)


class DetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE request
        view with Read, Update and Delete"""
    queryset = Rasterbucket.objects.all()
    serializer_class = RasterbucketSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)


class RasterbucketServiceCreateView(generics.ListCreateAPIView):
    """Defines the rasterbucket service creation behavior"""
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = RasterbucketService.objects.all()
    serializer_class = RasterbucketServiceSerializer

    def perform_create(self, serializer):
        """"""
        pk = self.kwargs.get('pk')
        rasterbucket = get_object_or_404(
            Rasterbucket,
            pk=pk,
            owner=self.request.user)
        serializer.save(
            rasterbucket=rasterbucket,
            owner=self.request.user)


class RasterbucketServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable rasterbucket service view
       with Read, Update and Delete"""
    queryset = RasterbucketService
    serializer_class = RasterbucketServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            RasterbucketService,
            pk=self.kwargs.get('pk_service'))


class GEEMapServiceCreateView(generics.ListCreateAPIView):
    """Defines the GEE map service creation behavior"""
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)
    queryset = GEEMapService.objects.all()
    serializer_class = GEEMapServiceSerializer

    def perform_create(self, serializer):
        """"""
        pk = self.kwargs.get('pk')
        rasterbucketservice = get_object_or_404(
            RasterbucketService,
            pk=pk,
            owner=self.request.user)
        serializer.save(
            rasterbucketservice=rasterbucketservice,
            owner=self.request.user)


class GEEMapServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Defines an actionable GEE map service view
       with Read, Update and Delete"""
    queryset = GEEMapService
    serializer_class = GEEMapServiceSerializer

    def get_object(self):
        """specifies the object used for `update`,
         `retrieve`, `destroy` actions"""
        return get_object_or_404(
            GEEMapService,
            pk=self.kwargs.get('pk_map'))


class UserView(generics.ListAPIView):
    """View to list the user queryset."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """View to retrieve a user instance."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
