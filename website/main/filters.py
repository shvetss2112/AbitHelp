import django_filters
from django.db.models import Q
from events.models import Event


class EventFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', input_formats=["%d.%m.%Y"])
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', input_formats=["%d.%m.%Y"])
    resource = django_filters.CharFilter(field_name='source__name', lookup_expr='iexact')
    must_include = django_filters.CharFilter(method='filter_must_include')
    exclude = django_filters.CharFilter(method='filter_exclude')
    include_any = django_filters.CharFilter(method='filter_include_any')

    class Meta:
        model = Event
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(content__icontains=value))

    def filter_must_include(self, queryset, name, value):
        for word in value.split():
            queryset = queryset.filter(Q(title__icontains=word) | Q(content__icontains=word))
        return queryset

    def filter_exclude(self, queryset, name, value):
        for word in value.split():
            queryset = queryset.exclude(Q(title__icontains=word) | Q(content__icontains=word))
        return queryset

    def filter_include_any(self, queryset, name, value):
        q = Q()
        for word in value.split():
            q |= Q(title__icontains=word) | Q(content__icontains=word)
        return queryset.filter(q)
