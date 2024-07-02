from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
from asgiref.sync import async_to_sync
from datetime import datetime
from livekit import api

import uuid
import logging
logger = logging.getLogger('api')

class TestView(View):
    def get(self, request, *args, **kwargs):

        return render(request, "test.html")


class JoinView(View):
    def get(self, request, *args, **kwargs):

        return render(request, "test.html")


class LiveStartView(View):
    async def get(self, request, *args, **kwargs):
        ## LiveKit API サーバー情報
        # api_key = 'devkey'
        # api_secret = 'secret'
        api_key = 'API54x5CU6hUq8Y'
        api_secret = '149w6E9C1dNUQDZiqL67tabiO4iiHrxW9sdc2DBoKLC'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        # livekit_api_url = 'http://127.0.0.1:7880'
        user_identity = str(uuid.uuid4())

        ## ルーム名を指定
        current_time = datetime.now().strftime('%H%M%S')
        room_name = f'Room_{current_time}'

        try:
            ## LiveKitAPIインスタンスを作成
            lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
            # logger.debug(f'lkapi: {lkapi}')
        except Exception as e:
            logger.debug(f'Failed to lkapi: {str(e)}')
            
        try:
            ## ルームを作成（非同期関数を同期的に呼び出すためにasync_to_syncを使用）
            room = await lkapi.room.create_room(api.CreateRoomRequest(name=room_name))
            # logger.debug(f'create room: {room}')
        except Exception as e:
            logger.debug(f'Failed create room: {str(e)}')

        try:
            ## アクセストークンを生成（有効期限を60分に設定）
            token = api.AccessToken(api_key, api_secret) \
                .with_identity(user_identity) \
                .with_name("Python Bot") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )).to_jwt()
                
            # ttl_minutes = 60
            # exp_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl_minutes)

            # # AccessTokenに期限を設定
            # token.set_expiry(exp_time.timestamp())

            # # JWT形式でトークンを生成
            # jwt_token = token.to_jwt()

            # logger.debug(f'create token: {token}')

            ## トークンとルーム情報を返す
            return JsonResponse({
                'token': token,
                'room_name': room_name,
                'room_sid': room.sid
            })
        except Exception as e:
            logger.debug(f'Failed create token: {str(e)}')
