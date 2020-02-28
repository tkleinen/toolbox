# coding=utf-8
'''
Created on Jan 17, 2012

@author: theo
'''
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
import urllib, json
from toolbox import settings

# EPSG codes
RDNEW=28992
RDOLD=28991
AMERSFOORT=4289
WGS84=4326

def trans(p, srid):
    '''transform Point p to requested srid'''
    if isinstance(p,Point):
        psrid = p.srid
        if not psrid:
            psrid = WGS84
        if (psrid != srid): 
            tr = CoordTransform(SpatialReference(p.srid), SpatialReference(srid))
            p.transform(tr)
        
        return p
    else:
        raise TypeError('django.contrib.gis.geos.Point expected')

def toRDNew(p):
    return trans(p, RDNEW)

def toWGS84(p):
    return trans(p, WGS84)

def DMSstr(x):
    d = int(x)
    m = int((x-d)*60)
    s = int((x-d-m/60.0)*3600.0)
    return "%d°%02d'%02d%s" % (d,m,s,'"')

def toDMS(p):
    q = toWGS84(p)
    return "%s, %s" % (DMSstr(q.x), DMSstr(q.y))

def geocode(address):
    ''' use Google Maps API to geocode an address '''
    address = urllib.quote_plus(address)
    request = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % address
    try:
        data = json.loads(urllib.urlopen(request).read())
        status = data['status']
        results = data['results'][0]
        address = results['formatted_address']
        geometry = results['geometry']
        location = geometry['location']
        lat = location['lat']
        lon = location['lng']
        return Point(x=float(lon),y=float(lat),srid=WGS84)
    except:
        return None

def point_from_address(address):
    p = geocode(address)
    if p is None:
        return None

def Amersfoort():
    return  Point(y=52.155172,x=5.387203,srid=WGS84)
    
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri

class HttpResponseReload(HttpResponse):
    """
    Reload page and stay on the same page from where request was made.

    example:

    def simple_view(request):
        if request.POST:
            form = CommentForm(request.POST):
            if form.is_valid():
                form.save()
                return HttpResponseReload(request)
        else:
            form = CommentForm()
        return render_to_response('some_template.html', {'form': form})
    """
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__(self)
        referer = request.META.get('HTTP_REFERER')
        self['Location'] = iri_to_uri(referer or "/")
