from finder.citygridapi import citygridplaces
from finder import yelp_api
from finder import expedia_api
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
    
    
def get_finder_results_yelp(request):
    url_params = {}
    
    location = request.POST.get('where')
    term = request.POST.get('term')
    url_params['location'] = location
    url_params['term'] = term
    
    response = yelp_api.search('api.yelp.com', '/v2/search', url_params, settings.YELP_CONSUMER_KEY, settings.YELP_CONSUMER_SECRET, settings.YELP_TOKEN, settings.YELP_TOKEN_SECRET)
    businesses = response['businesses']
    
    template = "finder/finder_results2.html"
    html = render_to_string(template, {'location':location, 'term':term, 'businesses': businesses})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    
def get_finder_results_expedia(request):
    url_params = {}
    
    url_params['cid'] = settings.EXPEDIA_CID
    url_params['minorRev'] = 99
    url_params['apiKey'] = settings.EXPEDIA_API_KEY
    url_params['locale'] = 'en_US'
    url_params['currencyCode'] = 'USD'
    url_params['xml'] = '<HotelListRequest><city>Seattle</city><stateProvinceCode>WA</stateProvinceCode><countryCode>US</countryCode><arrivalDate>10/17/2013</arrivalDate><departureDate>10/19/2013</departureDate><RoomGroup><Room><numberOfAdults>2</numberOfAdults></Room></RoomGroup><numberOfResults>25</numberOfResults></HotelListRequest>'
    
    response = expedia_api.search('api.ean.com', '/ean-services/rs/hotel/v3/list', url_params)
    hotels = response['HotelListResponse']['HotelList']['HotelSummary']
    
    template = "finder/finder_hotel_results.html"
    html = render_to_string(template, {'hotels': hotels})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')