from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm, PositionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import Task
from django.views import View
from django.db import transaction

class TempView(TemplateView):
    template_name = "home.html"

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    authentication_form = CustomAuthenticationForm
    redirect_autenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')
    

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_autenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args,**kwargs)

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task # => task.form.html
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

class TaskList(LoginRequiredMixin, ListView):
    model = Task # => task_list.html
    context_object_name = 'tasks'
    login_url = '/login/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks']=context['tasks'].filter(
                title__contains=search_input)
            
        context['search_input']=search_input

        return context
    
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task 
    context_object_name = 'task' 
    success_url = reverse_lazy('tasks')


    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            print(form.cleaned_data['position'])
            position_list = form.cleaned_data['position'].split(',')
            print(position_list)
            with transaction.atomic():
                self.request.user.set_task_order(position_list)

        return redirect(reverse_lazy('tasks'))