from django.shortcuts import render
from events.models import Event
from django.core.paginator import Paginator
from django.db.models import Q


def index(request):
    return render(request, 'index.html')


def about_us(request):
    return render(request, 'about_us.html')


def my_news(request):
    search_term = request.GET.get("search")
    queryset = Event.objects

    if search_term:
        queryset = queryset.filter(
            Q(content__icontains=search_term) | Q(title__icontains=search_term)
        )

    queryset = queryset.order_by('-created_at')

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_news.html', {"page_obj": page_obj, "search_term": search_term})


def news_detail(request, id):
    news = Event.objects.filter(id=id).first()
    return render(request, 'news_detail.html', {"news": news})
