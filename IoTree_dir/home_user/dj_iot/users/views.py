
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
from .forms import UserUpdateForm, ProfileUpdateForm, IDPostForm, InquiryPostForm, UserRegisterForm
from .mango import MongoCon
from django.core.paginator import Paginator
from .mqttcon import InitMqttClient, DelMqttClient
from django.http import HttpResponse, Http404
from django.conf import settings
from .fusioncharts import FusionCharts
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries
from django.contrib.auth.models import User
from datetime import timezone
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import datetime


# func. for process the zip_download request
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
            user = form.save(commit=False)
            init_mqtt_client = InitMqttClient(user_name, user_email)
            mqttpw = init_mqtt_client.run()
            user.first_name = "was given to you when registering."
            user.save()
            messages.success(request, str(user_name)+' account has been created! You are now able to log in!')
            messages.info(request, 'Your MQTT-Password is: -->'+str(mqttpw)+'<-- keep it safe. There is no way to restore it.')
            mqttpw = None
            del init_mqtt_client
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
            data_del = MongoCon(request.user.username)
            data = data_del.delete_all()
            mqttdel = DelMqttClient(request.user.username, request.user.email)
            mqttdel.deldel()
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
def iotree(request):
    if request.method == 'POST':
        form = IDPostForm(request.POST, user=request.user)
        if form.is_valid():
            gateway_id = form.cleaned_data['gateway_id']
            query = MongoCon(request.user.username)
            query.set_gateway_id(gateway_id)
            record = query.find()
            if record:
                return redirect('iotree-branch', gateway_id)
            else:
                messages.info(request, 'There is no data jet!')
                return render(request, 'users/iotree.html', {'form': form})
    else:
        form = IDPostForm(user=request.user)
        return render(request, 'users/iotree.html', {'form': form})


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


# func. for the iotree_branch site
@login_required
def iotree_branch(request, gateway_id):
    if request.method == 'POST':
        # some spacing for transmitting tree list as sting over url
        import ast
        treeasstring1 = request.POST.get('postdownload', None)
        treeasstring2 = request.POST.get('postshow', None)
        treeasstring3 = request.POST.get('postchart', None)
        if treeasstring1:
            treeaslist = ast.literal_eval(treeasstring1)
            tree = "_".join(treeaslist)
            return redirect('iotree-download', gateway_id, tree, 'data', 'True', 'False', str(0), 'now')
        if treeasstring2:
            treeaslist = ast.literal_eval(treeasstring2)
            tree = "_".join(treeaslist)
            return redirect('iotree-show', gateway_id, tree, 'data', 'True', 'False', str(0), 'now')
        if treeasstring3:
            treeaslist = ast.literal_eval(treeasstring3)
            tree = "_".join(treeaslist)
            return redirect('iotree-chart', gateway_id, tree, 'data', 'True', 'False', str(0), 'now')
    else:
        query = MongoCon(request.user.username)
        query.set_gateway_id(gateway_id)
        contexts = query.find()
        messages.success(request, 'Tree branches from gateway: ' + gateway_id)
        return render(request, 'users/iotree_branch.html', {'contexts': contexts})


# func. for the iotree_show site, for displaying tables
@login_required
def iotree_show(request, gateway_id, tree, filters, in_order, negated, time_start, time_end):
    # connecting to mongodb
    query = MongoCon(request.user.username)
    query.set_gateway_id(gateway_id)
    # process tree data to list
    mongotree = tree.split('_')
    while "" in mongotree:
        mongotree.remove("")
    query.tree(mongotree)
    # process in_order to bool
    in_order = in_order == 'True'
    query.order(in_order)
    # process negated to bool
    negated = negated == 'True'
    query.invert(negated)
    query.result_def(filters)
    # process time_.. back to float
    if time_end == 'now':
        time_end = time.time()
    else:
        time_end = int(time_end) / 1000
    time_start = int(time_start)/1000
    query.start_time(time_start)
    query.end_time(time_end)
    # query with given info
    contexts = query.find()
    print(contexts)
    # make more than one page if necessary
    if filters == "tree":
        inst = 30
    else:
        inst = 1
    paginator = Paginator(contexts, inst)
    page = request.GET.get('page')
    context = paginator.get_page(page)
    # give som info about the search
    tree_branch = tree.replace('_', ' -> ')
    messages.success(request, 'Gateway: ' + gateway_id)
    messages.info(request, 'Tree branch search: ' + tree_branch)
    # render page with given data
    return render(request, 'users/iotree_show.html', {'contexts': context})


# func. for the iotree_download process
@login_required
def iotree_download(request, gateway_id, tree, filters, in_order, negated, time_start, time_end):
    # import some tools for making and sending a csv file
    import csv
    import datetime
    # connecting to mongodb
    query = MongoCon(request.user.username)
    query.set_gateway_id(gateway_id)
    # process tree data to list
    mongotree = tree.split('_')
    while "" in mongotree:
        mongotree.remove("")
    query.tree(mongotree)
    # process in_order to bool
    in_order = in_order == 'True'
    query.order(in_order)
    # process negated to bool
    negated = negated == 'True'
    query.invert(negated)
    query.result_def(filters)
    # process time_.. back to float
    if time_end == 'now':
        time_end = time.time()
    else:
        time_end = int(time_end) / 1000
    time_start = int(time_start) / 1000
    query.start_time(time_start)
    query.end_time(time_end)
    # set time_unix to true -> time is also in raw (unix) available
    query.time_unix(True)
    # query with given info
    context = query.find()
    # starting a csv file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(gateway_id+'_'+tree+'_'+str(datetime.datetime.
                                                                                                     now())+'.csv')
    writer = csv.writer(response, delimiter=';', dialect='excel')
    for z in context:
        # add info about data to csv
        writer.writerow(['gateway: ', gateway_id, 'tree branch: ', ','.join(z['posts_tree'])])
        # headings for csv from data mongo
        writer.writerow(z['posts_head'])
        # values for csv form data mongo
        for n in z['posts_body']:
            writer.writerow(n)
        writer.writerow(['------', '------', '------', '------', '------', '------', '------'])
    return response


# func. for the inquiry site
@login_required
def inquiry(request):
    if request.method == 'POST':
        form_a = InquiryPostForm(request.POST)  # save Post in from_a
        form_b = IDPostForm(request.POST, user=request.user)  # save Post in from_b
        if form_a.is_valid() and form_b.is_valid():  # check if inputs a valid
            import re
            gateway_id = form_b.cleaned_data.get('gateway_id')
            if gateway_id != 'no data':  # check if there is a gateway astaplished
                # make all nessery variables with given data from Post
                tree = form_a.cleaned_data.get('tree_branch')
                filters = form_a.cleaned_data.get('filters')
                in_order = form_a.cleaned_data.get('in_order')
                negated = form_a.cleaned_data.get('negated')
                time_start = form_a.cleaned_data.get('time_start')
                time_end = form_a.cleaned_data.get('time_end')
                time_start = time_start.replace(tzinfo=timezone.utc).timestamp()
                time_start = int(time_start*1000)
                time_end = time_end.replace(tzinfo=timezone.utc).timestamp()
                time_end = int(time_end*1000)
                if tree:
                    tree = re.sub("\s+", "", tree)
                    tree = tree.split(',')
                    tree = '_'.join(tree)
                else:
                    tree = "_"
                # redirect web user with given information to the desired site / task
                if 'table' in request.POST:
                    return redirect('iotree-show', gateway_id, tree, filters, in_order, negated, time_start, time_end)
                elif 'download' in request.POST:
                    return redirect('iotree-download', gateway_id, tree, filters, in_order, negated, time_start, time_end)
                elif 'chart' in request.POST:
                    return redirect('iotree-chart', gateway_id, tree, filters, in_order, negated, time_start, time_end)
            # if there is now data jet give the user a short feedback
            else:
                messages.info(request, 'There is no data jet!')
                return render(request, 'users/inquiry.html', {'form_a': form_a,
                                                              'form_b': form_b})
    # render all input fields
    else:
        form_a = InquiryPostForm(initial={'time_end':datetime.datetime.now()})
        form_b = IDPostForm(user=request.user)
        return render(request, 'users/inquiry.html', {'form_a': form_a,
                                                      'form_b': form_b})


# func. for the iotree_chart site
@login_required
def iotree_chart(request, gateway_id, tree, filters, in_order, negated, time_start, time_end):
    # connecting to mongodb
    query = MongoCon(request.user.username)
    query.set_gateway_id(gateway_id)
    # process tree data to list
    mongotree = tree.split('_')
    while "" in mongotree:
        mongotree.remove("")
    query.tree(mongotree)
    # process in_order to bool
    in_order = in_order == 'True'
    query.order(in_order)
    # process negated to bool
    negated = negated == 'True'
    query.invert(negated)
    query.result_def(filters)
    # process time_.. back to float
    if time_end == 'now':
        time_end = time.time()
    else:
        time_end = int(time_end) / 1000
    time_start = int(time_start) / 1000
    query.start_time(time_start)
    query.end_time(time_end)
    # query with given info
    contexts = query.find()
    # make more than one page if necessary
    caption = "'"+'Gateway: '+str(gateway_id)+"'"
    # render page with given data
    i = 0
    for n in contexts:
        data = n['posts_body']
        subcaption = "'" + 'Tree Branch: ' + '->'.join(n['posts_tree']) + "'"
        # make schema with shema function form MangoCon
        schema = query.shema(n['posts_head'])
        print(schema)

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
    # using django paginator to make more pages
    paginator = Paginator(contexts, 1)
    page = request.GET.get('page')
    context = paginator.get_page(page)
    return render(request, 'users/iotree_chart.html', {'contexts': context})


# func. for the rest_api
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def iotree_api(request):
    if request.method == 'POST':
        try:
            data = dict(request.data)
            print(data)
            gateway_id = data['gateway_id']
            tree = data['tree']
            filters = data['filters']
            in_order = data['in_order']
            negated = data['negated']
            time_start = data['time_start']
            time_end = data['time_end']
            query = MongoCon(request.user.username)
            query.set_gateway_id(gateway_id)
            # process tree data to list
            mongotree = tree.split('_')
            while "" in mongotree:
                mongotree.remove("")
            query.tree(mongotree)
            # process in_order to bool
            in_order = in_order == 'True'
            query.order(in_order)
            # process negated to bool
            negated = negated == 'True'

            query.invert(negated)
            query.result_def(filters)
            # process time_.. back to float
            if time_end == 'now':
                time_end = time.time()
            else:
                time_end = int(time_end) / 1000
            time_start = int(time_start) / 1000
            query.start_time(time_start)
            query.end_time(time_end)
            query.time_unix(True)
            # query with given info
            context = query.find()
            return Response(context)
        except:
            return Response({"status":404})
    # connecting to mongodb to find related gateways to user
    query = MongoCon(request.user.username)
    gateways = query.find_gateways()
    return Response(gateways)
