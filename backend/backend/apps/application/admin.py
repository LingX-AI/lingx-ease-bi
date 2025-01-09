from django.contrib import admin

from .models import Application

# Register your models here.


class ApplicationAdmin(admin.ModelAdmin):
    verbose_name = "Application"
    list_display = (
        "name",
        "client_id",
        "database_configuration",
    )


admin.site.unregister(Application)
admin.site.register(Application, ApplicationAdmin)

admin.site.site_header = "LingX Chat DB Fine-tuning Backend"
admin.site.site_title = "LingX Chat DB Fine-tuning Backend"
admin.site.index_title = "LingX Chat DB Fine-tuning Backend"
