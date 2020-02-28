from SOAPpy import WSDL
import SOAPpy

class Dino(object):

    models = None
    
    def __init__(self):
        url=r'http://www.dinoservices.nl:80/geo3dmodelwebservices-1/Geo3DModelService?wsdl'
        namespace='http://ws.geo3dmodel.dino.nitg.tno.nl/types'
        #url=r'http://www.dinoservices.nl/wsdl/geo3dmodelwebservices-1.wsdl'
        self.client=WSDL.Proxy(url)
        #self.client=SOAPpy.SOAPProxy(url,namespace)
        self.client.config.debug=1

    def list_models2(self,x,y,coordinateSystem=None,includeAreas=None,currentModelOnly=None):
        response = self.client.listModels(x,y,coordinateSystem,includeAreas,currentModelOnly)
        return response.geo3DModel

    def list_rasters(self,model,resolution,modelUnitName):
        response = self.client.listRasters(model,resolution,modelUnitName)
        return response
        
    def list_models(self):
        if not self.models:
            response = self.client.listModels()
            self.models = response.geo3DModel
        return self.models

    def sample_column(self,model,x,y,resolution=100):
        response = self.client.sampleColumn(model,x,y,resolution)
        return response

    def draw_column(self,model,x,y,resolution=100,property=None,height=None):
        response = self.client.drawColumn(model,resolution,property,x,y,imageHeight=height)
        return response

if (__name__ == '__main__'):
    x=270000.0
    y=550000.0
    resolution=100
    name='lkn-regis-2.1'
    dino = Dino()
    models=dino.list_models2(x,y)
    col=dino.client.sampleColumn(name,x,y,100)
    ras=dino.list_rasters(name, resolution, None)
    pic = dino.draw_column(name, x, y, resolution, height=300)
    print pic
    