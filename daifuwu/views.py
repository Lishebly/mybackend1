

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
from django.conf import settings
from .models import CustomUser,Task,TaskMessage
from django.db.models import Q
baseurl='http://127.0.0.1:8000'
def show_image_list(request):
    mylist=[]
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}task_pubilish.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}public.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}mytask.png"})

    # 返回JSON响应
    return JsonResponse({'images': mylist})

def show_tou_list(request):
    mylist = []
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}tou1.jpeg"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}tou2.jpeg"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}tou3.jpeg"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}tou4.jpeg"})

    # 返回JSON响应
    return JsonResponse({'images': mylist})
def home(request):
    return render(request,'index.html')

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

@require_GET
def getrow(request):
    mylist = []
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}green.png"})
    mylist.append({'url': baseurl + f"{settings.STATIC_URL}red.png"})
    return JsonResponse({'data':mylist})


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
            image_url = f"{settings.MEDIA_URL[1:]}user_avatars/{image.name}"
            # print(settings.MEDIA_URL)
            # print(image_url)
            # 返回包含图片链接的JSON响应
            return JsonResponse({'imageUrl': image_url})
        except Exception as e:
            # print(str(e))
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@require_POST
def task_publish(request):
    try:
        # 获取前端传递过来的任务数据

        data = json.loads(request.body)
        title=data.get('title','')
        description = data.get('description', '')
        phone = data.get('phone', '')
        reward = data.get('reward', '')
        deadline = data.get('deadline', '')
        openid = data.get('openid', '')

        # 根据openid找到对应的用户
        user = CustomUser.objects.get(openid=openid)

        # 创建任务
        task = Task.objects.create(
            title=title,
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

@csrf_exempt
def show_task_by_id(request):
    try:
        data = json.loads(request.body)


        task_id = data.get('id', '')

        # 获取任务信息
        task = Task.objects.get(id=task_id)

        # 获取任务相关的用户信息
        creator_info = {'nickname': task.creator.nickname, 'phone': task.creator.phone_number,'openid':task.creator.openid}
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
            'reward': task.reward,
            'description': task.description,
            'creator': creator_info,
            'assignee': assignee_info,
        }

        return JsonResponse(response_data)
    except Task.DoesNotExist:
        return JsonResponse({'error': '任务不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def show_pending_tasks(request):
    # 获取所有状态为 'pending' 的任务
    pending_tasks = Task.objects.filter(status='pending').order_by('-publish_time')

    # 将任务数据转换为 JSON 格式
    tasks_data=[]
    for task in pending_tasks:
        c_usr=CustomUser.objects.get(id=task.creator_id)
        tmp={
            'id': task.id,
            'description': task.description,
            'reward': str(task.reward),  # 使用字符串表示 decimal 字段
            'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status,
            'assignee_id': task.assignee_id,
            'creator_id': task.creator_id,
            'creator_name': c_usr.nickname,
            'ex_phone_number': task.ex_phone_number,
            'title': task.title,
        }
        tasks_data.append(tmp)
    # 返回 JSON 响应
    return JsonResponse({'pending_tasks': tasks_data})

@csrf_exempt
def receive(request):
    try:
        data = json.loads(request.body)

        task_id = data.get('id', '')
        openid=data.get('openid','')
        a_usr=CustomUser.objects.get(openid=openid)

        # 获取任务信息
        task = Task.objects.get(id=task_id)
        status_info=task.status
        if status_info=='pending':
            task.status= 'in_progress'
            task.assignee=a_usr
            task.save()
            response_data={'res':'success','status':task.status}
            return JsonResponse(response_data)
        else:
            response_data = {'res': 'fail','status':task.status}
            return JsonResponse(response_data)
    except Task.DoesNotExist:
        return JsonResponse({'error': '任务不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt#修改用户信息
def revise(request):
    try:
        data = json.loads(request.body)
        avatar=data.get('avatar','')
        name=data.get('nickname','')
        phone=data.get('phone_number','')
        openid = data.get('openid', '')
        user=CustomUser.objects.get(openid=openid)
        if avatar:
            user.avatar=avatar
        if name:
            user.nickname=name
        if phone:
            user.phone_number=phone
        user.save()
        return JsonResponse({'res':'success'})


    except Task.DoesNotExist:
        return JsonResponse({'error': '任务不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def my_publish_tasks(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': '无法解析JSON数据', 'details': str(e)}, status=400)

    openid=data.get('openid','')
    usr=CustomUser.objects.get(openid=openid)
    usr_id=usr.id
    tasks=Task.objects.filter(creator_id=usr_id).order_by('-publish_time')
    grouped_tasks_data = {'pending': [], 'in_progress': [], 'completed': []}
    for task in tasks:
        tmp = {
            'id': task.id,
            'description': task.description,
            'reward': str(task.reward),  # 使用字符串表示 decimal 字段
            'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status,
            'assignee_id': task.assignee_id,
            'assignee_name': task.assignee.nickname if task.assignee else '',
            'creator_id': task.creator_id,
            'creator_name': usr.nickname,
            'ex_phone_number': task.ex_phone_number,
            'title': task.title,
            'please': task.please,
        }
        grouped_tasks_data[task.status].append(tmp)


    # 返回 JSON 响应
    return JsonResponse(grouped_tasks_data)

@csrf_exempt
def my_receive_tasks(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': '无法解析JSON数据', 'details': str(e)}, status=400)
    # print(data)
    openid = data.get('openid', '')
    usr = CustomUser.objects.get(openid=openid)
    tasks = Task.objects.filter(assignee=usr).order_by('-publish_time')
    grouped_tasks_data = {'pending': [], 'in_progress': [], 'completed': []}
    for task in tasks:
        tmp = {
            'id': task.id,
            'description': task.description,
            'reward': str(task.reward),  # 使用字符串表示 decimal 字段
            'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status,
            'creator_id': task.creator_id,
            'creator_name': task.creator.nickname,
            'ex_phone_number': task.ex_phone_number,
            'title': task.title,
            'please': task.please,
        }
        grouped_tasks_data[task.status].append(tmp)

    # 返回 JSON 响应
    return JsonResponse(grouped_tasks_data)

@csrf_exempt
def show_about_me_tasklist(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': '无法解析JSON数据', 'details': str(e)}, status=400)

    openid = data.get('openid', '')
    usr = get_object_or_404(CustomUser, openid=openid)


    task1 = Task.objects.filter(
        Q(creator=usr, assignee__isnull=False),
        Q(last_chat_time__isnull=False) | Q(last_chat_time__isnull=True),
    ).order_by('-last_chat_time')


    task2 = Task.objects.filter(
        Q(assignee=usr, creator__isnull=False),
        Q(last_chat_time__isnull=False) | Q(last_chat_time__isnull=True),
    ).order_by('-last_chat_time')

    result = {
        'data': {
            'in_progress': {
                'my_creat': [],
                'my_receive': [],
            },
            'completed': {
                'my_creat': [],
                'my_receive': [],
            }
        }
    }

    for e in task1:
        task_data = {
            'Taskid': e.id,
            'name': e.assignee.nickname,
            'avatar': e.assignee.avatar,
            'last_chat_time': e.last_chat_time.strftime('%Y-%m-%d %H:%M:%S') if e.last_chat_time else '',
            'last_chat_content': e.last_chat_content,
            'title': e.title,
        }
        if e.status == 'in_progress':
            result['data']['in_progress']['my_creat'].append(task_data)
        elif e.status == 'completed':
            result['data']['completed']['my_creat'].append(task_data)

    for e in task2:
        task_data = {
            'Taskid': e.id,
            'name': e.creator.nickname,
            'avatar': e.creator.avatar,
            'last_chat_time': e.last_chat_time.strftime('%Y-%m-%d %H:%M:%S') if e.last_chat_time else '',
            'last_chat_content': e.last_chat_content,
            'title': e.title,
        }
        if e.status == 'in_progress':
            result['data']['in_progress']['my_receive'].append(task_data)
        elif e.status == 'completed':
            result['data']['completed']['my_receive'].append(task_data)

    return JsonResponse(result)

@csrf_exempt
def search_by_key(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': '无法解析JSON数据', 'details': str(e)}, status=400)

    key_word = data.get('kw')

    if key_word:
        # 使用 Q 对象构建查询条件，标题包含关键词或描述包含关键词的任务都会匹配
        query_condition = (
                                  Q(title__icontains=key_word) | Q(description__icontains=key_word)
                          ) & Q(status__icontains='pending')

        # 执行查询
        matching_tasks = Task.objects.filter(query_condition)

        # 处理查询结果，例如将结果转换为 JSON 格式返回
        result = {
            'data': [{
                'id': task.id,
                'title': task.title,
                'description':task.description,
                'publish_name': task.creator.nickname,
                'reward': task.reward,
                'deadline': task.deadline,
                'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': task.status,
            } for task in matching_tasks]
        }

        return JsonResponse(result)
    else:
        return JsonResponse({'error': '关键词不能为空'}, status=400)

def get_history_messages(request):
    taskid = request.GET.get('taskid', '')
    task = Task.objects.get(id=taskid)
    messages = TaskMessage.objects.filter(task=task)

    if messages:
        res = []
        for m in messages:
            temp = {
                'sender': m.sender,
                'content': m.content,
                'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            res.append(temp)

        return JsonResponse({'messages': res,'error':'success'})
    else:
        return JsonResponse({'error': 'fail','message':'no messages'})


def c_a_info(request):
    taskid = request.GET.get('taskid','')
    task = Task.objects.get(id=taskid)
    res = {
        'creator_url': task.creator.avatar,
        'creator_name': task.creator.nickname,
        'assignee_url': task.assignee.avatar,
        'assignee_name': task.assignee.nickname,
    }
    return JsonResponse(res)


def select_by_reward(request):
    # 获取选择的酬劳范围
    reward = request.GET.get('selectReward', '')
    # print(reward)
    if not reward:
        return JsonResponse({'status': 'error', 'message': 'selectReward parameter is missing'})

    try:
        reward = reward.split(',')
        low, high = int(reward[0]), int(reward[1])
    except (json.JSONDecodeError, IndexError):
        return JsonResponse({'status': 'error', 'message': 'Invalid selectReward parameter'})

    # 使用酬劳范围筛选状态为 'pending' 的任务
    pending_tasks = Task.objects.filter(status='pending', reward__range=(low, high)).order_by('-publish_time')

    # 构建任务列表
    task_list = [{
        'id': task.id,
        'description': task.description,
        'reward': str(task.reward),  # 使用字符串表示 decimal 字段
        'publish_time': task.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
        'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'status': task.status,
        'creator_id': task.creator_id,
        'creator_name': task.creator.nickname,
        'ex_phone_number': task.ex_phone_number,
        'title': task.title,
    } for task in pending_tasks]

    return JsonResponse({'status': 'success', 'tasks': task_list})

def please_finish(request):
    taskid=request.GET.get('taskid','')
    if taskid:
        task=Task.objects.get(id=taskid)
        task.please = True
        # print('yes')
        task.save()
        return JsonResponse({'status': 'success','content': 'success'})
    else:
        return JsonResponse({'status': 'fail','content': 'no taskid'})


def show_please_finish(request):
    openid = request.GET.get('openid', '')
    se= request.GET.get('se','')
    se = int(se)
    # print(se)
    try:
        usr = CustomUser.objects.get(openid=openid)
        tasks = Task.objects.filter(creator=usr, status='in_progress', please=True)
        if se==1:
            return JsonResponse({'tasks_length': len(tasks)})
        # 构造返回的任务数据
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'reward': task.reward,
                'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),  # 将截止时间格式化为字符串
                'creator_name': task.creator.nickname,

            })

        return JsonResponse({'tasks': tasks_data})

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 确认请求
def please_finish_c(request):
    taskid=request.GET.get('taskid','')
    if taskid:
        task=Task.objects.get(id=taskid)
        task.please = True
        task.status = 'completed'

        task.save()
        return JsonResponse({'status': 'success','content': 'success'})
    else:
        return JsonResponse({'status': 'fail','content': 'no taskid'})