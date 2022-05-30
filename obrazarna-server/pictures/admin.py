from django.contrib import admin
from pictures.models import Picture


class PictureAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'number', 'created')
    search_fields = ['title', 'author', 'number']
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'year', 'technique', 'collection', 'number', 'notes')
        }),
        ('Obrázky', {
            'fields': ('file', 'mask', 'width', 'height', 'grid_width', 'grid_height', 'grid_ratio'),
        }),
    )
    readonly_fields = ('width', 'height', 'grid_width', 'grid_height', 'grid_ratio')


admin.site.register(Picture, PictureAdmin)
