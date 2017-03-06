from django.shortcuts import render
from rest_framework import generics
from .serializers import RasterbucketSerializer
from .models import Rasterbucket

# Create your views here.


class CreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api"""
    queryset = Rasterbucket.objects.all()
    serializer_class = RasterbucketSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new rasterbucket."""
        serializer.save(owner=self.request.user)


class DetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE request
        view with Read, Update and Delete"""
    queryset = Rasterbucket.objects.all()
    serializer_class = RasterbucketSerializer
