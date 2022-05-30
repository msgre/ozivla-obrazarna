from django.contrib import admin
from performance.models import Performance


class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('picture', 'state', 'selected', 'demonstrated_date', 'created')
    search_fields = ['picture__title', 'picture__author']
    list_filter = ('state', 'selected', 'picture', )
    fieldsets = (
        ('Stav', {
            'fields': ('state', 'selected', 'demonstrated_date'),
        }),
        ('Zdroje', {
            'fields': ('picture', 'accompaniment', ),
        }),
        ('Soubory', {
            'fields': ('raw_footage', 'processed_footage'),
        }),
        ('Processing', {
            'classes': ('collapse',),
            'fields': ('processed_returncode', 'processed_stdout', 'processed_stderr'),
        }),
    )
    readonly_fields = ('processed_returncode', 'processed_stdout', 'processed_stderr', 'state')


admin.site.register(Performance, PerformanceAdmin)
