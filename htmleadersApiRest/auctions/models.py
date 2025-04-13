from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import CustomUser


class Category(models.Model): 
    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering=('id',)

    def __str__(self):
        return self.name

class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(1), MaxValueValidator(5)])
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='auctions', on_delete=models.CASCADE)
    thumbnail = models.URLField()
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(CustomUser, related_name='auctions',on_delete=models.CASCADE)

    class Meta:
        ordering=('id',)

    def __str__(self):
        return self.title

class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name="bids", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.CharField(max_length=150, null=True, blank=True)
    bidder_id = models.ForeignKey(CustomUser, related_name='bids',on_delete=models.CASCADE)

    class Meta:
        ordering=('-price', 'creation_date')

    def __str__(self):
        return self.price