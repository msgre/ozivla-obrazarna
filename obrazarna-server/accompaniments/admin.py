from django.contrib import admin
from accompaniments.models import Accompaniment


class AccompanimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', )
    search_fields = ['title', 'author']


admin.site.register(Accompaniment, AccompanimentAdmin)
