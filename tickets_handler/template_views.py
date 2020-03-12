from django.views.generic import TemplateView

class HouseSearch(TemplateView):
    template_name = 'beeline_html/house_search.html'


class CheckNumber(TemplateView):
    template_name = 'beeline_html/check_number.html'


class Index(TemplateView):
    template_name = 'beeline_html/index.html'


class IsmSchedule(TemplateView):
    template_name = 'beeline_html/ism_schedule.html'

class CheckCTN(TemplateView):
    template_name = 'beeline_html/check_ctn.html'