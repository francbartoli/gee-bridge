from django.shortcuts import render
from rest_framework import generics, permissions
from .permissions import IsOwner
from .serializers import RasterbucketSerializer, UserSerializer
from .models import Rasterbucket
from django.contrib.auth.models import User

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


class UserView(generics.ListAPIView):
    """View to list the user queryset."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """View to retrieve a user instance."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
