from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings


class customuser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('trader', 'Trader'),
        ('buyer', 'Buyer'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    average_rating = models.FloatField(default=0.0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username'], name='unique_username'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    trader_name = models.ForeignKey(customuser, on_delete=models.CASCADE, related_name='products', default='')
    sentiment_score = models.FloatField(default=0.0)


    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(customuser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=[('POSITIVE', 'Positive'), ('NEGATIVE', 'Negative'), ('NEUTRAL', 'Neutral')])
    created_at = models.DateTimeField(auto_now_add=True)

class cartItems(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1 )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.user.username} in Cart"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart for {self.user.username}"