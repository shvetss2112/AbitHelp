import django_filters
from django.db.models import Q
from .models import Event


class EventAPIFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    resource = django_filters.CharFilter(field_name='source__name', lookup_expr='iexact')
    date__gte = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date__lte = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    exclude = django_filters.CharFilter(method='filter_exclude')
    include_any = django_filters.CharFilter(method='filter_include_any')

    class Meta:
        model = Event
        fields = ['resource', 'date__gte', 'date__lte', 'exclude', 'include_any']

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(content__icontains=value))

    def filter_exclude(self, queryset, name, value):
	words = [word for word in value.split() if word]
	for word in words:
            queryset = queryset.exclude(Q(title__icontains=word) | Q(content__icontains=word))
        return queryset

    def filter_include_any(self, queryset, name, value):
        q = Q()
	words = [word for word in value.split() if word]
	for word in words:
		q |= Q(title__icontains=word) | Q(content__icontains=word)
        return queryset.filter(q)
