from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
import pyrebase
from django.http import HttpResponse
from .models import notes,warehouse_db,product,history
from django.contrib.auth.models import User,auth
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum
import json
 
config = {
    "apiKey": "AIzaSyDwmoRUJErUniIc9jBZRdw6IWuvIG8-0dQ",
    "authDomain": "adam-60075.firebaseapp.com",
    "projectId": "adam-60075",
    "storageBucket": "adam-60075.appspot.com",
    "databaseURL": "https://adam-60075-default-rtdb.firebaseio.com",
    "messagingSenderId": "921412594804",
    "appId": "1:921412594804:web:a7724c930d0527d0c67521",
    "measurementId": "G-6VXNQK54TW"
}

firebase = pyrebase.initialize_app(config)
db=firebase.database()
authentication = firebase.auth()



def warehouse_login(request):

     if request.method == "POST":
       
          username = request.POST["email"]#firmaismi.x@gmail.com
          password = request.POST["password"]
      
          user=warehouse_db.objects.get(username=username)
              
         #my_car = request.session['logged']
          request.session['logged'] = pbkdf2_sha256.verify(password,user.password)
          if(pbkdf2_sha256.verify( password,user.password)):
               request.session['warehouse_id']=str(user.id)
               request.session['warehouse_owener']=str(user.owener)
               request.session['warehouse_worker']=str(user.username)
               print("***",request.session['warehouse_id'])
               print("***",request.session['warehouse_owener'])
               print("***",request.session['logged'])
               return redirect("/main_warehouse")     
          
         
          return render(request,"warehouse/warehouse_login.html")
           
     else:
         return render(request,"warehouse/warehouse_login.html")


def warehouse_logout(request):
     request.session['logged']=False
     return render(request,"warehouse/warehouse_login.html")

def main_warehouse(request):
 
      if(request.session['logged']):
            warehouse_box=db.child("users").child( request.session['warehouse_owener']).child("warehouse_box").order_by_child("warehouse_id").equal_to(request.session['warehouse_id']).order_by_child("delivery_option").equal_to(0).get()
            all_product = product.objects.all().filter(product_user= request.session['warehouse_owener']).count()
            sum_all_product=product.objects.all().filter(product_user= request.session['warehouse_owener']).aggregate(Sum('product_amount'))
            sum_all_product=sum_all_product["product_amount__sum"]
            try:
       
                warehouse_box=len(warehouse_box.val())
            except:
                warehouse_box=0
            return render(request,"warehouse/main_warehouse.html",{"warehouse_box":warehouse_box,"all_product":all_product,"sum_all_product":sum_all_product})
      else:
         return render(request,"warehouse/warehouse_login.html")

  


def orderlist_warehouse(request):
     
          if(request.session['logged']):

                    warehouse_box=db.child("users").child( request.session['warehouse_owener']).child("warehouse_box").order_by_child("warehouse_id").equal_to(request.session['warehouse_id']).order_by_child("delivery_option").equal_to(0).get()
                    
                    warehouse_box_dict={}
                    
                    try:
                        for box in warehouse_box.each():
                                product_price_list=[]
                                product_amount_list=[]
                                product_name_list=[]
                               # print("boz",box.val())
                                for j in box.val()["order_delivery_list"]:
                                
                                        k=db.child("users").child( request.session['warehouse_owener']).child("order").child(j).get().val()
                                
                                        product_id=k["product_id"]
                                        obj=product.objects.get(id=product_id)
                                        product_name_list.append(obj.product_head)
                                        product_amount_list.append(k["product_amount"])
                                        product_price_list.append(obj.product_price)
                                        print("ii",product_amount_list)
                                
                                box.val()["product_amount_list"]=product_amount_list
                                box.val()["product_price_list"]=product_price_list
                                box.val()["product_name_list"]=product_name_list

                                warehouse_box_dict[box.key()]=box.val()
                                #print("**zaza**",warehouse_box_dict)
                    except:
                        pass


                    if request.method == "POST":
                         if request.is_ajax():
                                
                                value=request.POST.get("value")
                                print("----",value)
                                result="haha "+str(value)
                                return JsonResponse({"x":result},status=200)

                         if 'warehouse_orderbox_ready' in  request.POST:
                              
                                   aa=request.POST.getlist('order_box')
                                   
                                   print("aaaaaaaaa",aa)
                                   if(len(aa)>0):
                                        for i in aa:
                                                db.child("users").child(request.user.get_username()).child("warehouse_box").child(i).update({"delivery_option":"hazır"})
                                    
                                   return redirect("/orderlist_warehouse")     

                    print("***",warehouse_box_dict)
                    return render(request,"warehouse/orderlist_warehouse.html",{"warehouse_box_dict":warehouse_box_dict})
          else:
              return render(request,"warehouse/warehouse_login.html")






def check_product_warehouse(request):


           if(request.session['logged']):
                        
               if request.method=="POST":
                    if request.POST.get('action') == 'selo':
                         value= request.POST.get('value')
                         value=json.loads(value)
                         result="Rapor KAydedildi...."
                         now = datetime.now()
                         # dd/mm/YY H:M:S
                         date_time = now.strftime("%d/%m/%Y %H:%M:%S")
                         for i in value:
                             
                             i["history_owner"]=request.session['warehouse_owener']
                             i["date_time"]=date_time
                          
                             s=history(**i)
                             s.save()
                         return JsonResponse({"x":result},status=200)
                         

                    if request.is_ajax():
                        id_v=request.POST.get("id")
                        value=request.POST.get("value")
                        try:
                           product.objects.filter(id = id_v).update(product_amount = value)
                           result=value
                        except:
                              result="Kaydederken Bi problem oluştu..."
                        return JsonResponse({"x":result},status=200)

                    
                    
                    elif "input_output_raport" in request.POST:



                        print("dasas")    

               try:
                  all_product = product.objects.all().filter(product_user= request.session['warehouse_owener'])
                
               except:
                    pass
    
               return render(request,"warehouse/check_product_warehouse.html",{"all_product":all_product})
           else:
               return render(request,"warehouse/warehouse_login.html")






def fun1(request):
    user_input = request.GET.get('value')
    #put your code here
    return HttpResponse('what you want to output to web')