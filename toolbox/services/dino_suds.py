import logging
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
#from suds.xsd.sxbasic import Import as simp

# Send log messages to console
logging.basicConfig(level=logging.INFO)
# Set Suds logging level to debug, outputs the SOAP messages.
logging.getLogger('suds.client').setLevel(logging.ERROR)

class Dino(object):
    models = None
    def __init__(self):
        url=r'http://www.dinoservices.nl:80/geo3dmodelwebservices-1/Geo3DModelService?wsdl'
        #url=r'http://www.dinoservices.nl/wsdl/geo3dmodelwebservices-1.wsdl'
        #ns="http://www.opengis.net/gml"
        #imp=Import("http://www.opengis.net/gml","http://schemas.opengis.net/gml/3.1.1/base/geometryBasic2d.xsd")
        #schemaLocation="http://schemas.opengis.net/gml/3.1.1/base/geometryAggregates.xsd"
        #imp = Import('http://www.opengis.net/gml/')
        #imp = Import(ns,schemaLocation)
        #imp.filter.add('http://ws.geo3dmodel.dino.nitg.tno.nl/types')
        #d = ImportDoctor(imp)
        self.client = Client(url)
        #self.client.add_prefix('ns2','http://www.opengis.net/gml')
        self.dino=self.client.service

    def list_models2(self,x,y,coordinateSystem=None,includeAreas=None,currentModelOnly=None):
        response = self.dino.listModels(x,y,coordinateSystem,includeAreas,currentModelOnly)
        return response.geo3DModel

    def list_rasters(self,model,resolution,modelUnitName):
        response = self.dino.listRasters(model,resolution,modelUnitName)
        return response
        
    def list_models(self):
        if not self.models:
            response = self.dino.listModels()
            self.models = response.geo3DModel
        return self.models

    def sample_column(self,model,x,y,resolution=100):
        response = self.dino.sampleColumn(model,x,y,resolution)
        return response

    def draw_column(self,model,x,y,resolution=100,property=None,height=None):
        response = self.dino.drawColumn(model,resolution,property,x,y,imageHeight=height)
        return response

if (__name__ == '__main__'):
    x=270000
    y=550000
    resolution=100
    name='lkn-regis-2.1'
    dino = Dino()
    #dino.client.add_prefix('ns2', 'http://www.opengis.net/gml')
    print dino.client
    
    #col=dino.sample_column(name,x,y)
    #ras=dino.list_rasters(name, resolution, None)
    pic = dino.draw_column(name, x, y, resolution, height=300)
    print pic
    