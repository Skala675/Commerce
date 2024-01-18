from django.contrib.auth.models import AbstractUser
from django.db import models

class Category(models.TextChoices):
    ELECTRONICS = 'EL', 'Electronics'
    CLOTHING_ACCESSORIES = 'CA', 'Clothing and Accessories'
    HOME_GARDEN = 'HG', 'Home and Garden'
    VEHICLES = 'VE', 'Vehicles'
    BOOKS_MEDIA = 'BM', 'Books and Media'
    TOYS_GAMES = 'TG', 'Toys and Games'
    SPORTS_OUTDOORS = 'SO', 'Sports and Outdoors'
    COLLECTIBLES = 'CO', 'Collectibles'
    SERVICES = 'SV', 'Services'
    MISCELLANEOUS = 'MI', 'Miscellaneous'
    NOT_LISTED = 'NL', 'Not Listed'


class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.CharField(
        max_length = 100
    )
    description = models.CharField(
        max_length = 2000
    )
    bid = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )
    image = models.URLField(
        blank = True
    )
    category = models.CharField(
        max_length = 2,
        choices = Category.choices,
        default = Category.NOT_LISTED
    )
    user = models.ForeignKey(User, 
        on_delete=models.CASCADE, 
        related_name='listings'
    )
    watchlist = models.ManyToManyField(User,
        blank = True,
        related_name='watchlist'
    )
    is_closed = models.BooleanField(
        default = False
    )
    winner = models.ForeignKey(User,
        null = True,
        blank = True,
        on_delete = models.SET_NULL,
        related_name = 'winner'
    )

class Bids(models.Model):
    bid = models.DecimalField(
        max_digits = 10,
        decimal_places = 2
    )
    listing = models.ForeignKey(Listings,
        on_delete=models.CASCADE,
        related_name = 'bids'
    )
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    

class Comments(models.Model):
    comment = models.CharField(
        max_length = 500
    )
    listing = models.ForeignKey(Listings,
        on_delete=models.CASCADE,
        related_name = 'comments'
    )
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
