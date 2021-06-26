from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse
from .models import *
from project import settings
import random, string
from django.db import IntegrityError

def generate_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(7))

####### VIEWS ################################################
def index(request):
    return render(request, "index.html")

def create(request):
    if request.method == "GET":
        items = Item.objects.all()
        return render(request, "create.html", {
            "items": items
        })
    elif request.method == 'POST':
        code = generate_code()
        names = request.POST['array'].split(',')
        print(names)
        items = [Item.objects.get(name=name) for name in names]
        new_course = Course(code=code)
        new_course.save()
        for i, item in enumerate(items):
            new_course.items.add(item, through_defaults={'index': i})
        data = dict(request.POST)
        data.update({"code": code})
        return render(request, "create.html", data)

def explore(request):
    if request.method == 'GET':
        random_id = random.randint(2, Item.objects.count())
        item = Item.objects.get(id=random_id)
        print(item)
        return render(request, "explore.html", {
            "item":item
        })
    elif request.method == 'POST':
        return HttpResponseRedirect(reverse('course', args=[request.POST["code"]]))


def course(request, code, index=0):
    try:
        course = Course.objects.get(code=code)
        try:
            sequence = Sequence.objects.get(course=course, index=index)
            index+=1
            print(sequence.item)
            return render(request, "course.html", {
                "item":sequence.item, "code":code, "next_index":index
                })
        except:
            return render(request, "course_end.html")
    except:
        return render(request, "course_not_found.html")


def discussion(request, item_pk=2):
    # DISCUSSION POST ITEM_PK MUST BE GREATER THAN 1
    if request.method == 'GET':
        dps = DiscussionPost.objects.filter(item=Item.objects.get(id=item_pk))
        print(dps)
        item = Item.objects.get(id=item_pk)
        data = {"posts":dps, "item":item, "loggedIn": False}
        if "username" in request.session:
            loggedIn = True
            user = User.objects.get(username=request.session["username"])
            data.update({"loggedIn": loggedIn, "user": user})
        return render(request, "discussion.html", data)
    elif request.method == 'POST':
        if request.POST['type'] == 'li':
            try:
                user = User.objects.get(username=request.POST["username"])
                if request.POST["password"] == user.password:
                    request.session["username"] = request.POST["username"]
                    print('success')
            except User.DoesNotExist:
                print('user does not exist')
        elif request.POST['type'] == 'su':
            try:
                user = User(username=request.POST["username"], 
                            password=request.POST["password"],
                            name=request.POST["name"])
                user.save()
                request.session["username"] = request.POST["username"]
            except IntegrityError:
                print('duplicate user')
        elif request.POST['type'] == 'po':
            dp = DiscussionPost(item=Item.objects.get(id=item_pk), 
                                user=User.objects.get(username=request.session["username"]),
                                post=request.POST["textarea"])
            dp.save()
        return HttpResponseRedirect(reverse('discussion', args=[item_pk]))



def login(request):
    if request.method == 'GET':
        return render(request, 'test.html')
    elif request.method == 'POST':
        try:
            data = dict(request.POST)
            user = User.objects.get(username=request.POST["username"])
            if request.POST["password"] == user.password:
                request.session["username"] = request.POST["username"]
                data.update({"loginSuccess": True})
                return render(request, 'test.html', data)
        except User.DoesNotExist:
            data.update({"loginSuccess": False})
            return render(request, 'test.html', data)

def signup(request):
    if request.method == 'GET':
        return render(request, 'test.html')
    elif request.method == 'POST':
        try:
            data = dict(request.POST)
            user = User(username=request.POST["username"], 
                        password=request.POST["password"],
                        name=request.POST["name"])
            user.save()
            data.update({"signupSuccess": True})
            request.session["username"] = request.POST["username"]
            return render(request, 'test.html', data)
        except IntegrityError:
            data.update({"signupSuccess": False})
            return render(request, 'test.html', data)



def save(request):
    try:
        code = request.POST["item_code"]
        item = Item.objects.get(id=code)
        username = request.session["username"]
        user = User.objects.get(username=username)
        save_item = SavedItem(item=item, user=user)
        save_item.save()
        return render(request, "explore.html", {
            "item":item
        })
    except:
        print("Not Logged In")
        return render(request, "index.html")





def saved(request):
    try:
        username = request.session["username"]
        user = User.objects.get(username=username)
        saved_items = SavedItem.objects.filter(user=user.id)
        return render(request, 'saved.html', {
            "saved_items":saved_items
        })
    except:
        print("NEED TO LOGIN")
        return render(request, 'index.html')








def clear(request):
    request.session.flush()
    return HttpResponseRedirect(reverse("index"))

####### TESTING ################################################
def test_image(request, pk): # TESTING SINGLE IMGS
    item = Item.objects.get(pk=pk)
    print(item)
    # print(item.img.url)
    return render(request, "test.html", {"item": item})

def test_all_img(request): # TESTING ALL IMGS
    items = Item.objects.all()
    return render(request, "test_all_img.html", {
        "items": items
    })
