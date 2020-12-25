from django.shortcuts import render


# Create your views here.
def onlineIDE(request):
    title = "y86/64 IDE"
    #if request.method == "GET":
    #print(request.GET.get("text"))
    return render(request, "IDE/onlineIDE.html", {
        'title':title,
    })



