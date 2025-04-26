from django.contrib import admin
from.models import *

# Register your models here.
admin.site.register(SignUp)
admin.site.register(Notes)



from .models import Company

admin.site.register(Company)

