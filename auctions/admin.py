from django.contrib import admin

from .models import Listings, Bids, Comments, User, Category

# Register your models here.
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(User)
admin.site.register(Comments)