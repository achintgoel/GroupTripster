import socket, urllib, urllib2
class citygridplaces(object):
       
    def srchplaceswhere(self, where, type, publishercode):        
        qStr = {'publisher':publishercode, 'where':where, 'type':type, 'format':'json'}
        
        url = "http://api.citygridmedia.com/content/places/v2/search/where?"
        
        
        url += urllib.urlencode(qStr)

        response = urllib2.urlopen( url ).read()

        return response           
           
       
    def placesdetail(self,id,id_type, publishercode):
        
        qStr = {'id':id, 'id_type':id_type, 'format':'json', 'publisher':publishercode}
        
        url = "http://api.citygridmedia.com/content/places/v2/detail?"
        
        
        url += urllib.urlencode(qStr)           
        
        response = urllib2.urlopen( url ).read()
        
        return response