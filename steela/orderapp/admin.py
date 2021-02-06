from django.contrib import admin
from .models import notes
from .models import product
from .models import warehouse_db
from .models import Customer
from .models import history
# Register your models here.

admin.site.register(Customer)
admin.site.register(notes)
admin.site.register(product)
admin.site.register(warehouse_db)
admin.site.register(history)