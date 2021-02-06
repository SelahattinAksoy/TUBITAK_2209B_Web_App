from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from . import views

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


data = {
	"company": "Dennnis Ivanov Company",
	"address": "123 Street name",
	"city": "Vancouver",
	"state": "WA",
	"zipcode": "98663",


	"phone": "555-555-2345",
	"email": "youremail@dennisivy.com",
	"website": "dennisivy.com",
	}

#Opens up page as PDF
class ViewPDF(View):
	def get(self, request, *args, **kwargs):


		print("*********",data)
		pdf = render_to_pdf('app/pdf_template.html', data)
		return HttpResponse(pdf, content_type='application/pdf')




class DownloadPDF(View):
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
		df=pd.read_csv("static/csv/selo.csv")

		df.set_index('date', inplace=True)
		df.index = pd.to_datetime(df.index)


		df.plot(figsize=(20,10))
		# Plot a 30 day moving average
		df.rolling(window=30).mean()['new_deaths_per_million'].plot()
'''
#Automaticly downloads to PDF file
class DownloadPDF(View):
	
	def get(self, request, *args, **kwargs):
		
		pdf = render_to_pdf('app/pdf_template.html', data)

		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Invoice_%s.pdf" %("12341231")
		content = "attachment; filename='%s'" %(filename)
		response['Content-Disposition'] = content
		return response

'''
