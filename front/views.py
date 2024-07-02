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
        authorized_user = login_check(request)
        now = datetime.now()
        ## 表示画像の取得
        web_top_image = get_web_image(now, "top")

        ## セッションにエラーメッセージがあるときは表示
        error_message = None
        if "error_msg" in request.session and request.session['error_msg']:
            error_message = request.session['error_msg']
            ## セッションのエラーメッセージを空にして保存
            request.session['error_msg'] = None
        success_message = None
        if "success_msg" in request.session and request.session['success_msg']:
            success_message = request.session['success_msg']
            ## セッションのサクセスメッセージを空にして保存
            request.session['success_msg'] = None

        return render(request, "front/top.html", {"authorized_user": authorized_user, "error_message": error_message, "success_message": success_message, "web_top_image": web_top_image})



class LiveStartView(View):
    async def get(self, request, *args, **kwargs):
        ## LiveKit API サーバー情報
        # api_key = 'devkey'
        # api_secret = 'secret'
        api_key = 'APITJa4apR9h99w'
        api_secret = 'Aln2Ix3BazFtqf6EomicLO8y0jOf2iYVEOukb7MUi9b'
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
