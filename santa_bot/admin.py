from django.contrib import admin
from django.utils.html import format_html

from santa_bot.models import Game, Image, Organizer, Player


@admin.register(Organizer)
class UserAdmin(admin.ModelAdmin):
    '''Admin panel for users'''
    search_fields = ['telegram_id']
    list_display = ['id', 'telegram_id']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    '''Admin panel for games'''
    search_fields = ['name', 'start_date', 'end_date', 'send_date']
    list_filter = ['name', 'start_date', 'end_date', 'send_date']
    list_display = [
        'name', 'organizer', 'start_date', 'end_date', 'send_date',
        'link', 'price_limit', 'players_distributed'
    ]
    raw_id_fields = ['organizer']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    '''Admin panel for players'''
    search_fields = ['telegram_id', 'game', 'name', 'email']
    list_filter = ['telegram_id', 'game', 'name', 'email']
    list_display = ['telegram_id', 'game', 'name', 'email']
    raw_id_fields = ['avoided_players', 'giftee']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'preview']

    def preview(self, image_obj):
        '''Display preview of image'''
        return format_html('<img src="{}" width="150" height="150" />',
                           image_obj.file.url)
