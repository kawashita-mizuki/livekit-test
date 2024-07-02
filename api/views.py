from rest_framework.permissions import AllowAny
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from livekit import api
import os
import asyncio
from asgiref.sync import async_to_sync

import uuid
import logging
logger = logging.getLogger('api')


class RoomListView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            room_list = loop.run_until_complete(self.list_rooms())
            return Response(room_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            loop.close()

    async def list_rooms(self):
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
        
        ## LiveKitAPI クライアントを作成
        lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
        ## ルーム一覧を取得
        rooms = await lkapi.room.list_rooms(api.ListRoomsRequest())
        room_names = [room.name for room in rooms.rooms]
        return room_names
    

class TokenCreateView(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        room_name = request.data.get('room_name', 'テスト')
        
        api_key = 'APILubZWopUFTo8'
        api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
        user_identity = str(uuid.uuid4())
        
        token = api.AccessToken(api_key, api_secret) \
                .with_identity(user_identity) \
                .with_name("Python Bot") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )).to_jwt()
        
        return Response({'token': token}, status=status.HTTP_200_OK)
    
    
    
class RoomCreateView(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        room_name = request.data.get('room_name', 'default-room')
        room = async_to_sync(self.create_room)(room_name)
        if room:
            return Response({'room_name': room.name}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to create room'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def create_room(self, room_name):
        try:
            api_key = 'APILubZWopUFTo8'
            api_secret = 'njsBhDaEJZ866ye1Vc6eKuzdk2fBpvd1M5V5XajFcZHB'
            livekit_api_url = 'https://livekit-test.colabmix.jp/livekit_server'
            
            ## LiveKitAPI クライアントを作成
            lkapi = api.LiveKitAPI(livekit_api_url, api_key, api_secret)
            ## ルームの作成
            room = await lkapi.room.create_room(api.CreateRoomRequest(name=room_name))
            return room
        except Exception as e:
            logger.debug(f'Error creating room: {str(e)}')
            return None