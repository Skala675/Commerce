from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listings, Bids, Comments, Category


class Comment(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']

    comment = forms.CharField(
        max_length = 500,
        label=False,
        widget=forms.Textarea(attrs={'placeholder' : 'Write a question..', 'rows' : 1, 'cols' : 100, 'autocomplete' : 'off', 'class' : "product-bid-button"}),
        validators=[MaxLengthValidator(limit_value=500, message="Character limit reached")]
    )

class Bid(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ['bid']
    
    bid = forms.DecimalField(
        max_digits = 10,
        label = False,
        decimal_places = 2,
        widget=forms.NumberInput(attrs={'min': 0.01, 'class' : "product-bid-button"}),
        validators=[MinValueValidator(limit_value=0.01, message=f"Bid must be at least $0.01")]
    )


class Publish(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'bid', 'image', 'category']
    
    title = forms.CharField(
        max_length=100,
        label=False,
        widget=forms.TextInput(attrs={'placeholder' : 'Enter title', 'autocomplete' : 'off', "class" : "form-control", "autofocus" : ""}),
        validators=[MaxLengthValidator(limit_value=100, message="Character limit reached")]
    )

    description = forms.CharField(
        max_length=2000,
        label=False,
        widget=forms.Textarea(attrs={'placeholder' : 'Enter description', 'rows' : 5, 'cols' : 70, "class" : "form-control"}),
        validators=[MaxLengthValidator(limit_value=2000, message="Character limit reached")]
    )

    bid = forms.DecimalField(
        max_digits = 10,
        label=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder' : 'Enter a initial bid', 'min': '0.01', "class" : "form-control"}),
        validators=[MinValueValidator(limit_value=0.01, message="Bid must be greater than 0")]
    )

    image = forms.URLField(
        required=False,
        label=False,
        widget=forms.TextInput(attrs={'placeholder' : 'Image URL', "class" : "form-control"})
    )

    category = forms.ChoiceField(
        choices=Category.choices,
        label=False,
        initial=Category.NOT_LISTED,
        widget=forms.Select(attrs={'class' : 'form-select', "class" : "form-control"})
    )


def index(request):
    categories = Category.choices
    category_products = {}
    
    for category in categories:
        products = Listings.objects.filter(category=category[0])[:10]
        category_products[category[-1]] = products

    return render(request, "auctions/index.html", {
        "category_products" : category_products
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

@login_required(redirect_field_name="login")
def publish(request):
    if request.method == "POST":
        form = Publish(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    listing = form.save(commit=False)
                    listing.user = request.user
                    listing.save()
            except Exception as e:
                return render(request, "auctions/listing.html", {
                    "message": str(e),
                    "form" : form
                })

            return HttpResponseRedirect(reverse("index"))
            
    else:
        form = Publish()

    return render(request, "auctions/listing.html", {
        'form': form
    })

def product(request, id):
    try:
        product = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/products.html", {
            'product': None
        })


    lastBid = product.bids.last().bid if product.bids.exists() else None
    comments = product.comments.all()

    if lastBid:
        formOffer = Bid(initial={'bid' : lastBid + 1})
        formOffer.fields['bid'].widget.attrs.update({'min': lastBid + 1})
        formOffer.fields['bid'].validators[0].limit_value = lastBid + 1
        formOffer.fields['bid'].validators[0].message = f"Bid must be at least ${lastBid + 1}"

    else:
        formOffer = Bid(initial={'bid' : product.bid})
        formOffer.fields['bid'].widget.attrs.update({'min': product.bid})
        formOffer.fields['bid'].validators[0].limit_value = product.bid
        formOffer.fields['bid'].validators[0].message = f"Bid must be at least ${product.bid}"


    formComment = Comment()

    return render(request, "auctions/products.html", {
        'product': product,
        'formOffer' : formOffer,
        'comments' : comments,
        'formComment' : formComment
    })


@login_required(redirect_field_name="login")
def watchlist(request, id):
    try:
        product = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/products.html", {
            'product': None
        })

    if request.user in product.watchlist.all():
        product.watchlist.remove(request.user)
    else:
        product.watchlist.add(request.user)
    
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('watchlistPage'))
    
    return HttpResponseRedirect(reverse('product', args=[id]))


@login_required(redirect_field_name="login")
def closeAuction(request, id):
    try:
        auction = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/products.html", {
            'product': None
        })

    if request.user == auction.user and not auction.is_closed:
        auction.is_closed = True
        auction.winner = auction.bids.last().user
        auction.save()

    return HttpResponseRedirect(reverse('product', args=[id]))


@login_required(redirect_field_name="login")
def offer(request, id):
    try:
        auction = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/products.html", {
            'product': None
        })

    form = Bid(request.GET)
    if form.is_valid():
        currentBid = form.cleaned_data.get('bid')
        
        if auction.bids.all():
            if currentBid <= auction.bids.last().bid:
                return HttpResponse(content="Your bid must be greater than the current bid.")
        else:
            if currentBid < auction.bid:
                return HttpResponse(content="Your bid must be at least equal to the initial bid.")
    
        try:
            with transaction.atomic():
                bid = form.save(commit=False)
                bid.listing = auction
                bid.user = request.user
                bid.save()
        except Exception as e:
            return render(request, "auctions/products.html", {
                "message": str(e),
                "form" : form
            })
        
    else:
        comments = auction.comments.all()
        return render(request, "auctions/products.html", {
            'product': auction,
            'formOffer' : form,
            'comments' : comments,
            'formComment' : Comment()
        })
        
    return HttpResponseRedirect(reverse('product', args=[id]))


@login_required(redirect_field_name="login")
def comment(request, id):
    try:
        auction = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/products.html", {
            'product': None
        })

    form = Comment(request.GET)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.listing = auction
        comment.user = request.user
        comment.save()
    else:
        lastBid = auction.bids.last()
        formOffer = Bid(initial={'bid' : lastBid.bid + 1}, min_value = lastBid.bid + 1) if lastBid else Bid(initial={'bid' : auction.bid}, min_value = auction.bid)
        comments = auction.comments.all()
        return render(request, "auctions/products.html", {
            'product': auction,
            'formOffer' : formOffer,
            'comments' : comments,
            'formComment' : form
        })
    
    return HttpResponseRedirect(reverse('product', args=[id]))


@login_required(redirect_field_name="login")
def watchlistPage(request):
    auctions = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        'watchlist' : auctions
    })


def category(request, cat):
    code = get_category_code(cat)

    if code is None:
        raise Http404("The category does not exist.")   
     
    auctions = Listings.objects.filter(category=code)
    categories = Category.choices

    return render(request, "auctions/category.html", {
        "auctions" : auctions,
        "categories" : categories
    })


def get_category_code(category):
    for code, desc in Category.choices:
        if desc == category:
            return code
    return None