from toolbox.models import GroupProfile, UserProfile, Location, Problem, Variable, Reference, Assumption, Case, Parameter, Financer, NewsItem
from django.contrib import admin
from django import forms
from olwidget.admin import GeoModelAdmin
from django.forms.widgets import TextInput

# we define our resources to add to admin pages
class CommonMedia:
  js = (
    'https://ajax.googleapis.com/ajax/libs/dojo/1.6.0/dojo/dojo.xd.js',
    '/media/admin/js/editor.js',
  )
  css = {
    'all': ('/media/admin/css/editor.css',),
  }


class FinanceAdmin(admin.ModelAdmin):
    list_display=('order','name','url','imgtag')
    
class UserProfileAdmin(admin.ModelAdmin):
    list_display=('user','group')
    
class ProblemAdmin(admin.ModelAdmin):
    list_display=('name','category',)
    fieldsets = (
                 ('',     {'fields':('category', 'name', 'description', 'figure')}),
                 ('Formula', {'classes':('collapse closed',),'fields':('formula','inputs','outputs','code')}),
                 ('References',  {'classes':('collapse closed',),'fields':('references',)}),
                 ('Assumptions', {'classes':('collapse closed',),'fields':('assumptions',)})
                )
    filter_horizontal = ('inputs','outputs','references','assumptions')

class VariableInline(admin.TabularInline):
    model = Variable

class ParameterInline(admin.TabularInline):
    model = Parameter
    
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'user')
    list_filter = ('user',)

    def queryset(self, request):
        qs = super(CaseAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        # list only cases for for current user
        return qs.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(CaseAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class ParameterAdmin(admin.ModelAdmin):
    list_filter = ('location',)
    def queryset(self, request):
        qs = super(ParameterAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        #list only parameters for current user
        return qs.filter(location__user=request.user)

class LocationAdmin(GeoModelAdmin):
    list_display=('name','user')
    list_filter = ('user',)
    inlines = [ParameterInline,]
    options = {
        'hide_textarea': True,
    }
    
    #exclude = ('user',)    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(CaseAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

class GroupAdmin(GeoModelAdmin):
    list_display=('name', 'url', 'imgtag')

class NewsAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(NewsAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(GroupProfile, GroupAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Variable)
admin.site.register(Reference)
admin.site.register(Assumption)
admin.site.register(Case, CaseAdmin)
admin.site.register(Parameter,ParameterAdmin)
admin.site.register(Financer,FinanceAdmin)
admin.site.register(NewsItem,NewsAdmin,Media=CommonMedia)
