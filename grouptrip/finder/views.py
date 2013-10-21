from finder.citygridapi import citygridplaces
from finder import yelp_api
from finder import expedia_api
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.template.loader import render_to_string
from xml.etree import ElementTree
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
    
    location = request.GET.get('where')
    term = request.GET.get('term')
    url_params['location'] = location
    url_params['term'] = term
    response = yelp_api.search('api.yelp.com', '/v2/search', url_params, settings.YELP_CONSUMER_KEY, settings.YELP_CONSUMER_SECRET, settings.YELP_TOKEN, settings.YELP_TOKEN_SECRET)
    businesses = response['businesses']
    
    template = "finder/finder_activities_results.html"
    html = render_to_string(template, {'location':location, 'term':term, 'businesses': businesses})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    
#TODO: change this to room group, so that adults is grouped with room number
def create_expedia_search_xml(location, check_in, check_out, num_adults):
    root = ElementTree.Element('HotelListRequest')
    destinationId = ElementTree.SubElement(root, 'destinationString')
    destinationId.text = location
    arrivalDate = ElementTree.SubElement(root, 'arrivalDate')
    arrivalDate.text =  check_in
    departureDate = ElementTree.SubElement(root, 'departureDate')
    departureDate.text =  check_out
    roomGroup = ElementTree.SubElement(root, 'RoomGroup')
    room = ElementTree.SubElement(roomGroup, 'Room')
    numberOfAdults = ElementTree.SubElement(room, 'numberOfAdults')
    numberOfAdults.text = str(num_adults)
    return ElementTree.tostring(root)
    
def get_finder_results_expedia(request):
    url_params = {}
    
    location = request.POST.get('location')
    check_in = request.POST.get('check_in')
    check_out = request.POST.get('check_out')
    num_adults = request.POST.get('num_adults')
    
    url_params['cid'] = settings.EXPEDIA_CID
    url_params['minorRev'] = 99
    url_params['apiKey'] = settings.EXPEDIA_API_KEY
    url_params['locale'] = 'en_US'
    url_params['currencyCode'] = 'USD'
    url_params['xml'] = create_expedia_search_xml(location, check_in, check_out, num_adults)
    
    response = expedia_api.search('api.ean.com', '/ean-services/rs/hotel/v3/list', url_params)
    print(response)
    hotels = response['HotelListResponse']['HotelList']['HotelSummary']
    
    template = "finder/finder_hotel_results.html"
    html = render_to_string(template, {'hotels': hotels})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')