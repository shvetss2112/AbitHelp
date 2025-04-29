from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')

def my_news(request):
    return render(request, 'my_news.html')
