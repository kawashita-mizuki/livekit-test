from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from datetime import datetime
from livekit import api
from livekit.protocol import room as proto_room
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



import uuid
import json
import logging
logger = logging.getLogger('api')


## ライブを始める人
class FirstJoinView(View):
    def get(self, request, *args, **kwargs):

        return render(request, "first_join.html")

## ライブを始める時のLiveKitサーバーとのやり取り
class LiveStartView(View):
    async def get(self, request, *args, **kwargs):
        ## LiveKit API サーバー情報
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        user_identity = request.GET.get('user_identity', str(uuid.uuid4()))

        ## ルーム名を指定
        current_time = datetime.now().strftime('%H%M%S')
        room_name = f'Room_{current_time}'

        try:
            ## LiveKitAPIインスタンスを作成
            lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        except Exception as e:
            logger.debug(f'Failed to lkapi: {str(e)}')
            
        try:
            ## room毎に最大参加可能人数を指定することができる
            ## room作成時か、livekite.yamlファイルで指定してあげる
            room = await lkapi.room.create_room(api.CreateRoomRequest(name=room_name, max_participants=2))
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

            ## トークンとルーム情報を返す
            return JsonResponse({
                'token': token,
                'room_name': room_name,
                'room_sid': room.sid
            })
        except Exception as e:
            logger.debug(f'Failed create token: {str(e)}')
            

## 後から入室する人
class SecondJoinView(View):
    async def get(self, request, *args, **kwargs):
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        
        ## LiveKitAPI クライアントを作成
        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        ## ルーム一覧を取得
        rooms_response = await lkapi.room.list_rooms(api.ListRoomsRequest())
        room_names = [room.name for room in rooms_response.rooms]
        return render(request, "second_join.html", {"room_names": room_names})


## トークンの取得
class GetTokenView(View):
    async def get(self, request, *args, **kwargs):
        room_name = request.GET.get('room')
        user_identity = request.GET.get('user_identity', str(uuid.uuid4()))
        
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        
        ## ルーム情報を取得
        rooms_response = await lkapi.room.list_rooms(api.ListRoomsRequest())
        room_info = next((room for room in rooms_response.rooms if room.name == room_name), None)
        ## 参加可能かどうかをチェック
        if room_info and room_info.num_participants >= room_info.max_participants:
            return JsonResponse({'message': 'ルームに参加できる人数を超えています。'})
        
        token = api.AccessToken(api_key, api_secret) \
                .with_identity(user_identity) \
                .with_name("Python Bot") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )).to_jwt()

        return JsonResponse({'token': token})
    

## 第三者用のview
class StaffView(View):
    async def get(self, request, *args, **kwargs):
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        
        ## LiveKitAPI クライアントを作成
        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        ## ルーム一覧を取得
        rooms_response = await lkapi.room.list_rooms(api.ListRoomsRequest())
        rooms = rooms_response.rooms
        return render(request, "staff.html", {"rooms": rooms})


## Roomの詳細情報を取得
class GetRoomParticipantsView(View):
    async def get(self, request, *args, **kwargs):
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        
        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        room_name = request.GET.get('room_name')

        try:
            # ルーム情報を取得
            room_info = await lkapi.room.list_participants(api.ListParticipantsRequest(room=room_name))
            participants = []
            for p in room_info.participants:
                ## FIXME: 各トラックの有効無効を判定したいがこれではできない
                is_audio_enabled = any('audio/' in track.mime_type and not track.muted for track in p.tracks)
                is_video_enabled = any('video/' in track.mime_type and not track.muted for track in p.tracks)
                participants.append({
                    "identity": p.identity,
                    "name": p.name,
                    "is_audio_enabled": is_audio_enabled,
                    "is_video_enabled": is_video_enabled
                })
            return JsonResponse({"participants": participants})
        except Exception as e:
            logger.error(f"Error getting participants: {e}")


## 強制退室
@method_decorator(csrf_exempt, name='dispatch')
class RemoveParticipantView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            room_name = data.get('room_name')
            participant_sid = data.get('participant_sid')

            api_key = 'APILubZWopUFTo8'
            api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
            livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
            lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)

            ## 特定のルームとそのルーム内の特定の参加者を識別するためのオブジェクトを作成
            participant_identity = proto_room.RoomParticipantIdentity(
                room=room_name,
                identity=participant_sid
            )

            ## 参加者を削除(強制退室)
            await lkapi.room.remove_participant(participant_identity)

            return JsonResponse({"success": True})
        except Exception as e:
            logger.debug(f"Error removing participant: {e}")


## カメラオフ、ミュート
@method_decorator(csrf_exempt, name='dispatch')
class ToggleTrackView(View):
    async def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        room_name = data.get('room_name')
        participant_sid = data.get('participant_sid')
        track_kind = data.get('track_kind')
        enable = data.get('enable')

        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'

        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        
        try:
            ## 参加者リストを取得
            room_info = await lkapi.room.list_participants(api.ListParticipantsRequest(room=room_name))
            if not room_info:
                return JsonResponse({"error": "Failed to retrieve participants"}, status=500)

            ## 特定の参加者を取得
            participant_info = next((p for p in room_info.participants if p.identity == participant_sid), None)
            if not participant_info:
                return JsonResponse({"error": "Participant not found"}, status=404)
        except Exception as e:
            logger.error(f"Error participant_info: {e}")

        try:
            track_sid = None
            for track in participant_info.tracks:
                ## MIMEタイプに基づいてトラックの種類を判断
                if track_kind == 'audio' and 'audio/' in track.mime_type:
                    track_sid = track.sid
                    break
                elif track_kind == 'video' and 'video/' in track.mime_type:
                    track_sid = track.sid
                    break

            if not track_sid:
                logger.error("Track not found")
                return JsonResponse({"error": "Track not found"}, status=404)
        except Exception as e:
            logger.error(f"Error トラック処理中にエラーが発生しました: {e}")

        try:
            track_request = proto_room.MuteRoomTrackRequest(
                room=room_name,
                identity=participant_sid,
                track_sid=track_sid,
                muted=not enable
            )

            response = await lkapi.room.mute_published_track(track_request)
            new_state = not response.track.muted

            return JsonResponse({"success": True, "new_state": new_state})
        except Exception as e:
            logger.error(f"Error track_request: {e}")
        