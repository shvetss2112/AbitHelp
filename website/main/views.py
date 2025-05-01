from django.shortcuts import render
from events.models import Event
from django.core.paginator import Paginator


def index(request):
    return render(request, 'index.html')


def about_us(request):
    return render(request, 'about_us.html')


def my_news(request):
    news = Event.objects.all().order_by('-created_at')
    paginator = Paginator(news, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_news.html', {"page_obj": page_obj})
