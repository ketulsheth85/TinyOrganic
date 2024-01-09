from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


# Create your views here.
class CoreView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Pixel = apps.get_model('analytics', 'Pixel')
        context['pixels'] = Pixel.objects.filter(is_active=True)
        return context


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Pixel = apps.get_model('analytics', 'Pixel')
        context['pixels'] = Pixel.objects.filter(is_active=True)
        return context


class OnboardingView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Pixel = apps.get_model('analytics', 'Pixel')
        context['pixels'] = Pixel.objects.filter(is_active=True)
        return context


class CoreUploadCSVView(TemplateView):
    template_name = 'index.html'
    async_function = callable
    view_name = ''

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        self.async_function.delay(decoded_file)
        messages.add_message(request=request, level=messages.SUCCESS, message='File Will be processed shortly!')
        return redirect(reverse(self.view_name))
