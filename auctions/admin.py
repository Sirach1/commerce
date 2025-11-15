from django.contrib import admin
from .models import Auction, User, Category, Watch, Bid, Comment

# Register your models here.
admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Watch)
admin.site.register(Bid)
admin.site.register(Comment)