from django.shortcuts import render

# Create your views here.



def homepage(request):

    if request.method=='POST':
        result=request.POST.get('arama')
        return render(request,'index.html',{'result':result})

    return render(request,'index.html')
