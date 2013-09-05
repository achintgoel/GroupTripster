from citygridapi import citygridplaces
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.template.loader import render_to_string
import json

# Create your views here.

def get_finder_results(request):
    where = request.POST.get('where')
    type = request.POST.get('type')
    
    searchwhere = citygridplaces()
    response = searchwhere.srchplaceswhere(where,type,settings.CITY_GRID_PUBLISHER_CODE)
    
    
    pResponse = json.loads(response)

    data = dict(json.loads(json.dumps(pResponse)))
    results = dict(json.loads(json.dumps(data[u'results'])))
    
    locations = results[u'locations']
    template = "finder/finder_results.html"
    html = render_to_string(template, {'locations': locations})
    response = simplejson.dumps({'success':'True', 'html':html, 'locations':locations})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    