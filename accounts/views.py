from django.shortcuts import render, redirect

from accounts.forms import CustomUserCreationForm


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, "register.html", {'form': form})
    return render(request, "register.html", context={"form": CustomUserCreationForm()})
