from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, IDPostForm, InquiryPostForm
from .mango import MongoCon
from django.core.paginator import Paginator


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


@login_required
def iotree(request):
    if request.method == 'POST':
        form = IDPostForm(request.POST)
        if form.is_valid():
            gateway_id = form.cleaned_data['gateways_id']
            query = MongoCon(gateway_id, request.user.username)
            record = query.find()
            if record:
                return redirect('iotree-branch', gateway_id)
            else:
                messages.info(request, f'Gateway: ' + gateway_id + f' not found')
                return render(request, 'users/iotree.html', {'form': form})
    else:
        form = IDPostForm()
        return render(request, 'users/iotree.html', {'form': form})


@login_required
def iotree_branch(request, gateway_id):
    if request.method == 'POST':
        # some spacing for transmitting tree list as sting over url
        import ast
        treeasstring1 = request.POST.get('postdownload', None)
        treeasstring2 = request.POST.get('postshow', None)
        if treeasstring1:
            treeaslist = ast.literal_eval(treeasstring1)
            tree = "_".join(treeaslist)
            return redirect('iotree-download', gateway_id, tree, 'data', 'True', 'False')
        if treeasstring2:
            treeaslist = ast.literal_eval(treeasstring2)
            tree = "_".join(treeaslist)
            return redirect('iotree-show', gateway_id, tree, 'data', 'True', 'False')
    else:
        query = MongoCon(gateway_id, request.user.username)
        contexts = query.find()
        messages.success(request, f'Tree branches from gateway: ' + gateway_id)
        return render(request, 'users/iotree_branch.html', {'contexts': contexts})


@login_required
def iotree_show(request, gateway_id, tree, filters, in_order, negated):
    # connecting to mongodb
    query = MongoCon(gateway_id, request.user.username)
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
    query.resultdef(filters)
    # query with given info
    contexts = query.find()
    print(contexts)
    # make more than one sinde if nesserey
    paginator = Paginator(contexts, 1)
    page = request.GET.get('page')
    context = paginator.get_page(page)
    # give som info about the search
    tree_branch = tree.replace('_', ' -> ')
    messages.success(request, f'Gateway: ' + gateway_id)
    messages.info(request, f'Tree search: ' + tree_branch)
    # render page with given data
    return render(request, 'users/iotree_show.html', {'contexts': context})


@login_required
def iotree_download(request, gateway_id, tree, filters, in_order, negated):
    # import some tools for making and sending a csv file
    import csv
    import datetime
    from django.http import HttpResponse
    # connecting to mongodb
    query = MongoCon(gateway_id, request.user.username)
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
    query.resultdef(filters)
    # query with given info
    context = query.find()
    # starting a csv file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(gateway_id+'_'+tree+'_'+str(datetime.datetime.
                                                                                                     now())+'.csv')
    writer = csv.writer(response)
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


@login_required
def inquiry(request):
    if request.method == 'POST':
        form = InquiryPostForm(request.POST)
        if form.is_valid():
            import re
            gateway_id = form.cleaned_data.get('gateway_id')
            tree = form.cleaned_data.get('tree_branch')
            filters = form.cleaned_data.get('filters')
            in_order = form.cleaned_data.get('in_order')
            negated = form.cleaned_data.get('negated')
            if tree:
                tree = re.sub("\s+", "", tree)
                tree = tree.split(',')
                tree = '_'.join(tree)
            else:
                tree = "_"
            if 'table' in request.POST:
                return redirect('iotree-show', gateway_id, tree, filters, in_order, negated)
            elif 'download' in request.POST:
                return redirect('iotree-download', gateway_id, tree, filters, in_order, negated)
    else:
        form = InquiryPostForm()
        return render(request, 'users/inquiry.html', {'form': form})
