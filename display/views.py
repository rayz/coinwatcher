from operator import *

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .cryptodata import CryptoData
from .forms import AddCryptoForm, RemoveCryptoForm, UserRegistrationForm
from .models import Coin, Portfolio

crypto_data = CryptoData()


def index(request):
    return render(request, "display/index.html")


def register(request):
    # if user is already logged in, go to list page
    if request.user.is_authenticated:
        return redirect("list-page")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # get the username and password
            username = request.POST["username"]
            password = request.POST["password1"]
            # authenticate user then login
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, user)
            return redirect("list-page")
    else:
        form = UserRegistrationForm()
    return render(request, "display/register.html", {"form": form})


# list cryptocurrencies in table
def listcoins(request):
    c_list = crypto_data.get_currencies()
    currencies = dict()

    # key for currencies is going to be the id from coingecko api
    for i in range(len(c_list)):
        currencies[c_list[i]["id"]] = {
            "name": c_list[i]["name"],
            "market_cap": c_list[i]["market_cap"],
            "total_volume": c_list[i]["total_volume"],
            "current_price": c_list[i]["current_price"],
            "market_cap_rank": c_list[i]["market_cap_rank"],
        }

    # sort currencies by market cap rank
    currencies = dict(
        sorted(currencies.items(), key=lambda x: getitem(x[1], "market_cap_rank"))
    )
    context = {"currencies": currencies}
    return render(request, "display/list.html", context)


# only allow user to go to portfolio page if logged in
@login_required(login_url="login")
def portfolio(request):
    portfolio = Portfolio.objects.get(user=request.user)
    coins = Coin.objects.filter(owner=portfolio)
    holdings = {}
    for coin in coins:
        if coin.amount_holding > 0:
            data = crypto_data.get_coin_price(coin.name_of_coin)
            price = data[coin.name_of_coin]["usd"]
            value_held = price * float(coin.amount_holding)
            holdings[coin.name_of_coin] = {
                "name": coin.name_of_coin.capitalize(),
                "current_price": data[coin.name_of_coin]["usd"],
                "owned": float(coin.amount_holding),
                "value": value_held,
            }

    context = {"holdings": holdings}
    return render(request, "display/portfolio.html", context)


def test(request):
    return HttpResponse("<h1> test page </h1>")


def coin(request, cryptoname=""):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.POST.get("add"):
                form = AddCryptoForm(request.POST)
                if form.is_valid():
                    portfolio = Portfolio.objects.get(user=request.user)
                    add_amount = form.cleaned_data.get("add_amount")

                    try:
                        c = Coin.objects.get(owner=portfolio, name_of_coin=cryptoname)
                        c.amount_holding += add_amount
                        c.save()
                        print(
                            c.amount_holding, cryptoname, "is being held by", portfolio
                        )
                    except Coin.DoesNotExist:
                        Coin.objects.create(
                            owner=portfolio,
                            name_of_coin=cryptoname,
                            amount_holding=add_amount,
                        )
            else:
                form = RemoveCryptoForm(request.POST)
                if form.is_valid():
                    portfolio = Portfolio.objects.get(user=request.user)
                    remove_amount = form.cleaned_data.get("remove_amount")

                    try:
                        c = Coin.objects.get(owner=portfolio, name_of_coin=cryptoname)
                        if c.amount_holding >= remove_amount:
                            c.amount_holding -= remove_amount
                            c.save()
                        print(
                            c.amount_holding, cryptoname, "is being held by", portfolio
                        )
                    except Coin.DoesNotExist:
                        print("user does not have specifed amount in their portfolio")
                        pass
            return redirect("portfolio-page")
        else:
            return redirect(register)

    try:
        coin_data = crypto_data.get_coin_info(cryptoname)
    except ValueError:
        return HttpResponse(f"<h1> {cryptoname} not found </h1>")
    add_form = AddCryptoForm()
    remove_form = RemoveCryptoForm()
    context = {
        "id": coin_data["id"].capitalize(),
        "description": coin_data["description"]["en"],
        "add_form": add_form,
        "remove_form": remove_form,
    }
    return render(request, "display/coin.html", context)
