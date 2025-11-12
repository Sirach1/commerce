from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
class Category(models.Model):
    title = models.CharField(max_length=64)
    thumbnail = models.URLField()

    def __str__(self):
        return self.title

class Auction(models.Model):
    title = models.CharField(max_length=64)
    desc = models.TextField()
    init_bid = models.DecimalField(max_digits=10 ,decimal_places=2)
    img = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name="auctions")
    create_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.title} FOR {self.init_bid} PUBLISHED BY {self.user} ON {self.create_datetime} CATEGORY: {self.category}"
    
class Bid(models.Model):
    amount = models.DecimalField(max_digits=10 ,decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"${self.amount}: From {self.user} on [{self.auction}]"

class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

class Watch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_lists")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

