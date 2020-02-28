from django.db import models
from django.contrib.gis.db import models as geo
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from toolbox.util import toRDNew, toDMS, geocode
from olwidget.widgets import InfoMap

class NewsItem(models.Model):
    text=models.TextField(_('text'))
    user=models.ForeignKey(User,default=User,verbose_name=_('user'))
    date_created=models.DateTimeField(_('created'),auto_now_add=True)
    date_modified=models.DateTimeField(_('modified'),auto_now=True)
    
    text.allow_tags = True

class Contact(models.Model):
    firstname=models.CharField(_('first name'), max_length=100)
    lastname=models.CharField(_('last name'), max_length=100, blank=True)
    email=models.EmailField(_('email address'))
    phone=models.CharField(_('phone number'),max_length=16,blank=True)
    message=models.TextField(_('message'))
    
class Financer(models.Model):
    name=models.CharField(_('financer'),max_length=100)
    logo=models.ImageField(_('logo'),upload_to='logos',blank=True)
    url=models.URLField(_('website'), blank=True)
    order=models.IntegerField(default=1)

    def __unicode__(self):
        return self.name
    
    def imgtag(self):
        return '<img src="/media/%s" height="50px"\>' % self.logo
    
    imgtag.allow_tags=True
    imgtag.short_description='logo'

    class Meta:
        verbose_name = _('financer')
    
class GroupProfile(models.Model):
    name=models.CharField(_('group'),max_length=50)
    logo=models.ImageField(_('logo'),upload_to='logos',blank=True)
    url=models.URLField(_('website'), blank=True)
    boundary=geo.PolygonField(blank=True,verbose_name=_('boundary'))
    objects = geo.GeoManager()
    
    class Meta:
        verbose_name = _('group profile')

    def __unicode__(self):
        return self.name

    def imgtag(self):
        return '<img src="/media/%s" height="50px"\>' % self.logo

    imgtag.allow_tags=True
    imgtag.short_description='logo'

def default_group():
    return GroupProfile.objects.get(name='default')

class UserProfile(models.Model):
    user=models.OneToOneField(User,verbose_name=_('user'))
    group=models.ForeignKey(GroupProfile,default=default_group,verbose_name=_('group'))
    objects = geo.GeoManager()
    def __unicode__(self):
        return self.user.__unicode__()

    class Meta:
        verbose_name = _('user profile')

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Variable(models.Model):
    name=models.CharField(_('name'),max_length=50)
    symbol=models.CharField(_('symbol'),max_length=10)
    description=models.TextField(_('description'),blank=True)
    unit=models.CharField(_('unit'),max_length=50)
    default_value=models.TextField()
    def __unicode__(self):
        return '%s [%s] (%s)' % (self.symbol, self.unit, self.name)

    class Meta:
        verbose_name = _('variable')
            
class Assumption(models.Model):
    assumption=models.CharField(_('assumption'),max_length=100)
    description=models.TextField(blank=True)
    def __unicode__(self):
        return self.assumption
    
    class Meta:
        verbose_name = _('assumption')

class Reference(models.Model):
    author=models.CharField(max_length=100)
    title=models.TextField()
    publisher=models.CharField(max_length=100)
    year=models.IntegerField()
    pages=models.CharField(max_length=50,blank=True)
    link=models.FileField(upload_to='references',blank=True)
    def __unicode__(self):
        return '%s (%s) - %s (%s)' % (self.author, self.year, self.title, self.pages)

    class Meta:
        verbose_name = _('reference')

def catname(cat):
        if cat.parent is None:
            return cat.name
        else:
            return catname(cat.parent) + ' - ' + cat.name

from categories.models import Category
Category.fullname = property(lambda u: catname)
            
class Problem(models.Model):
    name=models.CharField(_('name'),max_length=100, unique=True)
    description=models.TextField(_('description'),blank=True)
    figure=models.ImageField(upload_to='figures', blank=True)
    formula=models.ImageField(upload_to='formulas', blank=True)
    inputs=models.ManyToManyField(Variable,related_name='inputs',blank=True)
    outputs=models.ManyToManyField(Variable,related_name='outputs',blank=True)
    code=models.TextField('Python code',blank=True)
    assumptions=models.ManyToManyField(Assumption, blank=True)
    references=models.ManyToManyField(Reference, blank=True)
            
    @property
    def category_name(self):
        if hasattr(self,'category'):
            return self.category.fullname
        return None

    def calculate(self, variables):
        exec self.code in globals(), variables
        output = {}
        for v in self.outputs.all():
            if v.symbol in variables:
                output[v.symbol] = variables[v.symbol]
        return output

    def trycalc(self, variables):
        try:
            return self.calculate(variables)
        except:
            output = {}
            for v in self.outputs.all():
                output[v.symbol] = 'N/A'
            return output
        
    def catfig(self,cat):
        if cat.thumbnail:
            return cat.thumbnail
        elif cat.parent:
            return self.catfig(cat.parent)
        else:
            return None
        
    @property
    def category_figure(self):
        if hasattr(self,'category'):
            return self.catfig(self.category)
        return None
    
    @property
    def anyfig(self):
        if self.figure is None:
            return self.category_figure()
        else:
            return self.figure
        
    def __unicode__(self):
        return self.name

    def admin_figure(self):
        return '<img src="%s"\>' % self.figure

    admin_figure.allow_tags=True

from django.contrib.gis.geos import Point

class Location(models.Model):
    name=models.CharField(_('name'),max_length=50)
    description=models.TextField(_('description'),blank=True)
    address=models.CharField(_('address'), max_length=100, blank=True)
    zoomlevel=models.IntegerField(_('zoom'), default=8)
    location=geo.PointField(verbose_name=_('location'))
    user=models.ForeignKey(User,default=User,verbose_name=('user'))
    
    objects = geo.GeoManager()
    
    class Meta:
        verbose_name = _('location')
        unique_together = ('name','user')
        
    def __unicode__(self):
        return self.name

    @property
    def group(self):
        return self.user.profile.group
    
    @property
    def rd_coords(self):
        p = Point(x=self.location.x, y=self.location.y, srid=self.location.srid)
        return toRDNew(p)

    @property
    def latlon(self):
        p = Point(x=self.location.x, y=self.location.y, srid=self.location.srid)
        return toDMS(p)

    @property
    def infomap(self):
        info=[[self.location,self.name],]
        m = InfoMap(info)
        return m

    def infomap2(self,options):
        info=[[self.location,self.name],]
        if options is None:
            options={'mapDivStyle': {'width':'400px','height':'300px'} }
        m = InfoMap(info,options)
        return m

    def set_location_from_address(self, address):
        p = geocode(address)
        if not p is None:
            self.address = address
            self.location = p
        
def try_eval(a):
    try:
        return eval(a)
    except:
        return None

class Case(models.Model):
    problem=models.ForeignKey(Problem,verbose_name=_('problem'))
    location=models.ForeignKey(Location,verbose_name=_('location'))
    case_number=models.CharField(_('case_number'),max_length=50)
    description=models.TextField(_('description'),blank=True)
    user=models.ForeignKey(User,default=User,verbose_name=_('user'))
    date_created=models.DateTimeField(_('created'),auto_now_add=True)
    date_modified=models.DateTimeField(_('modified'),auto_now=True)
    
    objects = geo.GeoManager()
       
    class Meta:
        verbose_name = _('case')
        unique_together = ('case_number','user')
        
    def __unicode__(self):
#        return '%s (%s)' % (self.location, self.problem)
        return self.case_number

    @property
    def group(self):
        return self.user.profile.group

    @property
    def params(self):
        ''' returns all parameters for current problem as a dict '''
        a = { v.symbol : try_eval(v.default_value) for v in self.problem.inputs.all() } # defaults inputs for this problem
        b = { v.symbol : try_eval(v.default_value) for v in self.problem.outputs.all() } # defaults outputs for this problem
        c = { p.variable.symbol : try_eval(p.value) for p in self.location.parameters.all() } # parameters for current location
        return dict(a.items()+b.items()+c.items()) # merge the dicts

    def add_missing_parameters(self):
        ''' Adds missing parameters to this case '''
        for v in self.problem.inputs.all():
            try:
                p = self.location.parameters.get(variable__id=v.id)
            except Parameter.DoesNotExist:
                # create parameter from variable and add to location
                p = Parameter(location = self.location, variable = v, value = v.default_value)
                p.save()
    
    def save_output(self, result):
        ''' Collect output values from result dict '''
        for v in self.problem.outputs.all():
            if v.symbol in result:
                try:
                    p = self.location.parameters.get(variable__id = v.id)
                    p.value = repr(result[v.symbol])
                    p.save()
                except Parameter.DoesNotExist:
                    # auto add output parameter(s)
                    p = Parameter(location = self.location, variable = v, value = repr(result[v.symbol]))
                    p.save()
    
    @property
    def outputs(self):
        ''' returns a list of output parameters '''
        ret = []
        for v in self.problem.outputs.all():
            try:
                p = self.location.parameters.get(variable__id = v.id)
                ret.append(p)
            except Parameter.DoesNotExist:
                pass
        return ret

    @property
    def inputs(self):
        ''' returns a list of input parameters '''
        ret = []
        for v in self.problem.inputs.all():
            try:
                p = self.location.parameters.get(variable__id = v.id)
                ret.append(p)
            except Parameter.DoesNotExist:
                pass
        return ret
    
    def calculate(self):
        ''' calculate output variables using problem's code '''
        loc = self.params
        try:
            exec self.problem.code in globals(), loc
            self.save_output(loc)
        except:
            pass

    def inputQ(self):
        ''' return queryset of input parameters '''
        inp = self.inputs
        ids = [x.id for x in inp]
        q=Parameter.objects.filter(id__in=ids)
        return q
        
class Parameter(models.Model):
    location=models.ForeignKey(Location,related_name='parameters',verbose_name=_('location'))
    variable=models.ForeignKey(Variable,verbose_name=_('variable'))
    value=models.CharField(_('value'),max_length=255)
    source=models.CharField(_('source'),max_length=255,blank=True)
    objects = geo.GeoManager()

    @property
    def varname(self):
        return self.variable.name
    
    class Meta:
        verbose_name = _('parameter')
    
    def __unicode__(self):
        return '%s, %s' % (self.location, self.variable)
