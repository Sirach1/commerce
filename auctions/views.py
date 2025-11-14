from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User, Auction, Category, Bid, Watch, Comment


def index(request, category_id):
    listings = Auction.objects.all()
    return render(request, "auctions/index.html", {"auctions": listings})


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


@login_required
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def auction(request, id):
    auction = Auction.objects.get(id=id)
    bids = Bid.objects.filter(auction=auction)
    if request.method == "GET":
        if bids.exists():
            current_price = bids.order_by("-amount").first().amount
        else:
            current_price = auction.init_bid
        return render(
            request,
            "auctions/auction.html",
            {
                "auction": auction,
                "publisher": request.user == auction.user,
                "current_price": current_price,
            },
        )

    # Bidding Feat.
    elif request.method == "POST" and "bid" in request.POST:
        pending_bid = float(request.POST["bid"])
        if not bids.exists():
            if pending_bid > auction.init_bid:
                new_bid = Bid(amount=pending_bid, user=request.user, auction=auction)
                new_bid.save()
                return render(
                    request,
                    "auctions/auction.html",
                    {
                        "auction": auction,
                        "message": "Bid placed successfully.",
                    },
                )
        else:
            current_price = bids.order_by("-amount").first().amount
            if pending_bid > current_price:
                new_bid = Bid(amount=pending_bid, user=request.user, auction=auction)
                new_bid.save()
                return render(
                    request,
                    "auctions/auction.html",
                    {
                        "auction": auction,
                        "message": "Bid placed successfully.",
                    },
                )

        return render(
            request,
            "auctions/auction.html",
            {
                "auction": auction,
                "message": "Your bid must be higher than the current biding price.",
            },
        )
    else:
        if "watchlist" in request.POST:
            # add
            return render(
                request,
                "auctions/auction.html",
                {
                    "auction": auction,
                    "message": "This acution has been watchlisted.",
                },
            )
        else:
            # remove
            return render(
                request,
                "auctions/auction.html",
                {
                    "auction": auction,
                    "message": "This acution has been removed from your watchlist.",
                },
            )


@login_required
def create(request):
    if request.method == "GET":
        return render(
            request, "auctions/create.html", {"categories": Category.objects.all()}
        )
    else:
        categories = request.POST.getlist("categories")
        new_listing = Auction(
            title=request.POST["title"],
            desc=request.POST["desc"],
            init_bid=request.POST["init_bid"],
            img=request.POST["img"],
            user=request.user,
        )
        new_listing.save()
        for cat_id in categories:
            cat_id = Category.objects.get(id=cat_id)
            new_listing.categories.add(cat_id)
        new_listing.save()
        return HttpResponseRedirect(reverse("index"))


def watchlist(request):
    pass


def category(request):
    categories = Category.objects.all()
    if request.method == "GET":
        return render(request, "auctions/category.html", {"categories": categories})
