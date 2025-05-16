from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def calendar(request):
    return render(request, 'calendar.html')
