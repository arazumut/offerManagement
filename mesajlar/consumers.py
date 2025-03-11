import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Sohbet, Mesaj
import datetime
import logging


logger = logging.getLogger(__name__)

class SohbetConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.sohbet_id = self.scope['url_route']['kwargs']['sohbet_id']
        self.sohbet_group_name = f'sohbet_{self.sohbet_id}'
        

        client = self.scope['client']
        logger.info(f"WebSocket bağlantısı: {client[0]}:{client[1]} - Sohbet ID: {self.sohbet_id}")
        
        await self.channel_layer.group_add(
            self.sohbet_group_name,
            self.channel_name
        )
        
        
        await self.accept()
        

        if self.user.is_authenticated:

            await self.send(text_data=json.dumps({
                'mesaj': 'Bağlantı başarılı! Artık mesaj gönderebilirsiniz.',
                'gonderen_id': 0,
                'gonderen_username': 'Sistem',
                'mesaj_id': None,
                'gonderilme_tarihi': datetime.datetime.now().isoformat(),
            }))
        else:
            
            await self.send(text_data=json.dumps({
                'mesaj': 'Mesaj göndermek için giriş yapmalısınız.',
                'gonderen_id': 0,
                'gonderen_username': 'Sistem',
                'mesaj_id': None,
                'gonderilme_tarihi': datetime.datetime.now().isoformat(),
                'hata': 'auth_required'
            }))
    
    async def disconnect(self, close_code):
        
        client = self.scope['client']
        logger.info(f"WebSocket bağlantısı kapandı: {client[0]}:{client[1]} - Sohbet ID: {self.sohbet_id} - Kod: {close_code}")
        
    
        await self.channel_layer.group_discard(
            self.sohbet_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            
            
            if 'ping' in text_data_json:
                await self.send(text_data=json.dumps({
                    'pong': True,
                    'timestamp': datetime.datetime.now().isoformat()
                }))
                return
            
        
            mesaj = text_data_json['mesaj']
            
            
            if not self.user.is_authenticated:
            
                await self.send(text_data=json.dumps({
                    'mesaj': 'Mesaj göndermek için giriş yapmalısınız.',
                    'gonderen_id': 0,
                    'gonderen_username': 'Sistem',
                    'mesaj_id': None,
                    'gonderilme_tarihi': datetime.datetime.now().isoformat(),
                    'hata': 'auth_required'
                }))
                return
            
            
            try:
                yeni_mesaj = await self.save_message(mesaj)
                mesaj_id = yeni_mesaj.id
                gonderilme_tarihi = yeni_mesaj.gonderilme_tarihi.isoformat()
                
                # Mesajı sohbet grubuna gönder
                await self.channel_layer.group_send(
                    self.sohbet_group_name,
                    {
                        'type': 'sohbet_mesaji',
                        'mesaj': mesaj,
                        'gonderen_id': self.user.id,
                        'gonderen_username': self.user.username,
                        'mesaj_id': mesaj_id,
                        'gonderilme_tarihi': gonderilme_tarihi,
                    }
                )
            except Exception as e:
            
                logger.error(f"Mesaj kaydedilirken hata: {str(e)}")
                await self.send(text_data=json.dumps({
                    'mesaj': f'Mesaj gönderilirken bir hata oluştu: {str(e)}',
                    'gonderen_id': 0,
                    'gonderen_username': 'Sistem',
                    'mesaj_id': None,
                    'gonderilme_tarihi': datetime.datetime.now().isoformat(),
                    'hata': 'message_error'
                }))
        except Exception as e:
        
            logger.error(f"WebSocket mesajı işlenirken hata: {str(e)}")
    
    async def sohbet_mesaji(self, event):
        # WebSocket'e mesaj gönder
        await self.send(text_data=json.dumps({
            'mesaj': event['mesaj'],
            'gonderen_id': event['gonderen_id'],
            'gonderen_username': event['gonderen_username'],
            'mesaj_id': event.get('mesaj_id', None),
            'gonderilme_tarihi': event.get('gonderilme_tarihi', None),
        }))
    
    @database_sync_to_async
    def save_message(self, mesaj):
        sohbet = Sohbet.objects.get(id=self.sohbet_id)
        yeni_mesaj = Mesaj.objects.create(
            sohbet=sohbet,
            gonderen=self.user,
            icerik=mesaj
        )
        return yeni_mesaj 