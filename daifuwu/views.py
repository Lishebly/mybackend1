

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
from django.conf import settings
from .models import CustomUser,Task
baseurl='http://127.0.0.1:8000'
def show_image_list(request):
    mylist=[]
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}task_pubilish.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}public.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}mytask.png"})

    # 返回JSON响应
    return JsonResponse({'images': mylist})

def lunbo(re):
    mylist=[]
    mylist.append({'url': baseurl+f"{settings.STATIC_URL}welcome.png"})
    mylist.append({'url': baseurl+f"{settings.STATIC_URL}NENU1.png"})
    mylist.append({'url': baseurl+f"{settings.STATIC_URL}NENU2.png"})
    return JsonResponse({'images':mylist})
def shouyesilan(re):
    mylist=[]
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}task_pubilish.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}wait.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}wait.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}wait.png"})
    return JsonResponse({'images': mylist})
def showlogo(re):
    mylist=[]
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}logo.png"})
    return JsonResponse({'images': mylist})


def wx_login(request):
    # 从前端获取登录凭证 code
    code = request.GET.get('code', None)
    if not code:
        return JsonResponse({'error': '缺少登录凭证 code'}, status=400)

    # 微信小程序的相关参数
    appid = 'wxd64e0ff7c3d191b9'
    secret = 'cbffcfe1bb764774fcdfcfc71152614f'
    js_code = code
    grant_type = 'authorization_code'

    # 构建请求URL
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type={grant_type}'

    try:
        # 发送HTTP请求
        response = requests.get(url)
        data = response.json()

        # 处理微信返回的数据
        openid = data.get('openid', None)
        session_key = data.get('session_key', None)


        if openid and session_key:
            # 在这里你可以保存用户的openid和session_key，或者进行其他逻辑处理
            user, created = CustomUser.objects.get_or_create(openid=openid)
            refresh = RefreshToken.for_user(user)  # user是你的CustomUser实例
            access_token = str(refresh.access_token)
            isnew=False if user.avatar else True

            return JsonResponse({'openid': openid, 'session_key': session_key, 'token': access_token,'isnew':isnew})
        else:
            return JsonResponse({'error': '获取用户信息失败'}, status=500)

    except requests.RequestException as e:
        return JsonResponse({'error': f'请求微信API失败: {str(e)}'}, status=500)


@require_GET
def get_user_info(request):
    try:
        # 获取前端传递过来的openid
        openid = request.GET.get('openid', '')

        # 查找用户
        user = CustomUser.objects.get(openid=openid)

        # 构建要返回的用户信息
        user_info = {
            'avatar': user.avatar,
            'nickname': user.nickname,
            'phone_number': user.phone_number,
        }

        # 返回JSON响应
        return JsonResponse(user_info)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        # 处理其他异常
        return JsonResponse({'error': str(e)}, status=400)



@require_POST
@csrf_exempt
def upload_usr_info(request):
    try:
        # 假设请求数据以JSON格式发送
        data = json.loads(request.body)

        # 访问数据字段（nickname，phoneNumber，avatarUrl）
        nickname = data.get('nickname', '')
        phone_number = data.get('phoneNumber', '')
        avatar_url = data.get('avatarUrl', '')
        user_identifier= data.get('openid','')

        user = CustomUser.objects.get(openid=user_identifier)
        # 更新用户信息
        user.nickname = nickname
        user.phone_number = phone_number
        user.avatar = avatar_url

        # 保存用户信息
        user.save()
        # 返回JSON响应
        return JsonResponse({'message': '用户信息更新成功'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)

    except Exception as e:
    # 处理其他异常
        return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
def upload_images(request):
    if request.method == 'POST':
        try:
            image = request.FILES['image']

            # 生成唯一的文件名，你可以根据需要进行修改
            filename = f"{settings.MEDIA_ROOT}/user_avatars/{image.name}"
            # print(filename)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            # 将文件保存到服务器
            with open(filename, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # print(filename)
            # 构建图片的访问链接
            image_url = f"{settings.MEDIA_URL}user_avatars/{image.name}"

            # 返回包含图片链接的JSON响应
            return JsonResponse({'imageUrl': image_url})
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
@require_POST
def task_publish(request):
    try:
        # 获取前端传递过来的任务数据

        data = json.loads(request.body)
        description = data.get('description', '')
        phone = data.get('phone', '')
        reward = data.get('reward', '')
        deadline = data.get('deadline', '')
        openid = data.get('openid', '')
        print(openid)
        # 根据openid找到对应的用户
        user = CustomUser.objects.get(openid=openid)

        # 创建任务
        task = Task.objects.create(
            description=description,
            ex_phone_number=phone,
            reward=reward,
            deadline=deadline,
            creator=user,
        )

        return JsonResponse({'message': '任务发布成功', 'task_id': task.id})
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def show_task_by_id(request):
    try:
        data = json.loads(request.body)
        print('1')
        print(request.body)
        task_id = data.get('id', '')

        # 获取任务信息
        task = Task.objects.get(id=task_id)

        # 获取任务相关的用户信息
        creator_info = {'nickname': task.creator.nickname, 'phone': task.creator.phone_number}
        assignee_info = {'nickname': '', 'phone': ''}

        if task.assignee:
            assignee_info = {'nickname': task.assignee.nickname, 'phone': task.assignee.phone_number}

        # 构建返回的 JSON 数据
        response_data = {
            'title': task.title,
            'ex_phone_number': task.ex_phone_number,
            'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status,
            'description': task.description,
            'creator': creator_info,
            'assignee': assignee_info,
        }

        return JsonResponse(response_data)
    except Task.DoesNotExist:
        return JsonResponse({'error': '任务不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

