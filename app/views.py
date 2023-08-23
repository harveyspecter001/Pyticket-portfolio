from django.shortcuts import render,redirect
from allauth.socialaccount.models import SocialAccount
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import *
from .forms import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics,permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def is_user_admin(guild):
    permissions = int(guild.get('permissions', 0))
    return permissions & 0x8 == 0x8

@method_decorator(login_required, name='dispatch')
class home(View):
    def get(self, request):
        user = request.user
        social_account = SocialAccount.objects.get(user=user, provider='discord')
        discord_id = social_account.uid
        avatar_url = 'https://cdn.discordapp.com/avatars/' + discord_id + '/' + social_account.extra_data['avatar'] + '.png'
        guilds = social_account.extra_data.get('guilds', [])

        # Filtra la lista de gremios para incluir solo aquellos donde el usuario es administrador
        guilds = [guild for guild in guilds if is_user_admin(guild)]
        
        bot_servers = BotServer.objects.filter(server_id__in=[guild['id'] for guild in guilds])
        
        guilds_with_bot = []
        guilds_without_bot = []
        for guild in guilds:
            server_id = guild['id']
            # Genera un enlace de invitación único para cada servidor
            invite_link = 'https://discord.com/oauth2/authorize?client_id=1117291520618397726&permissions=8&scope=bot' + '&guild_id=' + guild['id']
            guild['invite_link'] = invite_link
            """ check if the bot is in the server """
            if bot_servers.filter(server_id=server_id).exists():
                guild['member_count'] = bot_servers.get(server_id=server_id).member_count
                guilds_with_bot.append(guild)
            else:
                guild['member_count'] = None
                guilds_without_bot.append(guild)
            
        context = {
            'user': user,
            'avatar_url': avatar_url,
            'guilds_with_bot': guilds_with_bot,
            'guilds_without_bot': guilds_without_bot,
        }

        return render(request, 'dashboard/index.html', context)

class login(View):
    def get(self,request):
        return render(request,'user/login.html')

class logout(View):
    def get(self,request):
        return redirect('login')


@csrf_exempt
def add_server(request):
    if request.method == "POST":
        server_id = request.POST.get('server_id')
        owner_id = request.POST.get('owner_id')
        BotServer.objects.update_or_create(server_id=server_id, owner_id=owner_id)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failure', 'error': 'Invalid request method'})


@method_decorator(login_required, name='dispatch')
class configure_bot(View):
    form_class = BotConfigurationForm
    template_name = 'dashboard/configure_bot.html'

    def get(self, request, server_id, *args, **kwargs):
        user = request.user
        social_account = SocialAccount.objects.get(user=user, provider='discord')
        discord_id = social_account.uid
        avatar_url = 'https://cdn.discordapp.com/avatars/' + discord_id + '/' + social_account.extra_data['avatar'] + '.png'        
        bot_server = BotServer.objects.get(server_id=server_id)
        initial_values = bot_server.templates

        form = self.form_class(initial=initial_values)
        return render(request, self.template_name, {'form': form, 'avatar_url': avatar_url})

    def post(self, request, server_id, *args, **kwargs):
        bot_server = BotServer.objects.get(server_id=server_id)
        form = self.form_class(request.POST)

        if form.is_valid():
            bot_server.templates = form.cleaned_data
            bot_server.save()
            return redirect('home')

        return render(request, self.template_name, {'form': form})
#class configure_bot(View)
    #form_class = BotConfigurationForm
    #initial = {'key': 'value'}
    #template_name = 'dashboard/configure_bot.html'
    #def get(self, request, *args, **kwargs):
        #form = self.form_class(initial=self.initial)
        #return render(request, self.template_name, {'form': form})
    #def post(self, request, *args, **kwargs):
        #form = self.form_class(request.POST)
        #if form.is_valid():
            #return redirect('home')
"""         #return render(request, self.template_name, {'form': form})
 """

class BotConfigView(APIView):
    queryset = BotServer.objects.all()  # Agrega esta línea

    def get(self, request, server_id, format=None):
        try:
            bot_server = BotServer.objects.get(server_id=server_id)
        except BotServer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = {
            'creation_message': bot_server.templates['creation_message'],
            'welcome_message': bot_server.templates['welcome_message'],
            'ticket_title': bot_server.templates['ticket_title'],
            'ticket_description': bot_server.templates['ticket_description'],
            # otros campos que necesites
        }
        
        return Response(data)

###NO TOCAR
@method_decorator(login_required, name='dispatch')
class ConfigureBot(View):
    form_class = BotConfigurationForm
    template_name = 'dashboard/configure_bot.html'

    def get(self, request, server_id):
        bot_server = BotServer.objects.get(server_id=server_id)
        form = self.form_class(initial=bot_server.templates)
        return render(request, self.template_name, {'form': form})

    def post(self, request, server_id):
        bot_server = BotServer.objects.get(server_id=server_id)
        form = self.form_class(request.POST, initial=bot_server.templates)
        if form.is_valid():
            bot_server.templates = form.cleaned_data
            bot_server.save()
            return redirect('home')
        return render(request, self.template_name, {'form': form})
######

class UpdateServerInfoAPIView(APIView):
    def post(self, request):
        server_id = request.data.get('server_id')
        member_count = request.data.get('member_count')

        if not server_id or not member_count:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            bot_server = BotServer.objects.get(server_id=server_id)
        except BotServer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        bot_server.member_count = member_count
        bot_server.save()

        return Response(status=status.HTTP_200_OK)