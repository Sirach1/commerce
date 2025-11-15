from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User, Auction, Category, Bid, Watch, Comment


def index(request, category_id=None):
    if category_id:
        category = Category.objects.get(id=category_id)
        listings = Category.objects.get(id=category_id).auctions.all()
    elif request.resolver_match.url_name == "closed_index":
        listings = Auction.objects.filter(is_active=False)
    else:
        listings = Auction.objects.filter(is_active=True)

    return render(
        request,
        "auctions/index.html",
        {"auctions": listings, "category": category if category_id else None},
    )


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

@login_required
def auction(request, id):
    auction = Auction.objects.get(id=id)
    current_price = auction.current_price()
    is_watchlisted = auction.is_watchlisted(request.user)
    if request.method == "GET":
        return render(
            request,
            "auctions/auction.html",
            {"auction": auction, "watchlist": is_watchlisted},
        )

    # Bidding Feat.
    elif "bid" in request.POST:
        pending_bid = float(request.POST["bid"])
        if pending_bid > current_price:
            new_bid = Bid(amount=pending_bid, user=request.user, auction=auction)
            new_bid.save()
            return render(
                request,
                "auctions/auction.html",
                {
                    "auction": auction,
                    "message": "Bid placed successfully.",
                    "watchlist": is_watchlisted,
                },
            )
        else:
            return render(
                request,
                "auctions/auction.html",
                {
                    "auction": auction,
                    "message": "Your bid must be higher than the current biding price.",
                    "watchlist": is_watchlisted,
                },
            )
    # Close auction
    elif "close" in request.POST:
        auction = Auction.objects.get(id=request.POST["auction_id"])
        auction.is_active = False
        auction.save()
        listings = Auction.objects.filter(is_active=False)
        return render(
            request,
            "auctions/index.html",
            {"auctions": listings, "category":  None},
        )
    # Watchlist
    elif "watchlist" in request.POST:
        if "watchlist" in request.POST:
            # add
            watchlist = Watch(user=request.user, auction=auction)
            watchlist.save()
            is_watchlisted = auction.is_watchlisted(request.user)
            return render(
                request,
                "auctions/auction.html",
                {
                    "auction": auction,
                    "message": "This acution has been watchlisted.",
                    "watchlist": is_watchlisted,
                },
            )
    # Unwatchlist
    elif "unwatchlist" in request.POST:
        # remove
        watchlist = request.user.watchlists.filter(auction=auction)
        watchlist.delete()
        is_watchlisted = auction.is_watchlisted(request.user)
        return render(
            request,
            "auctions/auction.html",
            {
                "auction": auction,
                "message": "This acution has been removed from your watchlist.",
                "watchlist": is_watchlisted,
            },
        )
    else:
        comment = Comment(
            text=request.POST["comment"], user=request.user, auction=auction
        )
        comment.save()

        return render(
            request,
            "auctions/auction.html",
            {
                "auction": auction,
                "message": "This acution has been removed from your watchlist.",
                "watchlist": is_watchlisted,
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

@login_required
def watchlist(request):
    if request.method == "GET":
        watchlist = request.user.watchlists.all()
        return render(request, "auctions/watchlist.html", {"list": watchlist})

@login_required
def category(request):
    categories = Category.objects.all()
    if request.method == "POST":
        new_category = Category(
            title=request.POST["title"], thumbnail=request.POST["thumbnail"]
        )
        new_category.save()
    return render(request, "auctions/category.html", {"categories": categories})
