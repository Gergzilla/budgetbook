from django.shortcuts import render

def landing_page(request):
    return render(request, "budget/landing.html")

def summary_page(request):
    return render(request,"budget/summary.html")