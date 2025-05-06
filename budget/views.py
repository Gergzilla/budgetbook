from django.shortcuts import render
from django.http import HttpResponseRedirect

from database.models import Transaction, Category
from .forms import EditTransaction

def landing_page(request):
    return render(request, "budget/landing.html")

def summary_page(request):
    data = ""
    error_message = ""
    summary_range = request.GET.get("summary_range", "Jan")
    print(summary_range)
    for key, value in request.GET.items():
        print(key,":",value)
    try:
        # The database querry needs to be called from here to return 'data'
        data = Transaction.objects.filter(charge_date__icontains=summary_range)
        # data = Transaction.objects.all() # testing all data
        myfields = Transaction._meta.get_fields()
        # print(dir(data))
        #this try/except was for troubleshooting date format issues and isn't currently needed
        # try:
        #     # for key, value in data:
        #     #     print("Key: ",key, "\n", "Value: ", value)
        #     print(dir(data))
        # except Exception as e:
        #     print(f"Couldn't print data.date because: {e}")
        print("All Fields: ",myfields)
    except Exception as e:
        error_message = f"Error retrieving data due to :{e}"
        data = ""
    if request.headers.get("HX-Request"):
        print("HX-Reuqest in header")
        return render(request, "budget/partials/_summary_view.html", {"data":data,
                                                                      "summary_range":summary_range,
                                                                      "error_message":error_message})
        # return render(request,"budget/summary.html")
    else:
        print("No HX-Request in header")
        return render(request,"budget/summary.html", {"data":data, 
                                                      "summary_range":summary_range,
                                                      "error_message":error_message})

def editor_page(request):
    data = ""
    error_message = ""
    edit_range = request.GET.get("edit_range", "Jan")
    
    try:
        data = Transaction.objects.filter(charge_date__icontains=edit_range)
        print("I tried")
    except Exception as e:
        error_message = f"Database query failed due to: {e}"
        print(error_message)
        data=""
    if request.method == "POST":
        form = EditTransaction(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/editor/")
    else:
        form = EditTransaction()
    if request.headers.get("HX-Request"):
        print("DEBUG: HX-Request in header")
        return render(request, "budget/partials/_editor_view.html", {"data":data,
                                                                     "edit_range":edit_range,
                                                                     "error_message":error_message})
    else:
        print("DEBUG: No HX-Request in header")
        return render(request, "budget/editor.html", {"data":data,
                                                      "edit_range":edit_range,
                                                      "error_message":error_message})
    
def report_page(request):
    return render(request, "budget/reports.html")