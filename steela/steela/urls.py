"""steela URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from orderapp.views import index
from orderapp.views import login
from orderapp.views import main
from orderapp.views import products
from orderapp.views import orderlist
from orderapp.views import emplooyes
from orderapp.views import graphs
from orderapp.views import register
from orderapp.views import logout
from orderapp.views import note_list
from orderapp.views import map
from orderapp.views import timeseries
from orderapp.views import ordermanagement
from orderapp.views import warehouse
from orderapp.views import department
from orderapp.views import selection
from orderapp.views import customer
from orderapp.views import order_location

from orderapp.views_warehouse import warehouse_login
from orderapp.views_warehouse import main_warehouse
from orderapp.views_warehouse import orderlist_warehouse
from orderapp.views_warehouse import warehouse_logout
from orderapp.views_warehouse import check_product_warehouse

from  orderapp import pdf_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('login/', login),
    path('main/', main),
    path('products/', products),
    path('orderlist/', orderlist),
    path('emplooyes/', emplooyes),
    path('graphs/', graphs),
    path('register/', register),
    path('logout/', logout),
    path('note_list/', note_list),
    path('map/', map),
    path('customer/', customer),
    path('timeseries/', timeseries),
    path('ordermanagement/', ordermanagement),
    path('warehouse/', warehouse),
    path('department/', department),
    path('selection/', selection),
    path('order_location/', order_location),

    path('warehouse_login/',warehouse_login),
    path('main_warehouse/',main_warehouse),
    path('orderlist_warehouse/', orderlist_warehouse),
    path('warehouse_logout/', warehouse_logout),
    path('check_product_warehouse/', check_product_warehouse),
    



    path('pdf_view/', pdf_view.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download/', pdf_view.DownloadPDF.as_view(), name="pdf_download"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #for qrcode 