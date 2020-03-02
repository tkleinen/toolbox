import urllib2
import json
from PIL import Image

class Dino(object):
    
    def __init__(self):
        self.url=r'http://www.dinoservices.nl/geo3dmodelwebservices-1/rest/'

    def get(self,path):
        r = urllib2.urlopen(self.url + path)
        t = r.read()
        d = json.loads(t)
        return self.condense(d)
    
    def condense(self, d):
        '''
        replace dicts with one entry with key '$' with value
        and @label (,) with value
        '''
        if isinstance(d, dict):
 #           if len(d) == 1:
            if '$' in d.keys():
                return d['$']
            elif '@label' in d.keys():
                return d['@label'][0]
            ret = {}
            for k,v in d.items():
                ret[k] = self.condense(v)
            return ret
        elif isinstance(d, list):
            ret = []
            for i in d:
                ret.append(self.condense(i))
            return ret
        else:
            return d
        
        
    def list_models2(self,x,y):
        path='models/list?x=%g&y=%g' % (x,y)
        resp = self.get(path)
#         lmr = resp['listModelsResponse']
        models = resp.get('geo3DModels')
        return models.get('geo3DModel') if models else None

    def list_rasters(self,model,resolution=100,modelUnitName=None):
        path='models/%s/%d/rasters/%s' % (model,resolution,modelUnitName)
        resp = self.get(path)
        return resp
    
    def list_models(self):
        resp = self.get("models/list")
        lmr = resp['listModelsResponse']
        models = lmr['geo3DModels']
        return models

    def sample_column(self,model,x,y,resolution=100):
        path='models/%s/%d/columnsample?x=%g&y=%g' % (model,resolution,x,y)
        resp = self.get(path)
        return resp.get('geoColumn')

    def draw_column(self,model,x,y,resolution=100,width=200,height=400):
        path='models/%s/%d/columnpicture?x=%g&y=%g&iw=%d&ih=%d' % (model,resolution,x,y,width,height)
        resp = self.get(path)
        return resp.get('columnPicture')

if (__name__ == '__main__'):
    x=270000.0
    y=550000.0
    resolution=100
    name='lkn-regis-2.1'
    dino = Dino()
    w=200
    h=300
#    models=dino.list_models2(x,y)
#    ras=dino.list_rasters(name, resolution, 'bxz1')
#    col=dino.sample_column(name,x,y)
    pic = dino.draw_column(name, x, y, resolution, width=w, height=h)
    ref=pic['pictureMetadata']['worldReference']
    h=int(ref['heightImagePixel'])
    w=int(ref['widthImagePixel'])
    bits = pic['columnPicture']
    size=(w,h)
    img=Image.fromstring('L', size, bits)
    print pic
    