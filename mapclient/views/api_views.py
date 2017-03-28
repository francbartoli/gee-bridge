from rest_framework.views import APIView
from rest_framework import viewsets
from mapclient.serializers import *
from rest_framework.response import Response
from mapclient.models import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class UserProcessViewSet(viewsets.ViewSet):
    """
    API endpoint for user processes
    """

    def list(self, request):
        queryset = Process.get_processes_for_user(self.request.user)
        serializer = ProcessSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CompletedProcessViewSet(viewsets.ViewSet):
    """
    API endpoint for completed/started processes
    """

    def list(self, request):
        queryset = Process.get_completed_processes()
        serializer = ProcessSerializer(queryset, many=True)
        return Response(serializer.data)


class CurrentUserView(APIView):

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SingleProcessViewSet(APIView):
    """
    Get all data for a process: Process Details, Maps, & Log
    """

    def get(self, request, **kwargs):
        process = Process.get_by_id(kwargs['process_id'])
        log = process.get_process_log()
        maps = process.get_all_process_processes()
        process_serializer = ProcessSerializer(process)
        log_serializer = ProcessLogSerializer(log, many=True)
        map_serializer = ProcessMapSerializer(maps, many=True)
        return_data = {'process': process_serializer.data,
                       'log': log_serializer.data,
                       'maps': map_serializer.data}
        return Response(return_data)


class ProcessMapsViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        process = get_object_or_404(Process, pk=pk)
        maps = process.get_all_process_maps()
        serializer = ProcessMapSerializer(maps, many=True)
        return Response(serializer.data)
