from django.shortcuts import render
from .models import Assignment, Observatory, SuperEvent, SourceCatalog, GCNNotice
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, get_list_or_404


def process_assignment_form(request):
    the_alert = GCNNotice.objects.filter(pk=request.POST['alert_id']).get()
    obs_id = int(request.POST['obs_id'])
    obs = Observatory.objects.get(pk=obs_id)

    obs_asg = Assignment.objects.filter(gcnnotice=the_alert, observatory=obs)

    aretakenlist = [int(k) for k in request.POST.getlist('istaken[]')]
    areobservedlist = [int(k) for k in request.POST.getlist('wasobserved[]')]

    def taken_by_others(asg):
        other_assng = Assignment.objects.filter(gcnnotice=the_alert)\
            .exclude(observatory=asg.observatory)\
            .filter(is_taken=True, target=asg.target)
        return other_assng.exists()

    def turn_on_taken(asg):
        if asg.is_taken is False:
            asg.is_taken = True

    def turn_off_taken(asg):
        if asg.is_taken is True:
            asg.is_taken = False

    for asg in obs_asg:
        if asg.id in aretakenlist:
            if not taken_by_others(asg) \
                    or asg.id in areobservedlist:
                turn_on_taken(asg)
            else:
                turn_off_taken(asg)
        else:
            turn_off_taken(asg)
        if asg.id in areobservedlist:
            if asg.was_observed is False:
                asg.was_observed = True
        else:
            if asg.was_observed is True:
                asg.was_observed = False
        asg.save()
    return 200, []


def process_upload_target_form(request):
    from django.utils import timezone

    assgn_text = request.POST.get('assignments', '')
    alert_id = request.POST.get('alert', None)
    thealert = GCNNotice.objects.get(pk=alert_id)

    was_error = False
    error_msg = []

    if not request.user.groups.filter(name='broker_admins').exists():
        error_msq = ["You don't have enough permissions to upload targets."]
        return 403, error_msg

    obss = list(filter(None, assgn_text.split(';')))
    for anobs_text in obss:
        split = anobs_text.split(':')
        try:
            obs, obj_text = split
        except:
            was_error = True
            error_msg.append("Error parsing line: {}".format(anobs_text))
            continue
        obs = obs.strip()
        name_lookup = Q(name__contains=obs) | Q(short_name__contains=obs)
        try:
            theobs = Observatory.objects.get(name_lookup)
        except:
            was_error = True
            error_msg.append("Could not find observatory {}".format(obs))
            continue
        objs = [obj.strip() for obj in filter(None, obj_text.split(','))]
        for obj_prob in objs:
            try:
                obj_prob_split = list(filter(None, obj_prob.split()))
                if len(obj_prob_split) == 1:
                    obj = obj_prob_split[0]
                    prob = 0.0
                else:
                    obj, prob = obj_prob_split
                    prob = float(prob)
            except:
                was_error = True
                error_msg.append("Could not parse '{}'".format(obj_prob))
                continue
            try:
                theobj = SourceCatalog.objects.get(name=obj)
            except:
                was_error = True
                error_msg.append("Could not find object {}".format(obj))
                continue
            new_assgn = Assignment(
                target=theobj, observatory=theobs,
                gcnnotice=thealert, datetime=timezone.now(), probability=prob)
            new_assgn.save()

    return (200, error_msg) if not error_msg else (400, error_msg)


def has_broker_access(user):
    return user.groups.filter(name__in=['broker_admins',
                                        'telescope_operators'])


@user_passes_test(has_broker_access)
def index(request, grace_id=None, gcn_pk=None):
    context = {}
    status = 200
    if request.method == 'POST' and 'upload_target' in request.POST:
        status, context['errors'] = process_upload_target_form(request)
    if request.method == 'POST' and 'upload_target' not in request.POST:
        status, context['errors'] = process_assignment_form(request)

    context['alerts'] = GCNNotice.objects.order_by('-datetime')
    context['super_event_name'] = SuperEvent.objects.order_by('-datetime')
    
    try:
        if grace_id is None:
            the_alert = GCNNotice.objects.order_by('-datetime').first()
            super_event_names = SuperEvent.objects.order_by('-datetime')
        else:
            the_alert = GCNNotice.objects.filter(superevent__grace_id=grace_id)
            super_event_names = SuperEvent.objects.order_by('-datetime')
            if gcn_pk is None:
                the_alert = the_alert.order_by('-datetime').first()
                super_event_names = SuperEvent.objects.order_by('-datetime')
            else:
                the_alert = the_alert.get(pk=gcn_pk)
                super_event_names = SuperEvent.objects.order_by('-datetime')
    except:
        return HttpResponseNotFound()
    context['the_alert'] = the_alert
    context['super_event_names'] = super_event_names
    
    context['all_assingments'] = Assignment.objects\
        .filter((Q(is_taken=True) | Q(was_observed=True)), gcnnotice=the_alert)\
        .order_by('target__name')

    selected_targets = Assignment.objects.filter(
        gcnnotice=the_alert, is_taken=True).count()
    context['selected_targets'] = selected_targets

    observed_targets = Assignment.objects.filter(
        gcnnotice=the_alert, was_observed=True).count()
    context['observed_targets'] = observed_targets

    def taken_by_others(asg):
        other_assng = Assignment.objects.filter(gcnnotice=the_alert)\
            .exclude(observatory=asg.observatory)\
            .filter(is_taken=True, target=asg.target)
        return other_assng.exists()

    assn_per_obs = []
    for obs in Observatory.objects.all():
        assgnms = Assignment.objects.filter(gcnnotice=the_alert, observatory=obs)
        for asg in assgnms:
            if (not asg.is_taken) and taken_by_others(asg):
                asg.flag_unavailable = True
            else:
                asg.flag_unavailable = False
        assn_per_obs.append([obs, assgnms])
    context['assn_per_obs'] = assn_per_obs
    context['is_admin'] = request.user.groups.filter(name='broker_admins').exists()

    return render(request, 'broker/index.html', context, status=status)


@login_required
@require_POST
@csrf_exempt
def uploadjson(request):
    import json
    import datetime as d
    import pytz
    from django.utils import timezone
    try:
        # Parse alert
        targetsjson = json.loads(request.POST["targets.json"])
        alert = targetsjson['alert']
        dt = d.datetime.strptime(alert["datetime"], "%Y-%m-%dT%H:%M:%S.%f")
        dt = pytz.utc.localize(dt)
        thealert, created = SuperEvent.objects.get_or_create(
            grace_id=alert["graceid"],
            defaults={
                'datetime':dt,
                'ligo_run':alert['ligo_run'],
                'se_type':alert['SEtype'],
                },
            )
        gcnnotice = targetsjson['gcnnotice']
        dt = d.datetime.strptime(gcnnotice["datetime"], "%Y-%m-%dT%H:%M:%S")
        dt = pytz.utc.localize(dt)
        gcntype_translation = {
            'Preliminary': 0,
            'Initial': 1,
            'Update': 2,
            'Retraction': 3,
            }
        thegcn = GCNNotice(
            gcnorigin='GW',
            gcntype=gcntype_translation[gcnnotice['gcntype']],
            serialnumber=gcnnotice['gcnserial'],
            datetime=dt,
            superevent=thealert,
            )
        thegcn.save()
        if gcnnotice['gcntype'] == 'Retraction':
            thealert.was_retracted = True
            thealert.save()
        if "assignments" in targetsjson:
            for obs_name, obs_assgn in targetsjson["assignments"].items():
                name_lookup = (Q(name__contains=obs_name) |
                               Q(short_name__contains=obs_name))
                try:
                    theobs = Observatory.objects.get(name_lookup)
                except:
                    continue
                for obj, prob in obs_assgn.items():
                    try:
                        theobj = SourceCatalog.objects.get(name=obj)
                    except:
                        continue
                    new_assgn = Assignment(
                        target=theobj,
                        observatory=theobs,
                        gcnnotice=thegcn,
                        datetime=timezone.now(),
                        probability=prob
                        )
                    new_assgn.save()
    except:
        return HttpResponseBadRequest()
    return HttpResponse()
