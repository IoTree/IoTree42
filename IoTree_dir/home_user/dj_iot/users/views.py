
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
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, TreePostForm
from django.core.paginator import Paginator
from .mqttcon import InitMqttClient, DelMqttClient
from django.http import HttpResponse, Http404
from django.conf import settings
from .fusioncharts import FusionCharts
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries
from django.contrib.auth.models import User
from datetime import timezone
from .fluxcon import InitInfluxUser, DelInfluxAll, DelInfluxData
from .fluxdatacon import FluxDataCon
from .grafanacon import InitGrafaUser, DelGrafaAll
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
        file_name = 'IoTree_Gateway_V_1.1.zip'
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
            del_flux_client = DelInfluxAll(request.user.username)
            del_flux_client.run()
            del_grafa_client = DelGrafaAll(request.user.username)
            del_grafa_client.run()
            mqttdel = DelMqttClient(request.user.username, request.user.email)
            data = mqttdel.deldel()
            if data:
                messages.success(request, 'All data related to your account has been deleted!')
            else:
                messages.success(request, 'There was no data related to your account!')
            messages.success(request, str(request.user.username) + ' account has been deleted!')
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
            flux_client = FluxDataCon(request.user.username)
            time_start = int(time_start*1000)
            time_end = int(time_end*1000)
            flux_client.start_time(time_start)
            flux_client.end_time(int(time.time())*1000)
            contexts = flux_client.find(tree)
            treee = tree.replace("/", "_")
            if len(contexts) == 0:
                messages.error(request, 'No Data Found! Data response: '+str(contexts)+'. Given Nodes: '+str(tree) )
                return redirect('treeview')
            else:
                if action == 'chart':
                    return redirect('iotree-chart', str(treee), time_start, time_end)
                if action == 'table':
                    return redirect('iotree-show', str(treee), time_start, time_end)
                if action == 'download':
                    return redirect('iotree-download', str(treee), time_start, time_end)
                if action == 'delete':
                    tags = flux_client.get_raw_tags(str(tree))
                    if tags == "":
                        messages.info(request, "No Date Found! on delete")
                        return redirect('treeview')
                    else:
                        flux_del = DelInfluxData(request.user.username, tags)
                        response = flux_del.run()
                        messages.info(request, 'Measuerments droped: '+str(tags)+'Database response: '+str(response))
                        del flux_del
                        del flux_client
                        return redirect('treeview')
    else:
        form = TreePostForm(initial={'time_end':datetime.datetime.now()})
        flux_client = FluxDataCon(request.user.username)
        context = flux_client.get_tag_tree()
        if str(context) == "[]":
            messages.info(request, 'No data jet!')
        return render(request, 'users/treeview.html', {'context':context, 'form':form})


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


# func. for the grafana site
@login_required
def tografana(request):
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
    paginator = Paginator(contexts, 1)
    page = request.GET.get('page')
    context = paginator.get_page(page)
    return render(request, 'users/iotree_show.html', {'contexts': context})


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
        for n in reversed(z['posts_body']):
            writer.writerow(n)
        writer.writerow(['------', '------', '------', '------', '------', '------', '------'])
    return response


@login_required
def iotree_chart(request, tags, time_start, time_end):
    tags = tags.replace("_", "/")
    time_start = int(time_start)
    time_end = int(time_end)
    flux_client = FluxDataCon(request.user.username)
    flux_client.start_time(time_start)
    flux_client.end_time(time_end)
    contexts = flux_client.find(tags)
    caption = "'"+'Tags: '+str(tags)+"'"
    # render page with given data
    i = 0
    for n in contexts:
        data = n['posts_body']
        subcaption = "'" + 'Tree Branch: ' + n['posts_tree']+ "'"
        # make schema with shema function
        schema = flux_client.shema(n['posts_head'])

        fusionTable = FusionTable(schema, data)
        timeSeries = TimeSeries(fusionTable)

        timeSeries.AddAttribute("caption", "{text: "+caption+"}")
        timeSeries.AddAttribute("subcaption", "{ text: "+subcaption+"}")
        timeSeries.AddAttribute("series", "'Type'")
        timeSeries.AddAttribute("yAxis", "[{plot: 'Sales Value',title: 'Sale Value',format: {prefix: '$'}}]")

        # Create an object for the chart using the FusionCharts class constructor
        fcchart = FusionCharts("timeseries", "ex1", 700, 450, "chart-1", "json", timeSeries)
        # returning complete JavaScript and HTML code, which is used to generate chart in the browsers.
        contexts[i]['posts_chart'] = fcchart.render()
        i += 1
    paginator = Paginator(contexts, 1)
    page = request.GET.get('page')
    context = paginator.get_page(page)
    return render(request, 'users/iotree_chart.html', {'contexts': context})



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
            return Response(context)
        except:
            return Response({"status":404})
    else:
        flux_client = FluxDataCon(request.user.username)
        context = flux_client.get_tag_tree()
        if str(context) == "false":
            context = {"error":"false"}
        if str(context) == "[]":
            context = {"error":"No Data jet!"}
        return Response(context)




