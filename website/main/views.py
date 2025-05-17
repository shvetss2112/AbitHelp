from django.shortcuts import render, get_object_or_404, redirect
from events.models import Event, Resource, Subscription, Like
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'index.html')


def about_us(request):
    return render(request, 'about_us.html')


@login_required
def my_news(request):
    search_term = request.GET.get("search")
    queryset = Event.objects.filter(source__subscribers__user=request.user)

    if search_term:
        queryset = queryset.filter(
            Q(content__icontains=search_term) | Q(title__icontains=search_term)
        )

    queryset = queryset.order_by('-created_at')

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    liked_event_ids = set(
        Like.objects.filter(user=request.user, event__in=page_obj.object_list).values_list('event_id', flat=True)
    )

    return render(
        request,
        'my_news.html',
        {
            "page_obj": page_obj,
            "search_term": search_term,
            "resources": Resource.objects.all(),
            "liked_event_ids": liked_event_ids
        }
    )


@login_required
def handle_like(request, event_id):
    ev = get_object_or_404(Event, id=event_id)
    like = Like.objects.filter(user=request.user, event=ev).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, event=ev)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def news_detail(request, id):
    news = Event.objects.filter(id=id).first()
    is_liked = Like.objects.filter(user=request.user, event__id=id)
    return render(request, 'news_detail.html', {"news": news, "is_liked": is_liked})


@login_required
def subscribe_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    Subscription.objects.get_or_create(user=request.user, resource=resource)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def subscriptions(request):
    subs = Subscription.objects.filter(user=request.user)
    return render(request, 'subscriptions.html', {"subscriptions": subs, "resources": Resource.objects.all()})


@login_required
def unsubscribe_resource(request, resource_id):
    if subscription := Subscription.objects.get(resource_id=resource_id, user=request.user):
        subscription.delete()
        return redirect('/subscriptions/')
