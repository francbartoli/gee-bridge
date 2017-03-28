from django.contrib.auth.models import User
from .models import Process, ProcessMap, ProcessLog, Map
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ('id', 'creator', 'algorithm', 'arguments',
                  'results', 'completed', 'created', 'modified')
        depth = 1


class ProcessMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessMap
        fields = ('id', 'process', 'owner', 'status',
                  'maps', 'created', 'modified')


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = ('id', 'text', 'player', 'created')
        depth = 1


class ProcessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessLog
        fields = ('id', 'friendly_name', 'map_type', 'url')
        depth = 1
