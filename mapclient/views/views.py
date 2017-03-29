from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from mapclient.models import Process


class HomeView(TemplateView):
    template_name = 'home.html'


class CreateUserView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = '/'

    def form_valid(self, form):
        valid = super(CreateUserView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid


class MapView(TemplateView):
    template_name = 'components/map/map.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MapView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)
        # get current completed processes to prepopulate the list

        # we're creating a list of processes
        # that contains just the id (for the link) and the creator
        completed_processes = [{
            'creator': process.creator.username,
            'id': process.pk}
            for process in Process.get_completed_processes()]
        print completed_processes
        # for the consumer's processes,
        # we're returning a list of processes
        consumer_processes = Process.get_processes_for_consumer(self.request.user)
        print consumer_processes

        return context
