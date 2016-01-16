from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import stripe
import datetime
import arrow
from django.template.context_processors import csrf
from accounts.forms import UserRegistrationForm, UserLoginForm



"""def register(request, register_form=UserRegistrationForm):

    if request.method == 'POST':

        form = register_form(request.POST)
        if form.is_valid():

            form.save()
            user = auth.authenticate(email=request.POST.get('email'), password=request.POST.get('password1'))

            if user:

                messages.success(request, "You have successfully registered")

                var = request.POST.get('email')
                message = 'Welcome ' + var + ', you are now registered!'



                send_mail('We are social', message, 'ronanhiggins8@gmail.com', ['ronan.higgins@ucdconnect.ie'], fail_silently=False)

                return redirect(logout)

            else:

                messages.error(request, "unable to log you in!")

    else:

        form = register_form()

    args = {'form': form}
    args.update(csrf(request))

    return render(request, 'register.html', args)"""

stripe.api_key = settings.STRIPE_SECRET

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                customer = stripe.Charge.create(
                    email =form.cleaned_data['email'],
                    card = form.cleaned_data['stripe_id'],
                    plan = 'REG_MONTHLY',
                )
            except stripe.error.CardError, e:
                messages.error(request, "Your card was declined, fool!")

            if customer.paid:

                user= form.save()
                user.stripe_id = customer.id
                user.subscription_end = arrow.now().replace(weeks=+4).datetime
                user.save()

                user = auth.authenticate(email=request.POST.get('email'),
                                         password=request.POST.get('password1'))

                if user:
                    auth.login(request, user)
                    messages.success(request, "You have successfully registered")
                    return redirect(reverse('profile'))

                else:
                    messages.error(request, "unable to log you in at this time!!!")
            else:
                messages.error(request, "We were unable to take a payment with that card!")

    else:
        today = datetime.date.today()
        form = UserRegistrationForm(initial={'expiry_month': today.month,
                                             'expiry_year': today.year})

    args = {'form': form, 'publishable': settings.STRIPE_PUBLISHABLE}
    args.update(csrf(request))

    return render(request, 'register.html', args)


@login_required(login_url='/accounts/login/')
def cancel_subscription(request):

    try:
        customer = stripe.Customer.retrieve(request.user.stripe_id)

        customer.cancel_subscription(at_period_end=True)

    except Exception, e:
        messages.error(request, e)


    return redirect('profile')






def login(request, success_url=None):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            user = auth.authenticate(email=request.POST.get('email'), password=request.POST.get('password'))

            if user is not None:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")
                return redirect(reverse('profile'))
            else:

                form.add_error(None, "Your email or password was not recognised")

    else:

        form = UserLoginForm()

    args = {'form':form}
    args.update(csrf(request))
    return render(request, 'login.html', args)


@login_required(login_url='/accounts/login/')
def profile(request):
    return render(request, 'profile.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out')
    return render(request, 'index.html')


def send_email(request):


        if request.method == 'POST':

            emailinput = request.POST.get('textfield', None)
            address = request.POST.get('address', None)

            print emailinput

            send_mail('We are social', emailinput, 'ronanhiggins8@gmail.com', [address], fail_silently=False)
            messages.error(request, "Your mail has been sent")

        return render(request, 'index.html')










