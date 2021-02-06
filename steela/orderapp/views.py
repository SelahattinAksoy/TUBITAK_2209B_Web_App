from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import notes,warehouse_db,Customer
from .models import product
import pyrebase #import pyrbase4
from passlib.hash import pbkdf2_sha256
from .pdf_view import ViewPDF,DownloadPDF

from xhtml2pdf import pisa
from django.template.loader import get_template
import ast 
from io import BytesIO
from django.http import HttpResponse

from django.contrib.staticfiles.templatetags.staticfiles import static
import statsmodels.api as sm

import pandas as pd
from io import StringIO
from datetime import date
import numpy as np


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


def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,encoding='UTF-8')
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None



def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        user_name = request.POST["user_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
    

        if password==confirm_password :
          if User.objects.filter(username=user_name).exists():
              context={"info":"kullanıcı kayıtlı, lütfen başka kullanıcı adı kullanınız."}
              return render(request, "register.html",context)
          elif User.objects.filter(email=email).exists():
              context={"info":"kullanıcı kayıtlı, lütfen başka email kullanınız."}
              return render(request, "register.html",context)


          user=User.objects.create_user(username=user_name,email=email,first_name=first_name,last_name=last_name,password=password)
          user.save()

          

          worker={"first_name":"first emplooye","last_name":"first emplooye","department":"first emplooye","mail":"first emplooye",
          "latitude":37.04022,"longitude":35.26165 }
          order={"product_name":"first_order","product_amount":"first_order","product_date":"first_order",
          "customer_name":"first_order","customer_address":"first_order", "latitude":36.987912,"longitude":35.326881,"order_taker":"first order taker",
          "delivery_date":"first order","delivery_situation":"first order" }
          db.child("users").child(user_name).child("order").push(order)
          db.child("users").child(user_name).child("emplooyes").push(worker)

                

          return redirect("/login")
        else:
            context={"info":"Şifreler uyuşmamaktatır."}
            return render(request, "register.html",context)

    else:
        return render(request, "register.html")


def index(request):
    return render(request,"index.html")


def login(request):
    if request.method == "POST":
       
       email = request.POST["email"]
       password = request.POST["password"]
       user=auth.authenticate(username=email,password=password)
 
       if user is not None:
           auth.login(request,user)
          
           return redirect("/main")
       else:
            context={"info":"Kullanıcı adı veya şifre yanlış"}
            return render(request,"login.html",context)

      
    else:
         return render(request,"login.html")





@login_required(login_url="/")
def main(request):



    workers_num=db.child("users").child(request.user.get_username()).child("emplooyes").shallow().get()
    order_num=db.child("users").child(request.user.get_username()).child("order").shallow().get()
    warehouse_box=db.child("users").child(request.user.get_username()).child("warehouse_box").shallow().get()
     
    all_note=notes.objects.filter(note_user=request.user.get_username()).count()
    all_products=product.objects.filter(product_user=request.user.get_username()).count()
  
    all_Customer=Customer.objects.filter(product_user=request.user.get_username()).count()

    workers_num=len(workers_num.val())-1
    order_num=len(order_num.val())-1
    try:
       
        warehouse_box=len(warehouse_box.val())
    except:
        warehouse_box=0

    now = datetime.now()
    # dd/mm/YY H:M:S
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    if request.method == "POST":
            if 'raport_pdf_view' in  request.POST:
                    data = {
                        "all_products": all_products,
                        "workers_num": workers_num,
                        "order_num": order_num,
                        "warehouse_box":warehouse_box,
                        "all_Customer":all_Customer,
                        "date":date_time,
                      }
	
                    pdf = render_to_pdf('app/raport.html', data )
                    return HttpResponse(pdf, content_type='application/pdf')

                 
            elif 'raport_pdf_download' in  request.POST:


                    data = request.POST["fatura_detaya"]
                    data=ast.literal_eval(data)
                    order_list={"selo":[]}
                
                    for i in data["order_delivery_list"]:
                            zaza=db.child("users").child(request.user.get_username()).child("order").child(i).get()
                            order_list["selo"].append(zaza.val())

                    pdf = render_to_pdf('app/pdf_template.html', order_list)
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "Invoice_%s.pdf" %("12341231")
                    content = "attachment; filename='%s'" %(filename)
                    response['Content-Disposition'] = content
                    return response



    
    context=[workers_num,order_num,all_note,all_products,warehouse_box,all_Customer]
    return render(request,"main.html",{"liste":context})


@login_required(login_url="/")
def products(request):
   
    all_product=product.objects.filter(product_user=request.user.get_username())
  
    if request.method == "POST":
            if 'delete_product' in  request.POST:
                   product_id = request.POST["product_id"]  
                   product.objects.get(pk=product_id).delete()
                 
            elif 'add_product' in  request.POST:
            
                now = datetime.now()
                # dd/mm/YY H:M:S
                date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        
                product_head = request.POST["product_head"]
                product_body = request.POST["product_body"]
                product_price = request.POST["product_price"]
                save_product=product(product_head=product_head,product_price=product_price,product_body=product_body,date_time=date_time,product_user=request.user.get_username())
                save_product.save()
                
                x={"product_name":product_head}
                db.child("users").child(request.user.get_username()).child("product").push(x)
                
            return  redirect("/products")
    else:
        return render(request, "products.html",{"all_product": all_product})



@login_required(login_url="/")
def orderlist(request):

       orders=db.child("users").child(request.user.get_username()).child("order").get()
       dict_siparis= []  # databasedn  kullanıcıları çekip buraya eklicez
       all_product=product.objects.filter(product_user=request.user.get_username())
       all_customer=Customer.objects.filter(product_user=request.user.get_username())
       
       for user in orders.each():
            dict_siparis.append(user.val()) 

       dict_siparis.reverse()
       if request.method == "POST":
          
            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            product_name = request.POST["product_name"]
            product_amount = request.POST["product_amount"]
            customer_name = request.POST["customer_name"]
            customer_address = request.POST["customer_address"]
           
            
            if not Customer.objects.filter(name=customer_name).exists():
                Customer.objects.create(name=customer_name,custemer_address=customer_address,product_user=request.user.get_username())
                customer={"customer_name":customer_name,"customer_address":customer_address}
                db.child("users").child(request.user.get_username()).child("customer").push(customer)
            if not product.objects.filter(product_head=product_name).exists():
                product.objects.create(product_head=product_name,product_user=request.user.get_username(),product_price=23,product_body="detay yok..")
                
                x={"product_name":product_name}
                db.child("users").child(request.user.get_username()).child("product").push(x)
            
            product_id = product.objects.filter(product_user=request.user.get_username()).get(product_head=product_name).id
            order={"product_name":product_name,"product_amount":product_amount,"product_date":dt_string,
            "customer_name":customer_name,"customer_address":customer_address,"delivery_situation":"sipariş alındı","delivery_date":"delivery_date",
            "latitude":"latitude","longitude":"longitude","product_id":product_id,"order_taker":"ofis"}
            db.child("users").child(request.user.get_username()).child("order").push(order)

            return  redirect("/orderlist")
       else:
          return render(request,"orderlist.html",{"orders_list":dict_siparis,"all_product":all_product,"all_customer":all_customer})




@login_required(login_url="/")
def emplooyes(request):
     workers=db.child("users").child(request.user.get_username()).child("emplooyes").get()
     dict_workers= []  # databasedn  kullanıcıları çekip buraya eklicez

     for user in workers.each():
           
            dict_workers.append(user.val()) 
   
     dict_workers.reverse()
     if request.method == "POST":
         
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            department= (request.POST["department"]).lower()
            mail = request.POST["mail"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            mail=request.user.get_username()+"."+mail
            worker={"first_name":first_name,"last_name":last_name,"department":department,"mail":mail,
            "latitude":"latitude","longitude":"longitude","order_delivery_list":"order_delivery_list" }

            db.child("users").child(request.user.get_username()).child("emplooyes").push(worker)
            authentication.create_user_with_email_and_password(mail,password)
            return  redirect("/emplooyes")
     else:
          #return render(request,"orderlist.html",{"orders_list":dict_siparis})
          return render(request,"emplooyes.html",{"workers_list":dict_workers})






@login_required(login_url="/")
def graphs(request):


    dict_all_product_count=dict()
    dict_all_customer_count=dict()
    dict_all_warehouse_count=dict()
    dict_all_emplooye_count=dict()

    order=db.child("users").child(request.user.get_username()).child("order").get()
    warehouse_box=db.child("users").child(request.user.get_username()).child("warehouse_box").get()
    emplooyes=db.child("users").child(request.user.get_username()).child("emplooyes").get()

    try:
        for i in order.each():
            x=i.val()["product_name"]
            y=i.val()["customer_name"]
            if x in dict_all_product_count:
                    
                dict_all_product_count[x]= dict_all_product_count[x]+1
            else:
                dict_all_product_count[x]=1
            
            if y in dict_all_customer_count:
                dict_all_customer_count[y]=dict_all_customer_count[y]+1
            else:
                dict_all_customer_count[y]=1   
    except:
        dict_all_customer_count={"Problem olabilir Web Geliştirici ile irtibata geç":0}

    try:
        for i in warehouse_box.each():

            x= warehouse_db.objects.get( id= i.val()["warehouse_id"]).warehose_name
            if x in dict_all_warehouse_count:
                    
                dict_all_warehouse_count[x]= dict_all_warehouse_count[x]+1
            else:
                dict_all_warehouse_count[x]=1
    except:
        dict_all_warehouse_count={"Problem olabilir Web Geliştirici ile irtibata geç":0}

    
    try:
        for i in emplooyes.each():
            x=i.val()["department"]
        
            if x in dict_all_emplooye_count:
                    
                dict_all_emplooye_count[x]= dict_all_emplooye_count[x]+1
            else:
                dict_all_emplooye_count[x]=1
    except:
        dict_all_emplooye_count={"Problem olabilir Web Geliştirici ile irtibata geç":0}

    data_names=["dict_all_customer_count","dict_all_product_count","dict_all_warehouse_count","dict_all_emplooye_count"]
    return render(request,"graphs.html",{"dict_all_customer_count":dict_all_customer_count,"dict_all_product_count":dict_all_product_count,"dict_all_warehouse_count":dict_all_warehouse_count,"data_names":data_names,"dict_all_emplooye_count":dict_all_emplooye_count})


@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return render(request,"login.html")




@login_required(login_url="/")
def note_list(request):

    all_note=notes.objects.filter(note_user=request.user.get_username())

    if request.method == "POST":
            if 'delete_note' in  request.POST:
                   note_id = request.POST["note_id"]  
                   notes.objects.get(pk=note_id).delete()
                 
            elif 'add_note' in  request.POST:
            
                now = datetime.now()
                # dd/mm/YY H:M:S
                date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        
                note_head = request.POST["note_head"]
                note_body = request.POST["note_body"]
                save_note=notes(note_head=note_head,note_body=note_body,date_time=date_time,note_user=request.user.get_username())
                save_note.save()
                
            return  redirect("/note_list")
    else:
        return render(request, "note_list.html",{"notes": all_note})


@login_required(login_url="/")
def map(request):

    workers=db.child("users").child(request.user.get_username()).child("emplooyes").get()
    dict_workers= []  # databasedn  kullanıcıları çekip buraya eklicez
      
 
    for user in workers.each():
            dict_workers.append(user.val()) 
    print(dict_workers)
    return render(request,"map.html",{"workers_list":dict_workers})




@login_required(login_url="/")
def timeseries(request):
  
    return render(request,"timeseries.html")



@login_required(login_url="/")
def ordermanagement(request):

       workers=db.child("users").child(request.user.get_username()).child("emplooyes").order_by_child("department").equal_to("saha").get()
       dict_workers= {}  # databasedn  kullanıcıları çekip buraya eklicez
       for user in workers.each():
            dict_workers[user.key()]=user.val()
   


       order_list=db.child("users").child( request.user.get_username()).child("order").order_by_child("delivery_situation").equal_to("sipariş alındı").get()
       order_dict= {}  # databasedn  kullanıcıları çekip buraya eklicez
       for order in order_list.each():
            order_dict[order.key()]=order.val()
           


        #check boxları alıyoz
       if request.method == "POST":
            #gives list of id of inputs 
            list_of_input_ids=request.POST.getlist('orders_input')
            worker_input=request.POST["worker_inputs"]
            box_name=request.POST["box_name"]
            now = datetime.now()
                # dd/mm/YY H:M:S
            date_time = now.strftime("%d/%m/%Y %H:%M:%S")

            for i in list_of_input_ids:
                 db.child("users").child(request.user.get_username()).child("order").child(i).update({"delivery_situation":"depoda"})

            box={
                "box_name":box_name,
                "emplooye_id":worker_input,
                "delivery_option":0,
                "warehouse_id":"null",
                "boxed_date":date_time,
                "order_delivery_list":list_of_input_ids,
            }
            db.child("users").child(request.user.get_username()).child("warehouse_box").push(box)
            return redirect("/ordermanagement")


       return render(request,"ordermanagement.html",{"order_dict":order_dict,"dict_workers":dict_workers})



@login_required(login_url="/")
def warehouse(request):
     all_warehouse=warehouse_db.objects.filter(owener=request.user)
     warehouse_box=db.child("users").child(request.user.get_username()).child("warehouse_box").order_by_child("warehouse_id").equal_to("null").get()
     
  
     warehouse_box_dict={}
     try:
        for box in warehouse_box.each():
                product_price_list=[]
                product_amount_list=[]
                product_name_list=[]
                
                for j in box.val()["order_delivery_list"]:
                 
                   k=db.child("users").child(request.user.get_username()).child("order").child(j).get().val()
                   try:
                        product_id=k["product_id"]
                        obj=product.objects.get(id=product_id)
                        product_name_list.append(obj.product_head)
                        product_amount_list.append(k["product_amount"])
                        product_price_list.append(obj.product_price)
                   except:
                       pass
                
                box.val()["product_amount_list"]=product_amount_list
                box.val()["product_price_list"]=product_price_list
                box.val()["product_name_list"]=product_name_list

                warehouse_box_dict[box.key()]=box.val()
                #print("****",warehouse_box_dict)
     except:
         pass

     if request.method == "POST":

            if 'add_warehouse' in  request.POST:

    
                 aa=request.POST.getlist('order_box')
                 bb=request.POST["id_warehouse"]
                
                 for i in aa:
                     db.child("users").child(request.user.get_username()).child("warehouse_box").child(i).update({"warehouse_id":bb})
             
                 return  redirect("/warehouse")  
             


            elif 'pdf_view' in  request.POST:
               
                 
                
                 data = request.POST["fatura_detaya"]
               
                 data=ast.literal_eval(data)
                 order_list={"selo":[]}
              
                 for i in data["order_delivery_list"]:
                        value=db.child("users").child(request.user.get_username()).child("order").child(i).get()
                        order_list["selo"].append(value.val())
                                           
                
                 pdf = render_to_pdf('app/pdf_template.html', data ) 
                 return HttpResponse(pdf, content_type='application/pdf')
                 


            elif 'pdf_download' in  request.POST:
    
                    data = request.POST["fatura_detaya"]
                    data=ast.literal_eval(data)
                    order_list={"selo":[]}
                
                    for i in data["order_delivery_list"]:
                            zaza=db.child("users").child(request.user.get_username()).child("order").child(i).get()
                            order_list["selo"].append(zaza.val())

                    pdf = render_to_pdf('app/pdf_template.html', order_list)
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "Invoice_%s.pdf" %("12341231")
                    content = "attachment; filename='%s'" %(filename)
                    response['Content-Disposition'] = content
                    return response


            elif 'create_warehouse' in  request.POST:
                    
                    warehose_name = (request.POST["warehose_name"]).lower()
                    user_first_name = request.POST["user_first_name"]
                    user_last_name = request.POST["user_last_name"]
                    username = request.POST["username"]
                    password = request.POST["password"]
                    confirm_password = request.POST["confirm_password"]
                    

                    if(password==confirm_password):
                    

                            username=request.user.get_username()+"."+username
                            worker={"first_name":user_first_name,"last_name":user_last_name,"department":"depo","mail":username,
                            "latitude":"latitude","longitude":"longitude","order_delivery_list":"order_delivery_list" }
                            db.child("users").child(request.user.get_username()).child("emplooyes").push(worker)
                            #authentication.create_user_with_email_and_password(username,password)

                            password=pbkdf2_sha256.encrypt(password,rounds=12000,salt_size=32)
                            save_warehouse_db=warehouse_db(username=username,warehose_name=warehose_name,user_first_name=user_first_name,user_last_name=user_last_name,password=password,owener=request.user)
                            save_warehouse_db.save()
                        
                    return  redirect("/warehouse")

   
     return render(request,"warehouse.html",{"all_warehouse":all_warehouse,"warehouse_box_dict":warehouse_box_dict})



@login_required(login_url="/")
def department(request):
     return render(request,"department.html")



def selection(request):
     return render(request,"selection/selection.html")





def customer(request):


   if request.method == "POST":

            if 'add_customer' in  request.POST:
               customer_name=request.POST["customer_name"]
               custemer_address=request.POST["custemer_address"]
               customer_detail=request.POST["customer_detail"]

               Customer(name=customer_name,product_user=request.user.get_username(),custemer_address=custemer_address,customer_detail=customer_detail).save()
               customer={"customer_name":customer_name,"customer_address":custemer_address}
               db.child("users").child(request.user.get_username()).child("customer").push(customer)
             

            if "delete_customer"  in  request.POST:
                customer_id=request.POST["customer_id"]
                Customer.objects.get(pk=customer_id).delete()

            return redirect("/customer")
   obj_list=Customer.objects.filter(product_user=request.user.get_username())
   context={
     
       "obj_list":obj_list
   }
   return render(request,"customer.html",context)




def order_location(request):
     workers=db.child("users").child(request.user.get_username()).child("order").get()
     order_list= []  # databasedn  kullanıcıları çekip buraya eklicez
      
 
     for user in workers.each():
            order_list.append(user.val()) 

    


     return render(request,"order_location.html",{"order_list":order_list})





from django.shortcuts import render
import plotly.express as px
from plotly.offline import plot
from plotly.graph_objs import Scatter
import pandas as pd
import urllib

def selo():

        print("**************geldi")
        period=106

        rng = pd.date_range('20190731', periods=period)
        #df = pd.DataFrame({'date': rng})  
        
        from random import seed
        from random import randint
        # seed random number generator
        seed(1)#bu alınan değeri sabit tutuyo bunu yapmazsan her run edince değer değişir
        # generate some integers
        numbers=[]
        for _ in range(period):
            value = randint(5, 16)
            numbers.append(value)

        #df["order"]=x
        df=pd.read_csv(r'C:/Users\selah\Desktop\DIKENLI_YOL\Steela\steela/orderapp\static/csv\selo.csv')

        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)

        df.plot(figsize=(20,10))
        # Plot a 30 day moving average
        df.rolling(window=30).mean()['new_deaths_per_million'].plot()
          #plottinG 2D
      
        #plottinG 2D
        plot_div = plot(px.scatter(df, x="new_deaths_per_million", y="date",size_max=20,
                        template="simple_white",width=900, height=600),
                    output_type='div')
        return plot_div
