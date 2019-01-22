from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from generalobj.views import general_obj, general_objs, general_obj_new, \
        general_obj_edit

from .forms import BugForm
from .models import BugStatus, Priority, Severity, Category, Bug, BugEntity, \
        Document
from .utils import get_next_statuses

import datetime, random, re, os

@login_required
def bugs(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        bugstatus = request.POST.getlist('bugstatus', '')
        user = request.POST.getlist('user', '')
        executor = request.POST.getlist('executor', '')
        tester = request.POST.getlist('tester', '')
        priority = request.POST.getlist('priority', '')
        severity = request.POST.getlist('severity', '')
        category = request.POST.getlist('category', '')
        assigned_to = request.POST.getlist('assigned_to', '')
        text = request.POST.get('text', '')
        text_type = request.POST.getlist('text_type', '')
        submit_save_search = request.POST.get('submit_save_search', '')
        submit_save_and_search = request.POST.get('submit_save_and_search', '')
        submit_search = request.POST.get('submit_search', '')
        if bugstatus or user or executor or tester or priority or severity or \
                category or assigned_to or text:
            terms = []
            if bugstatus:
                terms.append('bugstatus=%s' % ','.join(bugstatus))
            if user:
                terms.append('user=%s' % ','.join(user))
            if executor:
                terms.append('executor=%s' % ','.join(executor))
            if tester:
                terms.append('tester=%s' % ','.join(tester))
            if priority:
                terms.append('priority=%s' % ','.join(priority))
            if severity:
                terms.append('severity=%s' % ','.join(severity))
            if category:
                terms.append('category=%s' % ','.join(category))
            if assigned_to:
                terms.append('assigned_to=%s' % ','.join(assigned_to))
            if text:
                if 'subject' in text_type:
                    terms.append('subject=%s' % text)
                if 'description' in text_type:
                    terms.append('text=%s' % text)
                if 'flow' in text_type:
                    terms.append('flow=%s' % text)
            if submit_save_search or submit_save_and_search:
                SavedSearch.objects.create(user = request.user, name=name, \
                        search_phrase='?%s' % '&'.join(terms))
                request.session['info'] = ('Search has been saved successfully')
            if submit_save and search or submit_search:
                return HttpResponseRedirect('%s?%s' % \
                        (reverse('bugs'), '&'.join(terms)))
        return HttpResponseRedirect(reverse('bugs'))

    pass_to_template = {'bugstatuses': BugStatus.objects.filter(), \
            'users': User.objects.filter().order_by('last_name'), \
            'priorities': Priority.objects.filter(), \
            'severities': Severity.objects.filter(), \
            'categories': Category.objects.filter(), \
            'saved_searches': request.user.savedsearch_set.all()}

    query_term = ''
    bugstatus = request.GET.get('bugstatus', '')
    user = request.GET.get('user', '')
    executor = request.GET.get('executor', '')
    tester = request.GET.get('tester', '')
    priority = request.GET.get('priority', '')
    severity = request.GET.get('severity', '')
    category = request.GET.get('category', '')
    assigned_to = request.GET.get('assigned_to', '')
    subject = request.GET.get('subject', '')
    text = request.GET.get('text', '')
    flow = request.GET.get('flow', '')
    if bugstatus or user or executor or tester or priority or severity or \
            category or assigned_to or subject or text or flow:
        query_dict = {}
        if bugstatus:
            query_dict['bugstatus__code__in'] = bugstatus.split(',')
        if user:
            query_dict['__id__in'] = user.split(',')
        if executor:
            query_dict['__id__in'] = executor.split(',')
        if tester:
            query_dict['__code__in'] = tester.split(',')
        if priority:
            query_dict['__code__in'] = priority.split(',')
        if severity:
            query_dict['__code__in'] = severity.split(',')
        if category:
            query_dict['__code__in'] = category.split(',')
        if assigned_to:
            query_dict['__id__in'] = assigned_to.split(',')
        if subject:
            query_dict['subject__icontains'] = subject
        if text:
            query_dict['text__icontains'] = text
        if flow:
            query_dict['bugentity__text__icontains'] = flow
        excluded_query_dict = {}
    else:
        query_dict = {}
        excluded_query_dict = {'bugstatus__code__in': ['backlog', 'postponed', \
                'closed', 'cancelled']}
    columns_to_be_shown = ['id', 'priority', 'severity', 'bugstatus', \
            'subject', 'last_modified', 'assigned_to']
    return general_objs(request, Bug, BugForm, columns_to_be_shown, \
            query_term = query_term, \
            query_dict = query_dict, \
            excluded_query_dict = excluded_query_dict, \
            additional_template = 'bugtrack/templates/bugs_extra.html', \
            pass_to_template = pass_to_template)


@login_required
def bug_new(request):
    def postaction(obj):
        obj.user = request.user
        obj.bugstatus = BugStatus.objects.filter().order_by('id')[0]
        return obj

    return general_obj_new(request, Bug, BugForm, \
            callback_postaction=postaction)


@login_required
def bug(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    ret_dic = {}
    if request.method == 'POST':
        new_entry = request.POST.get('new_entry', '')
        submit_new_entry = request.POST.get('submit_new_entry', '')
        waiting_for_reply = request.POST.get('waiting_for_reply', '')
        private = request.POST.get('private', '')
        new_status = request.POST.get('new_status', '')
        new_assigned_to = request.POST.get('new_assigned_to', '')
        safe = request.POST.get('safe', '')
        if submit_new_entry:
            if new_entry:
                print(request.POST)
                private = False
                if private:
                    private = True
                safe = False
                if safe:
                    safe = True
                bug_entity = BugEntity.objects.create(user=request.user, \
                        bug=bug, text=new_entry, private=private, safe=safe)
                bug.last_modified = datetime.datetime.now()
                if waiting_for_reply:
                    bug.waiting_for_reply = True
                for pt in range(0, 5):
                    form_file_name = 'new_entry_file%s' % pt
                    if form_file_name in request.FILES:
                        file_to_upload = request.FILES[form_file_name]
                        size = file_to_upload._get_size()
                        if size > 0:
                            document = Document(user=request.user, \
                                    description='_', \
                                    name=re.sub('[^0-9a-zA-Z.]', '_', file_to_upload._get_name()), \
                                    size=size)
                            document.path = os.path.join(settings.MEDIA_ROOT, \
                                    'bug_entity__%s__%s' % (datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S'),
                                    random.random()))
                            with open(document.path, 'wb+') as destination:
                                for chunk in file_to_upload.chunks():
                                    destination.write(chunk)
                            document.save()
                            bug_entity.document_set.add(document)
                bug.save()
        if new_status:
            print(request.POST)
            try:
                bugstatus = BugStatus.objects.get(code=new_status)
            except:
                request.session['err'] = ('Invalid BugStatus', )
                return HttpResponseRedirect(reverse('bug', args=(bug_id,)))
            BugEntity.objects.create(user=request.user, bug=bug, \
                    new_status=True, \
                    text="%s->%s" % (bug.bugstatus.name, bugstatus.name))
            bug.bugstatus = bugstatus
            bug.save()
            pass
        if new_assigned_to:
            try:
                old_assigned_to = bug.assigned_to
                bug.assigned_to = User.objects.get(username = new_assigned_to)
                bug.save()
                print('3')
                BugEntity.objects.create(user=request.user, bug=bug, \
                        new_assignment=True, \
                        text="%s->%s" % (old_assigned_to, new_assigned_to))
                print('4')
            except:
                request.session['err'] = \
                        ('Error at assigned to %s' % new_assigned_to,)
        print(request.session)
        return HttpResponseRedirect(reverse('bug', args=(bug_id,)))
    ret_dic['bug'] = bug
    dt = {}
    term = Q()
    ret_dic['bugentities'] = bug.bugentity_set.filter(**dt).filter(term).\
            distinct().order_by('-created')
    ret_dic['next_statuses'] = get_next_statuses(bug)
    ret_dic['can_be_edited'] = bug.can_be_edited(request.user)
    ret_dic['can_be_commented'] = bug.can_be_commented(request.user)
    ret_dic['assigned_tos'] = User.objects.filter().\
            exclude(username=bug.assigned_to.username)
    return render(request, 'bugtrack/templates/bug.html', ret_dic)


@login_required
def bug_edit(request, bug_id):
    return general_obj_edit(request, Bug, BugForm)


@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    fl = open(document.path, 'rb')
    response = HttpResponse(fl, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % document.name
    return response