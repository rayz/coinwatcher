from django.shortcuts import render, redirect
from django.http import HttpResponse
from .cryptodata import CryptoData
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, AddCryptoForm
from .models import Portfolio, Coin
from operator import *



def index(request):
    return render(request, 'display/index.html')


def register(request):
    #if user is already logged in, go to list page
    if request.user.is_authenticated:
        return redirect('list-page')

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            #get the username and password
            username = request.POST['username']
            password = request.POST['password1']
            #authenticate user then login
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'],)
            login(request, user)
            return redirect('list-page')
    else:
        form = UserRegistrationForm()
    return render(request, 'display/register.html', {'form':form})

#list cryptocurrencies in table
def listcoins(request):
    crypto_data = CryptoData()
    c_list = crypto_data.get_currencies()
    currencies = dict()
    for i in range(25):
        currencies[c_list[i]['id']] = {
            'name' : c_list[i]['name'],
            'market_cap' : c_list[i]['market_cap'],
            'total_volume' : c_list[i]['total_volume'],
            'current_price' : c_list[i]['current_price'],
            'market_cap_rank': c_list[i]['market_cap_rank']
        }

	#sort currencies by market cap rank
    currencies = dict(sorted(currencies.items(),key=lambda x:getitem(x[1],'market_cap_rank')))
    context = {
        'currencies' : currencies
    }
    return render(request, 'display/list.html', context)


def test(request):
	return HttpResponse('<h1> test page </h1>')


def coin(request, cryptoname =''):
    if request.method == "POST":
        form = AddCryptoForm(request.POST)
        if form.is_valid():
            portfolio = Portfolio.objects.get(user=request.user)
            c = Coin.objects.filter(owner=portfolio, name_of_coin = cryptoname)[0]
            c.amount_holding += form.cleaned_data.get('add_amount')
            c.save()
            print("has",c.amount_holding,cryptoname)
        return redirect('test-page')

    crypto_data = CryptoData()
    c_list = crypto_data.get_currencies()
    try:
        coin_data = crypto_data.get_coin_info(cryptoname)
    except ValueError:
        return HttpResponse(f'<h1> {cryptoname} not found </h1>')
    form = AddCryptoForm()
    context = {
        'id' : coin_data['id'].capitalize(),
        'description' : coin_data['description']['en'],
        'form' : form
    }
    return render(request, 'display/coin.html', context)

#only allow user to go to portfolio page if logged in
@login_required(login_url='login')
def portfolio(request):
    return render(request, 'display/portfolio.html')
