from django.db import models

# Create your models here.
class UserInfo(models.Model):
    name =models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    age=models.IntegerField()

#
class MyModel(models.Model):
    image = models.ImageField(upload_to='images/')