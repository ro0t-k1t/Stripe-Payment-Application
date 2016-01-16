from django.contrib import messages
from django.contrib import messages
from django.shortcuts import render
from .forms import ContactView
from django.core.mail import send_mail


def contact(request):

    if request.method == 'POST':

        form = ContactView(request.POST)
        if form.is_valid():
            our_form = form.save(commit=False)
            our_form.save()

            messages.add_message(request, messages.SUCCESS, 'Your message has been sent')

        return render(request, 'index.html')

    else:

        form = ContactView()
    return render(request, 'contact.html', {'form': form})





