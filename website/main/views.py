from django.shortcuts import render, get_object_or_404, redirect
from events.models import Event, Resource, Subscription, Like
from django.contrib.auth.decorators import login_required
from .filters import EventFilter
from django.utils.decorators import method_decorator
from django_filters.views import FilterView


@login_required
def index(request):
    return render(request, 'index.html')


def about_us(request):
    return render(request, 'about_us.html')


class MyNewsView(FilterView):
    model = Event
    template_name = 'my_news.html'
    context_object_name = 'object_list'
    paginate_by = 10
    filterset_class = EventFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Event.objects.filter(source__subscribers__user=self.request.user).order_by('-created_at')
        return Event.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context["page_obj"]
        user = self.request.user
        if self.request.user.is_authenticated:
            context["liked_event_ids"] = set(
                Like.objects.filter(user=user, event__in=page_obj).values_list('event_id', flat=True)
            )
        context["resources"] = Resource.objects.all().order_by('name')
        return context


@login_required
def handle_like(request, event_id):
    ev = get_object_or_404(Event, id=event_id)
    like = Like.objects.filter(user=request.user, event=ev).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, event=ev)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def news_detail(request, id):
    news = Event.objects.filter(id=id).first()
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, event__id=id).exists()
    return render(request, 'news_detail.html', {"news": news, "is_liked": is_liked})


@login_required
def subscribe_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    Subscription.objects.get_or_create(user=request.user, resource=resource)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def subscriptions(request):
    subs = Subscription.objects.filter(user=request.user)
    return render(request, 'subscriptions.html', {"subscriptions": subs, "resources": Resource.objects.all().order_by('name')})


@login_required
def unsubscribe_resource(request, resource_id):
    if subscription := Subscription.objects.get(resource_id=resource_id, user=request.user):
        subscription.delete()
        return redirect('/subscriptions/')
