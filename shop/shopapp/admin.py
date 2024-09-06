from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin


admin.site.register(models.Product),
admin.site.register(models.Cart),
admin.site.register(models.cartItems),
admin.site.register(models.Category)

class customUserAdmin(UserAdmin):
    model = models.customuser

admin.site.register(models.customuser, customUserAdmin)