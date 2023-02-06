from django.db import models

# Create your models here.
class ConnectedTVs(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default="null")
    mobile_no = models.BigIntegerField()
    package = models.CharField(max_length=255)
    date_subscribed = models.DateTimeField()
    expiry_date = models.DateTimeField()
    champ_name = models.CharField(max_length=255)
    building_name = models.CharField(max_length=255)
    tv_mac = models.CharField(max_length=255, default="null")
    package_status = models.CharField(max_length=255)
    connection_status = models.CharField(max_length=255)
    
    

    class Meta:
        ordering = ('id',)


    def __str__(self):
        return f"{self.id}, {self.name}, {self.mobile_no}, {self.package}, {self.date_subscribed}, {self.expiry_date}, {self.champ_name}, {self.building_name}, {self.tv_mac}, {self.package_status}, {self.connection_status}"        
