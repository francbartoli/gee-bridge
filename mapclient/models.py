from __future__ import unicode_literals
from django.db import models
from channels import Group
import json
from django.contrib.auth.models import User
from jsonfield import JSONField
from datetime import datetime
from django.utils import timezone
from gee_bridge import settings
# Create your models here.


class Algorithm(models.Model):
    name = models.CharField(max_length=100, default='wapor')
    arguments = JSONField(default={})

    def __unicode__(self):
        return 'Algorithm {0}'.format(self.name)


class Process(models.Model):
    creator = models.ForeignKey(User, related_name='creator')
    algorithm = models.ForeignKey(
        Algorithm, related_name='algorithm', null=True, blank=True)
    arguments = JSONField(default={})
    result = JSONField(default={})

    # dates
    completed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Process #{0}'.format(self.pk)

    @staticmethod
    def get_completed_processes():
        # return Process.objects.filter(algorithm=None, completed=None)
        now = timezone.now()
        return Process.objects.filter(completed__lte=now).exclude(completed__isnull=True)

    @staticmethod
    def created_count(user):
        return Process.objects.filter(creator=user).count()

    @staticmethod
    def get_processes_for_consumer(user):
        from django.db.models import Q
        return Process.objects.filter(Q(creator=user))

    @staticmethod
    def get_by_id(id):
        try:
            return Process.objects.get(pk=id)
        except Process.DoesNotExist:
            # TODO: Handle this Exception
            pass

    @staticmethod
    def create_new(user, algorithm, arguments):
        """
        Create a new process and process algorithm params
        :param user: the user that created the process
        :return: a new process object
        """
        # make the process's name from the username, the algorithm of
        # the process created
        new_process = Process(creator=user,
                              algorithm=algorithm,
                              arguments=arguments)
        import ipdb; ipdb.set_trace()
        new_process.save()
        # for each row, create the proper number of cells based on rows
        # for row in range(process.rows):
        #     for col in range(process.cols):
        #         new_context = ProcessContext(
        #             process=new_process,
        #             row=row,
        #             col=col
        #         )
        #         new_process.save()

        # put first log into the ProcessLog
        new_process.add_log('Process created by {0}'.format(new_process.creator.username))

        return new_process

    def add_log(self, text, user=None):
        """
        Adds a text log associated with this process.
        """
        entry = ProcessLog(process=self, text=text, consumer=user).save()
        return entry

    def get_all_process_maps(self):
        """
        Gets all of the maps for this Process
        """
        return ProcessMap.objects.filter(process=self)

    def get_process_map(algorithm, arguments):
        """
        Gets a map for a process by it's arguments
        """
        try:
            return ProcessMap.objects.get(process=self,
                                          algorithm=algorithm,
                                          arguments=arguments)
        except ProcessMap.DoesNotExist:
            return None

    # def get_square_by_coords(self, coords):
    #     """
    #     Retrieves the cell based on it's (x,y) or (row, col)
    #     """
    #     try:
    #         square = GameSquare.objects.get(row=coords[1],
    #                                         col=coords[0],
    #                                         game=self)
    #         return square
    #     except GameSquare.DoesNotExist:
    #         # TODO: Handle exception for gamesquare
    #         return None

    def get_process_log(self):
        """
        Gets the entire log for the process
        """
        return ProcessLog.objects.filter(process=self)

    def send_process_update(self):
        """
        Send the updated process information and maps to the process's channel group
        """
        # imported here to avoid circular import
        from serializers import ProcessMapSerializer, ProcessLogSerializer, ProcessSerializer

        maps = self.get_all_process_maps()
        map_serializer = ProcessMapSerializer(maps, many=True)

        # get process log
        log = self.get_process_log()
        log_serializer = ProcessLogSerializer(log, many=True)

        process_serializer = ProcessSerializer(self)

        message = {'process': process_serializer.data,
                   'log': log_serializer.data,
                   'maps': map_serializer.data}

        process_group = 'process-{0}'.format(self.id)
        Group(process_group).send({'text': json.dumps(message)})

    def mark_complete(self, result):
        """
        Sets a process to completed status and records the winner
        """
        self.result = result
        self.completed = datetime.now()
        self.save()


class Map(models.Model):
    friendly_name = models.CharField(max_length=50)
    map_type = models.CharField(choices=settings.MAP_TYPES,
                                max_length=25,
                                default='tms')
    url = models.URLField()


class ProcessMap(models.Model):
    STATUS_TYPES = (
        ('Free', 'Free'),
        ('Selected', 'Selected'),
        ('Surrounding', 'Surrounding')
    )
    process = models.ForeignKey(Process)
    owner = models.ForeignKey(User, null=True, blank=True)
    status = models.CharField(choices=STATUS_TYPES,
                              max_length=25,
                              default='Free')
    maps = models.ForeignKey(Map)

    # dates
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{0} - ({1})'.format(self.process, self.maps)

    @staticmethod
    def get_by_id(id):
        try:
            return ProcessMap.objects.get(pk=id)
        except ProcessMap.DoesNotExist:
            # TODO: Handle exception for processmap
            return None

    # def claim(self, status_type, user):
    #     """
    #     Claims the square for the user
    #     """
    #     self.owner = user
    #     self.status = status_type
    #     self.save(update_fields=['status', 'owner'])

    #     # get surrounding squares and update them if they can be updated
    #     surrounding = self.get_surrounding()

    #     for coords in surrounding:
    #         # get square by coords
    #         square = self.game.get_square_by_coords(coords)

    #         if square and square.status == 'Free':
    #             square.status = 'Surrounding'
    #             square.owner = user
    #             square.save()

    #     # add log entry for move
    #     self.game.add_log('Square claimed at ({0}, {1}) by {2}'
    #                       .format(self.col, self.row, self.owner.username))

    #     # set the current turn for the other player if there are still free
    #     # squares to claim
    #     if self.game.get_all_game_squares().filter(status='Free'):
    #         self.game.next_player_turn()
    #     else:
    #         self.game.mark_complete(winner=user)
    #     # let the game know about the move and results
    #     self.game.send_game_update()


class ProcessLog(models.Model):
    process = models.ForeignKey(Process)
    text = models.CharField(max_length=300)
    user = models.ForeignKey(User, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Process #{0} Log'.format(self.process.id)
