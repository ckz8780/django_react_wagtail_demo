from django.shortcuts import render

def frontend(request):
    context = {}
    template = 'frontend.html'
    return render(request, template, context)