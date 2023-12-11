from django.shortcuts import redirect, render
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# first need to pip install requests
import requests
from django.conf import settings

from .forms import *
from .filters import OrderFilter
from .models import *
from .decorators import *

# Create your views here.


@login_required(login_url="login")
# @allowedUsers(allowedGroups=["admin"])
@forAdmins
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    t_orders = orders.count()
    d_orders = orders.filter(status="Delivered").count()
    p_orders = orders.filter(status="Pending").count()
    in_orders = orders.filter(status="In Progress").count()
    out_orders = orders.filter(status="Out for delivery").count()
    orders = Order.objects.all()
    context = {
        "customers": customers,
        "orders": orders,
        "t_lrders": t_orders,
        "d_orders": d_orders,
        "p_orders": p_orders,
        "in_orders": in_orders,
        "out_orders": out_orders,
    }
    return render(request, "bookstore/dashboard.html", context)


@login_required(login_url="login")
@forAdmins
def books(request):
    books = Book.objects.all()
    return render(request, "bookstore/books.html", {"books": books})


@login_required(login_url="login")
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    # order_set: get all the orders of the customer (using the forgein key in Order model)
    orders = customer.order_set.all()
    num_orders = orders.count()
    # queryset: to search in the orders of the customer
    searchFilter = OrderFilter(request.GET, queryset=orders)
    orders = searchFilter.qs
    context = {
        "customer": customer,
        "orders": orders,
        "num_orders": num_orders,
        "myFilter": searchFilter,
    }
    return render(request, "bookstore/customer.html", context)


@login_required(login_url="login")
@allowedUsers(allowedGroups=["admin"])
def create(request, pk):
    OrderFormSet = inlineformset_factory(
        Customer,
        Order,
        fields=("book", "status"),
        extra=8,
    )
    customer = Customer.objects.get(id=pk)
    # instance: to create a new order for the customer, queryset: to not show any orders
    # queryset=Order.objects.none(): to not show any orders (my orders)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == "POST":
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect("home")
    context = {"formset": formset}
    return render(request, "bookstore/my_order_form.html", context)


@login_required(login_url="login")
@allowedUsers(allowedGroups=["admin"])
def update(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == "POST":
        # print("Printing POST:", request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("/")
    context = {"form": form}
    return render(request, "bookstore/order_form.html", context)


@login_required(login_url="login")
@allowedUsers(allowedGroups=["admin"])
def delete(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect("/")
    context = {"item": order}
    return render(request, "bookstore/delete_form.html", context)


@notLoggedUsers
def register(request):
    form = CreateNewUser()
    if request.method == "POST":
        form = CreateNewUser(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get("g-recaptcha-response")
            data = {
                "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            }
            # requests.post: to send a post request to the google recaptcha api to verify the answers
            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data,
            )
            result = r.json()
            if result["success"]:
                form.save()
                username = form.cleaned_data.get("username")
                messages.success(request, "Account was created for " + username)
                return redirect("login")
            else:
                messages.error(request, "Invalid reCAPTCHA. Please try again.")
    context = {"form": form}
    return render(request, "bookstore/register.html", context)


@notLoggedUsers
def UserLogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Username or Password is incorrect")
    context = {}
    return render(request, "bookstore/login.html", context)


@login_required(login_url="login")
def userLogout(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
@allowedUsers(allowedGroups=["customer"])
def userProfile(request):
    orders = request.user.customer.order_set.all()
    t_orders = orders.count()
    d_orders = orders.filter(status="Delivered").count()
    p_orders = orders.filter(status="Pending").count()
    in_orders = orders.filter(status="In Progress").count()
    out_orders = orders.filter(status="Out for delivery").count()
    orders = Order.objects.all()
    context = {
        "orders": orders,
        "t_lrders": t_orders,
        "d_orders": d_orders,
        "p_orders": p_orders,
        "in_orders": in_orders,
        "out_orders": out_orders,
    }
    return render(request, "bookstore/profile.html", context)


# form.as_p: to show the form as paragraphs
@login_required(login_url="login")
def profileInfo(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {"form": form}
    return render(request, "bookstore/profile_info.html", context)
