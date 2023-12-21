from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from app1 import views as app1
from daifuwu import views as backend
urlpatterns = [
    path('show/image_list',backend.show_image_list),
    path('show/lunbo',backend.lunbo),
    path('show/silan',backend.shouyesilan),
    path('show/logo',backend.showlogo),
    path('show/getrow',backend.getrow),
    path('loginByWeixin',backend.wx_login),
    path('get/userinfo',backend.get_user_info),
    path('change/usr_info',backend.upload_usr_info),
    path('upload/uploadImages',backend.upload_images),
    path('task/publish',backend.task_publish),
    path('task/show_task_by_id',backend.show_task_by_id),
    path('task/search_by_key',backend.search_by_key),
    path('home/',backend.home),
    path('task/show_pending_tasks',backend.show_pending_tasks),
    path('task/receive',backend.receive),
    path('task/revise',backend.revise),
    path('task/show_my_publish_tasks',backend.my_publish_tasks),
    path('task/show_my_receive_tasks',backend.my_receive_tasks),
    path('task/show_all_about_melist',backend.show_about_me_tasklist),
    path('message/history',backend.get_history_messages),

]

# 添加以下两行以处理静态文件
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

