from django.db import models
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    custemer_address=models.CharField(max_length=200)
    customer_detail=models.CharField(max_length=200)
    product_user=models.CharField(max_length=100)#bunu foregin key yap, unique veya id yap 
    qr_code = models.ImageField(upload_to='customer_qr_codes', blank=True)

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(self.name)
        canvas = Image.new('RGB', (290, 290), 'white')
        canvas.paste(qrcode_img)
        fname = f'customer_qr_code-{self.name}.png'
        buffer = BytesIO()
        canvas.save(buffer,'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)



class notes(models.Model):
    id = models.AutoField(primary_key=True)
    note_head=models.CharField(max_length=100)
    note_body=models.TextField()
    note_user=models.CharField(max_length=100)#bunu foregin key yap
    date_time=models.CharField(max_length=100)



class product(models.Model):
    id = models.AutoField(primary_key=True)
    product_price=models.CharField(max_length=100,default="")
    product_head=models.CharField(max_length=100,default="")
    product_body=models.TextField(default="")
    product_user=models.CharField(max_length=100)# importnant ******bunu foregin key yap
    product_amount=models.IntegerField(default=0)
    date_time=models.CharField(max_length=100,default="")
    qr_code = models.ImageField(upload_to='product_qr_codes', blank=True)
 
 

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(self.product_head)
        canvas = Image.new('RGB', (290, 290), 'white')
        canvas.paste(qrcode_img)
        fname = f'product_qr_code-{self.product_head}.png'
        buffer = BytesIO()
        canvas.save(buffer,'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)


class warehouse_db(models.Model):
     id = models.AutoField(primary_key=True)
     warehose_name=models.CharField(max_length=100)
     user_first_name=models.CharField(max_length=100)
     user_last_name=models.CharField(max_length=100)
     username=models.CharField(max_length=100,unique=True)
     password=models.CharField(max_length=256)
     owener=models.ForeignKey(User, on_delete=models.CASCADE)
     def verify_password(self,passwd):
         return pbkdf2_sha256.verify(passwd,self.password)
     def get_username(self):
         return warehouse_db.objects.get()

class history(models.Model):
     id = models.AutoField(primary_key=True)
     product_id=models.CharField(max_length=100)
     first_value=models.CharField(max_length=100)
     last_value=models.CharField(max_length=100)
     date_time=models.CharField(max_length=100)
     #history_owner=models.ForeignKey(User, db_index=True,on_delete=True)
     history_owner=models.CharField(max_length=100)