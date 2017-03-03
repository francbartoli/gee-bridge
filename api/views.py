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
        serializer.save()
