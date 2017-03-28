from django.db.models.signals import post_save
from django.dispatch import receiver
from mapclient.models import *
import json
from channels import Group
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .serializers import *
from .models import Process, ProcessMap, ProcessLog


@receiver(post_save, sender=Process)
def new_process_handler(**kwargs):
    """
    When a new process is created, this builds a list of all completed processes and 
    sends it down to all channels in the 'map' group
    """
    # if new
    if kwargs['completed']:
        # send the latest list to all channels in the "map" group
        # the Group's send method requires a dict
        # we pass "text" as the key and then serialize the list 
        # of completed processes
        completed_process_list = Process.get_completed_processes()
        completed_serializer = ProcessSerializer(completed_process_list, many=True)
        Group('map').send({'text': json.dumps(completed_serializer.data)})
