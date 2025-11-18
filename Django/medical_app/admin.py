from django.contrib import admin
from .models import Disease, DiseaseRecommendation, Hospital, SymptomKeyword


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'description']
    list_filter = ['severity']
    search_fields = ['name', 'description']


@admin.register(DiseaseRecommendation)
class DiseaseRecommendationAdmin(admin.ModelAdmin):
    list_display = ['disease', 'recommendation']
    list_filter = ['disease']
    search_fields = ['recommendation']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'address', 'phone']
    list_filter = ['specialty']
    search_fields = ['name', 'address', 'specialty']


@admin.register(SymptomKeyword)
class SymptomKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword']
    filter_horizontal = ['diseases', 'hospitals']
    search_fields = ['keyword']

