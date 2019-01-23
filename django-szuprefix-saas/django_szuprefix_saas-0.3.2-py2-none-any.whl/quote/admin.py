from django.contrib import admin

from . import models


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)


admin.site.register(models.Manufacturer, ManufacturerAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)


admin.site.register(models.Company, CompanyAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'manufacturer')
    raw_id_fields = ('party', 'manufacturer',)


admin.site.register(models.Product, ProductAdmin)


class RequestAdmin(admin.ModelAdmin):
    list_display = ('customer', 'create_time')
    raw_id_fields = ('party', 'customer', 'user')
    search_fields = ("customer.name",)
    # readonly_fields = ('party', 'customer', 'user')


admin.site.register(models.Request, RequestAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'customer', 'product', 'unit_price')
    raw_id_fields = ('party', 'request', 'customer', 'product')
    search_fields = ("customer.name", 'product.name')
    # readonly_fields = ('party',)


admin.site.register(models.Item, ItemAdmin)


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("vendor.name",)
    # readonly_fields = ('party',)


admin.site.register(models.Quote, QuoteAdmin)
