
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.utils import timezone
class ChatConsumer(WebsocketConsumer):


    def websocket_connect(self, message):
        group = self.scope['url_route']['kwargs'].get("group")
        print('taskid为', group)
        self.accept()
        async_to_sync(self.channel_layer.group_add)(group, self.channel_name)

    def websocket_receive(self, message):
        group = self.scope['url_route']['kwargs'].get("group")
        content_str = message['text']

        try:
            content_dict = json.loads(content_str)
            print(content_dict)

            content = content_dict['content']
            sender = content_dict['sender']
            task=Task.objects.get(id=group)
            task.last_chat_time = timezone.now()
            task.save()
            TaskMessage.objects.create(
                sender=sender,
                content=content,
                task=task,
            )
            print(group)
            print(content)
            print(sender)
            async_to_sync(self.channel_layer.group_send)(
                group,
                {
                    "type": "xxx_ooo",
                    "message": {
                        "sender": sender,
                        # "sender": "me",
                        "content": content,
                    },
                }
            )
            # 现在 content_dict 是一个字典类型
            # 可以通过 content_dict['key'] 来访问具体的值
        except json.JSONDecodeError as e:
            # 处理 JSON 解析错误
            print(f"Error decoding JSON: {e}")


    def xxx_ooo(self, event):
        sender = event['message']['sender']
        content = event['message']['content']

        # 将字典转换为 JSON 字符串
        json_data = json.dumps({'sender': sender, 'content': content})

        # 发送 JSON 字符串给前端
        self.send(text_data=json_data)

    def websocket_disconnect(self, message):
        group = self.scope['url_route']['kwargs'].get("group")
        async_to_sync(self.channel_layer.group_discard)(group, self.channel_name)
