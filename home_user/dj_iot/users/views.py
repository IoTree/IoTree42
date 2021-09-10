
"""
//Iotree42 sensor Network

//purpose: for handle requests and to process the wep pages
//used software: python3, django, time, datetime, rest_framework
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, TreePostForm, InputPostForm
from django.core.paginator import Paginator
from .mqttcon import InitMqttClient
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timezone
from .fluxcon import InitInfluxUser, DelInfluxData
from .fluxdatacon import FluxDataCon
from .grafanacon import InitGrafaUser
from .pahocon import PahoSend
import time
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from revproxy.views import ProxyView
import datetime


with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

def zip_download(request, version):
    import os
    if int(version) == 1:
        file_name = 'IoTree_Gateway_V_2.0.zip'
        # file_name = version
    file_path = os.path.join(settings.MEDIA_ROOT, 'downloadfiles/'+file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename='+ file_name
            return response
    raise Http404


# func. for the register site
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('username')
            user_email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            user = form.save(commit=False)
            init_flux_client = InitInfluxUser(user_name, password1)
            init_flux_client.run()
            init_mqtt_client = InitMqttClient(user_name, password1)
            init_mqtt_client.run()
            init_grafa_client = InitGrafaUser(user_name, password1, user_email)
            init_grafa_client.run()
            user.first_name = "Same as the login PW from this site."
            user.last_name = "Same as the login PW from this site."
            user.save()
            messages.success(request, str(user_name)+': account has been created! You are now able to log in!')
            del init_mqtt_client
            del init_grafa_client
            del init_flux_client
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# func. for deleting user and process the deleting site
@login_required
def delete_user(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        cancel = request.POST.get('cancel')
        if confirm == 'confirm':
            user = User.objects.get(username=request.user.username)
            user.delete()
            messages.success(request, str(request.user.username) + ' account has been deleted! and all related data')
            return redirect('logout')
        if cancel == 'cancel':
            return redirect('profile')
    else:
        return render(request, 'users/delete_user.html')


# func. for the profile site
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        delete = request.POST.get('delete', None)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
        if delete:
            try:
                return redirect('delete-user')
            except User.DoesNotExist:
                messages.success(request, ' account does not exist!')
            except Exception as e:
                messages.success(request, str(e.message))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        print(p_form)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


# func. for the iotree site
@login_required
def treeview(request):
    if request.method == 'POST':
        form = TreePostForm(request.POST)
        if form.is_valid():
            time_start = form.cleaned_data.get('time_start')
            time_end = form.cleaned_data.get('time_end')
            time_start = time_start.replace(tzinfo=timezone.utc).timestamp()
            time_end = time_end.replace(tzinfo=timezone.utc).timestamp()
            tree = request.POST.get('tree', None)
            action = form.cleaned_data.get('action')
            time_start = int(time_start*1000)
            time_end = int(time_end*1000)
            treee = tree.replace("/", "_")
            if action == 'table':
                return redirect('iotree-show', str(treee), time_start, time_end)
            if action == 'download':
                return redirect('iotree-download', str(treee), time_start, time_end)
            if action == 'delete':
                flux_client = FluxDataCon(request.user.username)
                tags = flux_client.get_raw_tags(str(tree))
                del flux_client
                if tags == "":
                    messages.info(request, "No Date Found! for delete")
                    return redirect('treeview')
                else:
                    flux_del = DelInfluxData(request.user.username, tags)
                    response = flux_del.run()
                    messages.info(request, 'Measuerments droped: '+str(tags)+'Database response: '+str(response))
                    del flux_del
                    return redirect('treeview')
    else:
        form = TreePostForm(initial={'time_end':datetime.datetime.now()})
        flux_client = FluxDataCon(request.user.username)
        context = flux_client.get_tag_tree()
        if str(context) == "[]":
            messages.info(request, 'No data jet!')
        del flux_client
        return render(request, 'users/treeview.html', {'context':context, 'form':form})


# func. for display all gateways and do actions
@login_required
def gatewaylist(request):
    if request.method == 'POST':
        messages.info(request, "No Post -> get")
    else:
        # connect to db
        flux_client = FluxDataCon(request.user.username)
        # get all tags
        tags = flux_client.get_tag_tree()
        # filter only the gateway ids
        dicttags = json.loads(tags)
        gatewaylist = []
        for m in dicttags:
            gatewaylist.append(m["text"])
        # getting last 5 min entrys of ping of each gatway
        flux_client.start_time((int(time.time())-300)*1000)
        flux_client.end_time(int(time.time())*1000)
        tree = [s + "/SYSTEMcontrol/ping" for s in gatewaylist]
        lastseen = flux_client.find(",".join(tree))
        del flux_client
        # check if gateway is online the last 5 min or not
        lastseenlist = []
        for n in lastseen:
            tag = n["posts_tree"]
            tag = tag.split("/")
            lastseenlist.append(tag[0])
        # map data for render page
        context = []
        for b in gatewaylist:
            element = {}
            element["id"] = b
            if b in lastseenlist:
                element["status"] = "online"
                element["color"] = "green"
            else:
                element["status"] = "offline"
                element["color"] = "red"
            context.append(element)
        if str(context) == "[]":
            messages.info(request, 'No gateway connected jet!')
        return render(request, 'users/gateway_list.html', {'context':context})


# func. for the setup_rpi site
@login_required
def input(request, gateway, task):
    if request.method == 'POST':
        form = InputPostForm(request.POST)
        if form.is_valid():
            if request.POST.get("send"):
                textbox = form.cleaned_data.get('textbox')
                if "jsonfile" in task:
                    topic = "SYSTEMcontrolDONOTSAVE/syncfile"
                    pahosend = PahoSend(request.user.username, gateway, topic)
                    jsonstring = pahosend.checkjson(textbox)
                    if jsonstring:
                        io = pahosend.send(jsonstring)
                        if io:
                            messages.info(request, "MQTT message has been send!")
                        else:
                            messages.error(request, "Somthing went wrong when sending please try again.")
                    else:
                        messages.error(request, "Sorry this might be not proper json!")
                elif "commandsend" in task:
                    topic = "SYSTEMcontrolDONOTSAVE/bashCOMMAND"
                    pahosend = PahoSend(request.user.username, gateway, topic)
                    io = pahosend.send(textbox)
                    if io:
                        messages.info(request, "MQTT message has been send!")
                    else:
                        messages.error(request, "Somthing went wrong when sending please try again.")
                elif "linkgateway" in task:
                    topic = "SYSTEMcontrolDONOTSAVE/linkgateway"
                    pahosend = PahoSend(request.user.username, gateway, topic)
                    jsonstring = pahosend.checkjson(textbox)
                    if jsonstring:
                        io = pahosend.send(jsonstring)
                        if io:
                            messages.info(request, "MQTT message has been send!")
                        else:
                            messages.error(request, "Somthing went wrong when sending please try again.")
                    else:
                        messages.error(request, "Sorry this might be not proper json!")
                else:
                    messages.error(request, "Somthing went wrong: task ist not clear. Please try again")
                return redirect('input', gateway, task)
            elif request.POST.get("update"):
                return redirect('input', gateway, task)
            elif request.POST.get("cancel"):
                return redirect('gatewaylist')
    else:
        flux_client = FluxDataCon(request.user.username)
        flux_client.last = True
        # label the textbox
        if "jsonfile" in task:
            label = "Json File:"
            # pre fill with saved data in db
            lastentry = flux_client.find(gateway+"/SYSTEMcontrolSAVEJSON/syncfile")
            if lastentry:
                jsonstring = lastentry[0]["posts_body"][0][1]
                form = InputPostForm(initial={"textbox":  jsonstring})
            else:
                form = InputPostForm(initial={"textbox":  "{}"})
        elif "commandsend" in task:
            label = "Send a command to your Gateway (default options: reboot, update, upgrade):"
            form = InputPostForm(initial={"textbox":  "update"})
        elif "linkgateway" in task:
            label = 'Listen to other Gateways (example: {"gatewayID":"topic1/topic2/#"}):'
            # pre fill with saved data in db
            lastentry = flux_client.find(gateway+"/SYSTEMcontrolSAVEJSON/linkgateway")
            if lastentry:
                jsonstring = lastentry[0]["posts_body"][0][1]
                form = InputPostForm(initial={"textbox":  jsonstring})
            else:
                form = InputPostForm(initial={"textbox":  "{}"})
        context = {
            'gateway': "Gateway: "+gateway,
            'label': label
        }
        return render(request, 'users/input.html', {'context':context, 'form':form})


# func. for the setup_rpi site
@login_required
def setup_rpi(request):
    if request.method == 'POST':
        request.POST.get('download', None)
        version = 1
        return redirect('zip-download', version)
    else:
        context = {
            'file': '1'
        }
        return render(request, 'users/setup_rpi.html', context)


# func. for the manual site
@login_required
def manual(request):
    return render(request, 'users/manual.html')


# func. for redirect to a grafana iframe via modif.
@login_required
def tografana(request):
#    return render(request, 'users/dashboard.html')
# somthing not wroking properly with iframe needs more investiagtion.
# work around no iframe via redirect to grafana proxy address
    return redirect(config['GRAFA_ADDRESS'])


# modified page for render Grafana in iframe
@login_required
def iframedash(request):
    return redirect(config['GRAFA_ADDRESS'])


# methode for reverse proxy to grafana with auto login and user validation
@method_decorator(login_required, name='dispatch')
class GrafanaProxyView(ProxyView):
    upstream = 'http://localhost:3000/'
    def get_proxy_request_headers(self, request):
        headers = super(GrafanaProxyView, self).get_proxy_request_headers(request)
        headers['X-WEBAUTH-USER'] = request.user.username
        return headers


# func. for the iotree_show site, for displaying tables
@login_required
def iotree_show(request, tags, time_start, time_end):
    tags = tags.replace("_", "/")
    time_start = int(time_start)
    time_end = int(time_end)
    flux_client = FluxDataCon(request.user.username)
    flux_client.start_time(time_start)
    flux_client.end_time(time_end)
    contexts = flux_client.find(tags)
    del flux_client
    if len(contexts) == 0:
        messages.error(request, 'No Data Found! Data response: '+str(contexts)+'. Given Nodes: '+str(tags) )
        return redirect('treeview')
    else:
        paginator = Paginator(contexts, 1)
        page = request.GET.get('page')
        context = paginator.get_page(page)
        return render(request, 'users/iotree_show.html', {'contexts': context})


# CSV download  return
@login_required
def iotree_download(request, tags, time_start, time_end):
    import csv
    import datetime
    tags = tags.replace("_", "/")
    time_start = int(time_start)
    time_end = int(time_end)
    flux_client = FluxDataCon(request.user.username)
    flux_client.start_time(time_start)
    flux_client.end_time(time_end)
    context = flux_client.find(tags)
    del flux_client
    if len(context) == 0:
        messages.error(request, 'No Data Found! Data response: '+str(context)+'. Given Nodes: '+str(tags) )
        return redirect('treeview')
    else:
        # starting a csv file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format('IoTree42_'+str(datetime.datetime.
                                                                                                         now())+'.csv')
        writer = csv.writer(response, delimiter=';', dialect='excel')
        for z in context:
            # add info about data to csv
            writer.writerow(['tree branchs: ', z['posts_tree']])
            # headings for csv from data mongo
            writer.writerow(z['posts_head'])
            # values for csv form data mongo
            writer.writerows(z['posts_body'])
#            for n in reversed(z['posts_body']):
#                writer.writerow(n)
            writer.writerow(['------', '------', '------', '------', '------', '------', '------'])
        return response


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def iotree_api(request):
    if request.method == 'POST':
        try:
            data = dict(request.data)
            print(data)
            tree = data['tree']
            time_start = data['time_start']
            time_end = data['time_end']
            if time_end == 'now':
                time_end = int(time.time()*1000)
            else:
                time_end = int(time_end)
            time_start = int(time_start)
            flux_client = FluxDataCon(request.user.username)
            flux_client.start_time(time_start)
            flux_client.end_time(time_end)
            context = flux_client.find(tree)
            del flux_client
            if str(context) == "[]":
                context = {"error":"No Data found! or Timeout!", "Info":"Hint: Max rows 200000!"}
            return Response(context)
        except:
            return Response({"status":404,"Info":"Something went wrong when the query", "Hint":"Max rows 200000!"})
    else:
        flux_client = FluxDataCon(request.user.username)
        iotree = flux_client.get_tag_tree()
        leafs = flux_client.get_leafs()
        context = {
            "listofleafs": leafs,
            "iotree": json.loads(iotree)
            }
        del flux_client
        if str(context) == "false":
            context = {"error":"false"}
        if str(context) == "[]":
            context = {"error":"No Data jet!"}
        return Response(context)




