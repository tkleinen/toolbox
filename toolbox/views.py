from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms import ValidationError

from toolbox.models import Problem, Case, Location, Parameter, catname, NewsItem
from toolbox.forms import CaseForm, ParamForm, EditForm, ContactForm, UserProfileForm, BaseEditFormSet, LocationForm, LocationSelectForm
from toolbox.services.dino import Dino
from toolbox.util import toRDNew, HttpResponseReload, Amersfoort
from olwidget.widgets import InfoMap, EditableMap
from categories.models import Category
from django.contrib.auth.models import User
# from django_xhtml2pdf.utils import generate_pdf
from django.db import IntegrityError
from django.forms.util import ErrorList

def newcase(request):
    try:
        loc = Location.objects.get(name='Default')
    except:
        loc = Location()
        loc.name='Default'
        loc.user=request.user
        loc.location=Amersfoort()
        locid=loc.save()
        
    prob = Problem.objects.all()[0]
    dossier = Case(location=loc,problem=prob,user=request.user)
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=dossier)
        if form.is_valid():
            form.instance.user=request.user
            form.instance.location=loc
#            try:
            fid=form.save()
            return HttpResponseRedirect('/dossier/%s/location?new=1' % fid.id)
#            except IntegrityError:
#                name = form.instance.case_number
#                form.errors['case_number'] = ErrorList([u'U hebt al een dossier met de naam ' + name])
    else:
        form = CaseForm(instance=dossier)
    return render_to_response('toolbox/newdossier.html', {'form': form, 'dossier': dossier}, context_instance=RequestContext(request))
    
def locsel(request,pid):
    c = get_object_or_404(Case,pk=pid)
    if request.method == 'POST':
        form = LocationSelectForm(request.user,request.POST)
        if form.is_valid():
            c.location = form.cleaned_data['location']
            if 'submit' in request.POST:
                c.save()
            elif 'change' in request.POST:
                pass
    else:
        form = LocationSelectForm(request.user,instance=c)
    m = c.location.infomap2({'default_zoom':6})
    return render_to_response('toolbox/locsel.html', {'form': form, 'case': c, 'map': m}, context_instance=RequestContext(request))

def locadd(request):
    mode='add'
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if 'geocode' in request.POST:
            loc = form.instance
            adres = form.data['address']
            loc.set_location_from_address(adres)
            form = LocationForm(instance=loc)
        elif form.is_valid():
            form.instance.user = request.user
            try:
                form.save()
            except IntegrityError, e:
                name = form.instance.name
                uid = form.instance.user.id
                form.errors['name'] = ErrorList([u'Locatie bestaat al: ' + name])
                form.instance = Location.objects.get(user=uid, name=name)
                return render_to_response('toolbox/locadd.html', {'form': form, 'integrityerror': e, 'mode':mode}, context_instance=RequestContext(request))
    else:
        newloc = Location(user=request.user)
        form = LocationForm(instance=newloc)
    return render_to_response('toolbox/locadd.html', {'form': form,'mode':mode}, context_instance=RequestContext(request))

def locchange(request,locid):
    mode='change'
    loc = get_object_or_404(Location,pk=locid)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=loc)
        if 'geocode' in request.POST:
            loc = form.instance
            adres = form.data['address']
            loc.set_location_from_address(adres)
            form = LocationForm(instance=loc)
        elif form.is_valid():
            try:
                form.save()
            except IntegrityError, e:
                name = form.instance.name
                uid = form.instance.user.id
                form.errors['name'] = ErrorList([u'Een locatie met deze naam bestaat al: ' + name])
                return render_to_response('toolbox/locadd.html', {'form': form, 'integrityerror': e, 'mode': mode}, context_instance=RequestContext(request))
    else:
        loc = get_object_or_404(Location,pk=locid)
        form = LocationForm(instance=loc)
    return render_to_response('toolbox/locadd.html', {'form': form, 'mode': mode}, context_instance=RequestContext(request))
    
def printcase(request, caseid):
    options={'layers':['osm.mapnik','google.streets','google.satellite'], 'mapDivStyle': {'width':'100%'}}
    c=get_object_or_404(Case,pk=caseid)
    m=c.location.infomap2(options)
    return render_to_response('toolbox/pdf.html', {'map':m, 'case': c}, context_instance=RequestContext(request))

def printpdf(request, caseid):
    raise NotImplementedError('PrintDF is not supported.')

#     options={'layers':['osm.mapnik','google.streets','google.satellite'], 'mapDivStyle': {'width':'100%'}}
#     c=get_object_or_404(Case,pk=caseid)
#     m=c.location.infomap2(options)
#     resp = HttpResponse(content_type='application/pdf')
#     resp['Content-Disposition'] = 'attachment; filename=%s.pdf' % c.case_number
#     context = RequestContext(request)
#     context['case'] = c
#     context['map'] = m
#     context['pdf'] = True
#     result = generate_pdf('toolbox/pdf.html', file_object=resp, context=context)
#     return result

def edit_user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # save form data in database
            form.save()
            
            return HttpResponseRedirect('/') # Redirect after POST            
            
    else:
        u = request.user
        form = UserProfileForm(instance=u)
    return render_to_response('toolbox/userprofile.html', {'form': form}, context_instance=RequestContext(request))


def try_eval(a):
    try:
        return eval(a)
    except:
        return None
    
def bewerk(request,pid):
    '''
    Bewerk berekening met problem class (op basis van dict, zonder location of case)
    '''
    EditFormset = formset_factory(form=EditForm, formset=BaseEditFormSet, extra=0)
    
    problem=get_object_or_404(Problem,pk=pid)
    inp = problem.inputs.all()
    out = problem.outputs.all()
    
    # haal de parents op
    parents = []
    p = problem.category
    while not p is None:
        parents.insert(0,p)
        p=p.parent

    if request.method == 'POST':
        formset = EditFormset(request.POST)
        formset.input_variables = inp
        if formset.is_valid():
            # berekenen
            values = [f.cleaned_data['value'] for f in formset]
            locs = {a.symbol: try_eval(b) for a,b in zip(inp, values)}
            result = problem.trycalc(locs)
        else:
            # redisplay
            # return HttpResponseReload(request)
            result = [] # geen resultaten laten zien, wel de foutmeldingen
            
    else:
        # formset vullen met default waardes
        result = problem.trycalc({ v.symbol: eval(v.default_value) for v in inp })
        data = [{'value': v.default_value} for v in inp]
        formset = EditFormset(initial=data)
        formset.input_variables = inp
        request.session['ref'] = request.META['HTTP_REFERER']
        
    ref = request.session['ref']
    fi = zip(formset, inp)

    #fo = zip(result, out)
    fo = []
    for v in out:
        if v.symbol in result:
            fo.append((result[v.symbol],v))

    if 'error' in result:
        error = result['error']
    else:
        error = None
        
    return render_to_response('toolbox/bewerk_en_bereken.html', {'problem': problem, 'parents':parents, 'formset': formset, 'fi': fi, 'fo': fo, 'refer': ref, 'error': error}, context_instance=RequestContext(request))

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # save form data in database
            form.save()
            
            # send contact mail
            subject = 'Grondwater Toolbox Contactformulier'
            message = form.cleaned_data['message']
            sender = form.cleaned_data['email']
            recipients = ['info@acaciawater.com', sender]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
 
            return HttpResponseRedirect('/') # Redirect after POST            
            
    else:
        form = ContactForm()

    return render_to_response('toolbox/contact.html', {'form': form}, context_instance=RequestContext(request))
    
def partners(request):
    return render_to_response('toolbox/partners.html', context_instance=RequestContext(request))

def info(request):
    return render_to_response('toolbox/info.html', context_instance=RequestContext(request))

def toolbox(request):
    cats = Category.objects.filter(parent=None)
    url = request.GET.get('url',None)
    return render_to_response('toolbox/toolbox.html', {'cats':cats, 'url': url}, context_instance=RequestContext(request))

def welcome(request):
    cats = Category.objects.filter(parent=None)
    try:
	news = NewsItem.objects.latest('date_created')
    except:
        news = NewsItem()
    return render_to_response('toolbox/welcome.html', {'cats':cats, 'news': news}, context_instance=RequestContext(request))

def wizard(request, pid):
    cats = Category.objects.filter(parent=pid)
    url = request.GET.get('url',None)
    if cats:
        # haal de parents op
        parents = []
        p = get_object_or_404(Category, id=pid)
        while not p is None:
            parents.insert(0,p)
            p=p.parent
        # laat categorieen zien
        return render_to_response('toolbox/wizard.html', {'cats':cats, 'parents':parents, 'url': url}, context_instance=RequestContext(request))
    else:
        problems = Problem.objects.filter(category=pid)
        if url is None:
            # Bewerken
            if problems is None or len(problems) == 0:
                return HttpResponseReload(request)
            return bewerk(request, problems[0].id)
        else:
            # terug naar url
            url = "%s?p=%s" % (url, problems[0].id)
            return HttpResponseRedirect(url)
            
def dossier(request):
    name=request.user.username
    doss = Case.objects.filter(user__username=name)
    return render_to_response('toolbox/dossier.html', {'doss':doss}, context_instance=RequestContext(request))

def dosprob(request,pid):
    c=get_object_or_404(Case,pk=pid)
    newp = request.GET.get('p',None)
    if not newp is None:
        # change problem
        c.problem = get_object_or_404(Problem,pk=newp)

    # haal de parents op
    parents = []
    p = c.problem.category
    while not p is None:
        parents.insert(0,p)
        p=p.parent
    
    # FOR HOME.HTML EXTENSION
    cats = Category.objects.all()
    name=request.user.username
    doss = Case.objects.filter(user__username=name)
    
    if request.method == 'POST':
        if 'save' in request.POST:
            c.save()
            
    return render_to_response('toolbox/dossier_probleem.html', {'parents':parents, 'nodes':cats, 'dossiers': doss, 'dossier':c, 'url':'/dossier/%s/problem' % pid}, context_instance=RequestContext(request))

def dosloc(request,pid):
    c = get_object_or_404(Case,pk=pid)
    if request.method == 'POST':
        form1 = LocationSelectForm(request.user, request.POST,instance=c, prefix='dossier')
        form2 = LocationForm(request.POST, instance=c.location)
        #if form1.is_valid():
        if 'geocode' in request.POST:
            loc = form2.instance
            adres = form2.data['address']
            loc.set_location_from_address(adres)
            form2 = LocationForm(instance=loc)
        elif 'submit' in request.POST:
            if form2.is_valid():
                loc = form2.instance
                loc.user = request.user
                if loc.id is None: 
                    loc = form2.save(commit=False)
                try:
                    loc.save()
                except IntegrityError, e:
                    # update existing location
                    name = loc.name
                    uid = loc.user.id
                    loc2 = Location.objects.get(user=uid, name=name)
                    loc.id = loc2.id
                    loc.save()
                c.location=loc
                c.save()
        elif 'change' in request.POST:
            if form1.is_valid():
                c.location = form1.cleaned_data['location']
            form2 = LocationForm(instance=c.location)
        elif 'nieuw' in request.POST:
            c.location = Location(user=request.user)
            form1 = LocationSelectForm(request.user,instance=c,prefix='dossier')
            form2 = LocationForm(instance=c.location)
        else:
            form2 = LocationForm(request.POST)
            if form2.is_valid():
                form2.instance.user = request.user
                loc = form2.save(commit=False)
                form1 = LocationSelectForm(request.user,instance=c,prefix='dossier')
    else:
        isnew = request.GET.get('new','0') 
        if isnew == '1':
            c.location = Location(user=request.user)
        form1 = LocationSelectForm(request.user,instance=c,prefix='dossier')
        form2 = LocationForm(instance=c.location)
    return render_to_response('toolbox/dossier_locatie.html', {'dossier_form': form1, 'form': form2, 'dossier':c, 'map':EditableMap(), 'url':'/dossier/%s/location' % pid}, context_instance=RequestContext(request))

def dosreken(request,pid):

    EditFormset = formset_factory(form=EditForm, formset=BaseEditFormSet, extra=0)
    
    c = get_object_or_404(Case,pk=pid)
    c.add_missing_parameters()
    c.calculate()
    
    problem = c.problem
    inp = c.inputs
    out = c.outputs
    
    varin = [p.variable for p in inp]
    
    if request.method == 'POST':
        formset = EditFormset(request.POST)
        formset.input_variables = varin
        if formset.is_valid():
            # berekenen
            values = [f.cleaned_data['value'] for f in formset]
            fi = zip(varin, values)
            locs = {a.symbol: try_eval(b) for a,b in fi}
            result = problem.trycalc(locs)
            # save input parameters
            fi = zip(inp, values)
            for p,v in fi:
                if v is None or len(v) == 0:
                    p.delete()
                else:
                    p.value = v
                    p.save()
            # save result
            for p in out:
                if p.variable.symbol in result:
                    p.value = result[p.variable.symbol]
                    p.save()

        else:
            # redisplay
            # return HttpResponseReload(request)
            result = [] # geen resultaten laten zien, wel de foutmeldingen
            
    else:
        # formset vullen met standaard waardes
        result = problem.trycalc({ p.variable.symbol: try_eval(p.value) for p in inp })
        data = [{'value': p.value} for p in inp]
        formset = EditFormset(initial=data)
        formset.input_variables = inp
        #request.session['ref'] = request.META['HTTP_REFERER']
        
    vi = [p.variable for p in inp]
    fi = zip(formset, vi)

    #fo = zip(result, out)
    fo = []
    for p in out:
        if p.variable.symbol in result:
            fo.append((result[p.variable.symbol],p.variable))
    
    return render_to_response('toolbox/dossier_reken.html', {'dossier' : c, 'problem': problem, 'formset': formset, 'fi': fi, 'fo': fo}, context_instance=RequestContext(request))


def dosreken1(request,pid):
    c=get_object_or_404(Case,pk=pid)
    c.add_missing_parameters()
    c.calculate()
    inp=c.inputs
    return render_to_response('toolbox/dossier_reken.html', {'dossier':c, 'input':inp, 'url':'/dossier/%s/calc' % pid}, context_instance=RequestContext(request))

def viewparams(request,pid):
    c=get_object_or_404(Case,pk=pid)
    newp = request.GET.get('p',None)
    if not newp is None:
        # change problem
        c.problem = get_object_or_404(Problem,pk=newp)

    c.add_missing_parameters()
    c.calculate()
    inp=c.inputs
    
    # haal de parents op
    parents = []
    p = c.problem.category
    while not p is None:
        parents.insert(0,p)
        p=p.parent
    
    # FOR HOME.HTML EXTENSION
    cats = Category.objects.all()
    name=request.user.username
    doss = Case.objects.filter(user__username=name)
    m=c.location.infomap
    
    return render_to_response('toolbox/dossiertemplate.html', {'parents':parents, 'nodes':cats, 'dossiers': doss, 'dossier':c, 'map':m, 'input':inp, 'url':'/dossier/'+pid}, context_instance=RequestContext(request))

def showcase(request, pid):
    c = get_object_or_404(Case,pk=pid)
    c.add_missing_parameters()
    c.calculate()
    l=c.location
    m=InfoMap([[l.location,'yeah'],])
    return render_to_response('toolbox/showcase.html', {'case': c, 'map': m }, context_instance=RequestContext(request))

def testcalc(request, pid):
    p = get_object_or_404(Case,pk=pid)
    p.add_missing_parameters()
    p.calculate()
    return render_to_response('toolbox/calc.html', {'case': p }, context_instance=RequestContext(request))

_dino = None    
def get_dino():
    global _dino
    if _dino is None:
        _dino = Dino()
    return _dino

def testdino(request):
    dino = get_dino()
    models = dino.list_models2(x=108702.0,y=447988.0)
    table = []
    for m in models:
        md = m.modelMetadata
        l = [md.model, md.description, md.resolution, md.version]
        table.append(l)
    return render_to_response('toolbox/list_table.html', 
                              {'table': table, 
                               'headers': ('model','description','resolution','version',)}, 
                              context_instance=RequestContext(request))
def listmodels(request):
    dino = get_dino()
    models = dino.list_models2(x=108702.0,y=447988.0)
    #models = dino.list_models()
    return render_to_response('dino/models.html', {'models': models}, context_instance=RequestContext(request))

def locmodels(request,locid):
    obj = get_object_or_404(Location,pk=locid)
    loc = toRDNew(obj.location)
    dino = get_dino()
    models = dino.list_models2(x=loc.x,y=loc.y)
    #models = dino.list_models()
    return render_to_response('dino/models.html', {'models': models, 'locatie': obj, 'coords': loc}, context_instance=RequestContext(request))
    
def listparams(request,model):
    dino = get_dino()
    column = dino.sample_column(model,x=108702.0,y=447988.0)
    #picture = dino.draw_column(model,x=108702.0,y=447988.0,height=200)
    #models = dino.list_models()
    return render_to_response('dino/geocolumn.html', {'column': column}, context_instance=RequestContext(request))
    
def locparams(request,locid,model):
    obj = get_object_or_404(Location,pk=locid)
    loc = toRDNew(obj.location)
    dino = get_dino()
    try:
        column = dino.sample_column(model,x=loc.x,y=loc.y)
        picture = dino.draw_column(model,x=loc.x,y=loc.y,height=800)
        #models = dino.list_models()
        return render_to_response('dino/geocolumn.html', {'column': column, 'locatie': obj, 'coords':loc, 'image':picture}, context_instance=RequestContext(request))
    except:
        return render_to_response('dino/nocolumn.html', {'model':model, 'locatie': obj, 'coords':loc}, context_instance=RequestContext(request))
    
def makeplot(x, y, xtitle=None, ytitle=None):
    '''
    Make a line plot of x,y
    '''
    from django.http import HttpResponse
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    
    fig=Figure()
    ax=fig.add_subplot(111)
    if isinstance(y,list):
        for yy in y:
            ax.plot(x,yy,'.')
    else:
        ax.plot(x, y, '.')
    ax.xaxis.set_label_text(xtitle)
    ax.yaxis.set_label_text(ytitle)
    canvas=FigureCanvas(fig)
    response=HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response    

def showplot(request):
    return render_to_response('toolbox/plot.html', context_instance=RequestContext(request))

def parplot(request, pid):
    '''
    Make t,y plot of a parameter 
    '''
    p = get_object_or_404(Parameter, pk=pid)
    d = eval(p.value)
    x=[]
    y=None
    for t in d:
        x.append(t)
        if y is None:
            y=[]
            for i in d[t]:
                y.append([])

        for i in range(len(d[t])):
            y[i].append(d[t][i])
            
    return makeplot(x,y,'x-axis','y-axis')

def cat(request):
    cats = Category.objects.all()
    return render_to_response('toolbox/cattree.html', {'nodes': cats}, context_instance=RequestContext(request))

def catsel(request,cat):
    cats = Category.objects.all()
    return render_to_response('toolbox/catsel.html', {'nodes': cats, 'selected': cat}, context_instance=RequestContext(request))

def cat_detail(request,pid):
    cat = get_object_or_404(Category,pk=pid)
    problems = cat.problem_set.all()
    return render_to_response('toolbox/cat_detail.html', {'cat': cat, 'problems': problems}, context_instance=RequestContext(request))

def problem_detail(request,pid):
    problem = get_object_or_404(Problem,pk=pid)
    return render_to_response('toolbox/problem_detail.html', {'problem': problem}, context_instance=RequestContext(request))


def editparams(request,pid):
    ParamFormset = modelformset_factory(Parameter, form=ParamForm, extra=0)
    c=get_object_or_404(Case,pk=pid)
    c.add_missing_parameters()
    c.calculate()
    inp=c.inputs
    if request.method == 'POST':
        formset = ParamFormset(request.POST)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            formset.save()
            # save case as well to update date_modified
            c.save()
            return HttpResponseReload(request)
            
    else:
        formset = ParamFormset(queryset=c.inputQ())
    return render_to_response('toolbox/editparams.html', {'dossier':c, 'formset': formset, 'fi': zip(formset,inp)}, context_instance=RequestContext(request))

def dossier_details(request,pid):
    c=get_object_or_404(Case,pk=pid)
    c.add_missing_parameters()
    c.calculate()
    inp=c.inputs
    options={'layers':['osm.mapnik','google.streets','google.satellite'], 'mapDivStyle': {'width':'100%'}}
    m=c.location.infomap2(options)

    parents = []
    p=c.problem.category
    while not p is None:
        parents.insert(0,p)
        p=p.parent
        
    return render_to_response('toolbox/dossier_details.html', {'dossier':c, 'map':m, 'input':inp, 'parents':parents}, context_instance=RequestContext(request))

def dosdel(request, pid):
    c=get_object_or_404(Case,pk=pid)
    c.delete()
    return HttpResponseRedirect('/dossier')
    
