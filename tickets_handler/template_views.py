from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView
from django.utils.decorators import method_decorator

from tickets_handler.beeline_parser.mail import feedback_mail
from tickets_handler.decorators import check_access
from tickets_handler.form import Feedback
from tickets_handler.models import Installer, Workers as WorkersModel
from .decorators import check_access


@method_decorator(check_access, name='dispatch')
class HouseSearch(TemplateView):
    template_name = 'beeline_html/house_search.html'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class CheckNumber(TemplateView):
    template_name = 'beeline_html/check_number.html'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class Index(TemplateView):
    template_name = 'beeline_html/index.html'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class IsmSchedule(TemplateView):
    template_name = 'beeline_html/ism_schedule.html'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class CheckCTN(TemplateView):
    template_name = 'beeline_html/check_ctn.html'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class Installers(ListView):
    model = Installer
    template_name = 'beeline_html/installers.html'
    context_object_name = 'installers'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(check_access, name='dispatch')
class WorkersTable(ListView):
    model = WorkersModel
    template_name = 'beeline_html/workers.html'
    context_object_name = 'workers'
    ordering = 'master'

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@method_decorator(check_access, name='dispatch')
class Feedback(FormView):
    template_name = 'beeline_html/feedback.html'
    form_class = Feedback

    def form_valid(self, form):
        text = { 'descr' : form['descr'].value(), 'agent' : self.request.session['operator']}
        feedback_mail(text)
        return redirect('feedback')

    @method_decorator(check_access)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class WorkersTable(ListView):
    model = WorkersModel
    template_name = 'beeline_html/workers.html'
    context_object_name = 'workers'
    ordering = 'master'

