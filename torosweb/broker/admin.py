from django.contrib import admin
from .models import Observatory, Assignment, SuperEvent, GCNNotice
# Register your models here.

admin.site.register(Observatory)
admin.site.register(Assignment)
admin.site.register(SuperEvent)
admin.site.register(GCNNotice)
