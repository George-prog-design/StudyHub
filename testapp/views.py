from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# # rooms = [
# #     {'id': 1, 'name': 'lets leave',}
    
# ]
# Create your views here.

def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect ('home')


    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        #we get the username and password using post get 
        # check if user exists using try function
        # if doesnt we dosplay error message
        # if does exist we then use authenticate function to check username and password
        # the get the username and password from user object
        # the log in creates a session
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)        
        
        if user is not None:
             login(request, user)
             return redirect('home') 
        else:
             messages.error(request, 'Username does not exist')   
    context = {'page': page}
    return render(request, 'testapp/login_register.html', context)


def LogoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):

    # we use a built in usercreation form
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
           user = form.save(commit=False)
    # once a user is created we accesss thier page
           user.username = user.username.lower()
           user.save() 
           login(request, user)
           return redirect('home')
        else:
            messages.error(request, 'An error occurred')
            
    return render(request, 'testapp/login_register.html', {'form': form})


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    # using set_all we get all the children connected to the table
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages': room_messages,'topics':topics}
    return render(request, 'testapp/profile.html', context)



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # used q as a search varibale to filter
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
                                )

# using special function Q impoterd we can search by
# all three perimeters we want
    topics = Topic.objects.all()[0:4]
    # limits to only five visible topics
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    # filters to specific recent activity based on topics

# the function Room.objects.filter used to filter
    context = {'rooms' : rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'testapp/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # to get certain information you can specify from the model room
    room_messages = room.message_set.all()
    # used to submit new messages to the convo since we
    # are adding to user room and bosy of the model messages
    partcipants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room = room,
            body = request.POST.get('body')

        )
        # used to add a new participant
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context = {'room' : room, 'room_messages' : room_messages, 'partcipants' : partcipants}

    return render(request, 'testapp/room.html', context)



# restricts the page to only certain users
# in the case of trying to log in user is redirected to to login
@login_required(login_url='login')
def createRoom(request):
    form =RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )    
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
        # just as the models we treat Roomform the same way and put it in context
        # # request.POST method is used to save data anad the condition 
        # if a form is valid is saved. then we redirect the user to the home page
        
    context = {'form' : form, 'topics' : topics}

    return render(request, 'testapp/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
       return HttpResponse('Bad Request') 

    # ensures the form is prefixed with the instance   
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # form = RoomForm(request.POST, instance=room)
        # # used to direct post info to the specific instance
        # if form.is_valid():
        #     form.save()
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


    context = {'form' : form, 'topics' : topics, 'room' : room}
    return render(request, 'testapp/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
       return HttpResponse('Bad Request')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'testapp/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
       return HttpResponse('Bad Request')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'testapp/delete.html',{'obj':message})


@login_required(login_url='login')
def Updateuser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    return render(request, 'testapp/update_user.html', {'form':form})

def topicsPage(request):
    topics = Topic.objects.filter()
    return render(request, 'testapp/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'testapp/activity.html',{'room_messages': room_messages})
