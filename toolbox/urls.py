from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('toolbox.views',
    url(r'^home/$', 'welcome', name='welcome'),
    url(r'^$', 'welcome', name='welcome'),
    url(r'^contact/$', 'contact'),
    url(r'^partners/$', 'partners'),
    url(r'^toolbox/$', 'toolbox'),
    url(r'^info/$', 'info'),
    url(r'^location/(?P<pid>\d+)$', 'locsel'),
    url(r'^location/add$', 'locadd'),
    url(r'^location/change/(?P<locid>\d+)$', 'locchange'),
    url(r'^case/(?P<pid>\d+)$','showcase'),
    url(r'^calc/(?P<pid>\d+)$','testcalc'),
    url(r'^dino$','listmodels'),
    url(r'^dino/(?P<locid>\d+)$','locmodels'),
    url(r'^dino/(?P<locid>\d+)/model/(?P<model>\S+)','locparams'),
    url(r'^cat/(?P<pid>\d+)$', 'cat_detail'),
    url(r'^problem/(?P<pid>\d+)$', 'problem_detail'),

    url(r'^dossier/(?P<pid>\d+)$', 'viewparams'),
    url(r'^dossier/(?P<pid>\d+)/problem$', 'dosprob'),
    url(r'^dossier/(?P<pid>\d+)/location$', 'dosloc'),
    url(r'^dossier/(?P<pid>\d+)/calc$', 'dosreken'),
    url(r'^dossier/(?P<pid>\d+)/delete$', 'dosdel'),
    url(r'^dossier/new$', 'newcase'),
    url(r'^dossier$', 'dossier'),

    url(r'^wizard/(?P<pid>\d+)$', 'wizard'),
    url(r'^edit/(?P<pid>\d+)$', 'editparams'),
    url(r'^bewerk/(?P<pid>\d+)$', 'bewerk'),
    url(r'^users/$', 'edit_user_profile'),
    url(r'^print/(?P<caseid>\d+)$','printcase'),
    url(r'^printpdf/(?P<caseid>\d+)$','printpdf'),
    url(r'^cat/$', 'cat'),
    url(r'^category/select/(?P<cat>\d+)$', 'catsel'),
    
)

from registration.views import register
from toolbox.forms import RegistrationFormEx
import regbackend

urlpatterns += patterns('',

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', register, 
        {'backend': 'registration.backends.default.DefaultBackend',
         'form_class': RegistrationFormEx,
         'success_url': '/'}, 
        name='registration_register'),
    url(r'^accounts/',include('registration.backends.default.urls')),
#    url(r'^zetting/',include('zetting.urls')),
    
)

urlpatterns += patterns('',
  url(r'^login/$', 'django.contrib.auth.views.login'),
  url(r'^logout/$', 'django.contrib.auth.views.logout'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
