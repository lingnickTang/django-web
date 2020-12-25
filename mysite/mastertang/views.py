from django.shortcuts import render
import chat
import IDE

# Create your views here.
def home(request):
    import requests
    import json
    api_request = requests.get("https://api.github.com/users?since=0")
    api = json.loads(api_request.content)
    title = "Welcome to my homepage"
    return render(request,"home.html",{"api":api,"title":title})

def test(request):
    return render(request,"test.html",{})

def user(request):
    title = "research page"
    if request.method == "POST":
        import requests
        import json
        print(request)
        user = request.POST['user']
        user_request = requests.get("https://api.github.com/users/"+user)
        username = json.loads(user_request.content)
        return render(request,"user.html",{"user":user,"username":username,"title":title})
    else:
        notfound = "please input the name you want to search in the right-top bar"
        return render(request,"user.html",{"notfound":notfound, "title":title})

def tochat(request):
    return chat.views.index(request)

def toIDE(request):
    return IDE.views.onlineIDE(request)