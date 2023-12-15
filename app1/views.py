from django.http import JsonResponse
from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.conf import settings


from .models import UserInfo,MyModel
# Create your views here.
def index(request):
    return HttpResponse("欢迎")

def index1(request):
    return render(request,'a1.html')

def login(request):
    if request.method == "GET":
        return render(request,'login.html')
    else:
        print(request.POST)
        return HttpResponse("登录成功")

def test_showlist(request):
    data_list=UserInfo.objects.all()
    return render(request,'info_list.html',{"datalist":data_list})

def test_add(request):
    for i in range(1, 11):
        UserInfo.objects.create(
            name=f'User{i}',
            password=f'password{i}',
            age=i * 5  # Just an example for age
        )
    return HttpResponse('success')
@csrf_exempt
def postadd(request):
    if request.method == 'POST':
        a=request.POST
        for e in a:
            print(e)

        name = request.POST.get('name')
        password = request.POST.get('password')
        age = request.POST.get('age')

        # Add the user to the database
        UserInfo.objects.create(name=name, password=password, age=age)

        # Return a JSON response
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def show_image(request):
    images_folder = os.path.join(settings.MEDIA_ROOT, 'images')

    # 获取所有图片文件的信息
    image_info_list = []
    for filename in os.listdir(images_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(images_folder, filename)
            image_info_list.append({
                'filename': filename,
                'url': request.build_absolute_uri(settings.MEDIA_URL + 'images/' + filename),
                'size': os.path.getsize(file_path),
            })

    # 将图片信息列表转为 JSON 字符串
    images_json_str = json.dumps(image_info_list)

    return JsonResponse({'images': images_json_str})

def task_pubilish(request):
    return render(request,'tu1.html')
class Mystatic():
    def task_pubilish(self,request):
        return render(request,'tu1.html')
    def test(self,re):
        return HttpResponse('aaa')