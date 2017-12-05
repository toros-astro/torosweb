from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RankingForm
from .models import TransientCandidate, Ranking, Dataset
from .models import Experiment, Feature
from .forms import ExperimentForm
from django.contrib.auth import get_user_model


# For the comments
# from django_comments.models import Comment
# from django.contrib.sites.shortcuts import get_current_site


def rank(request):
    if request.method == "POST":
        form = RankingForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.ranker = UserModel.objects.get(user=request.user)
            tc_id = int(request.POST.get('tc_id'))
            r.trans_candidate = TransientCandidate.objects.get(pk=tc_id)
            r.save()

            # Now save the comment if there is one.
            # comment_text = request.POST.get('comment')
            # if len(comment_text) > 0:
            #     # save the comment
            #     new_comment = Comment()
            #     new_comment.user = request.user
            #     new_comment.user_name = request.user.username
            #     new_comment.user_email = request.user.email
            #     new_comment.user_url = UserModel.objects.get(user=request.user).website
            #     new_comment.comment = comment_text
            #     new_comment.site = get_current_site(request)
            #     new_comment.content_object = tc
            #     new_comment.save()

            return redirect('winnow:rank')
        else:
            tc_id = int(request.POST.get('tc_id'))
            tc = TransientCandidate.objects.get(pk=tc_id)
    else:
        try:
            # Fetch any tc not ranked yet
            ds = Dataset.objects.filter(isCurrent=True).reverse()[0]
            tc = TransientCandidate.objects.filter(dataset=ds).\
                exclude(ranking=Ranking.objects.all())[0]
        except IndexError:
            # Fetch any tc not ranked by the current user
            try:
                ds = Dataset.objects.filter(isCurrent=True).reverse()[0]
                tc = TransientCandidate.objects.filter(dataset=ds)\
                    .exclude(
                        ranking=Ranking.objects.filter(ranker=request.user))[0]
            except IndexError:
                tc = None

        if tc is None:
            tc_id = -1
        else:
            tc_id = tc.id

        form = RankingForm()

    return render(request, 'winnow/rank.html',
                  {'form': form, 'page_rank': 'selected',
                   'tc_id': tc_id, 'object': tc})


def object_detail(request, object_slug):
    UserModel = get_user_model()

    trans_obj = TransientCandidate.objects.get(slug=object_slug)
    ranked_interesting = Ranking.objects\
        .filter(trans_candidate=trans_obj, isInteresting=True)
    int_users_list = UserModel.objects.filter(ranking=ranked_interesting)
    int_counts = len(int_users_list)

    # if request.method == "POST":
    #     if request.user.is_authenticated():
    #         # Save the comment if there is one.
    #         # comment_text = request.POST.get('comment')
    #         # if len(comment_text) > 0:
    #         #     # save the comment
    #         #     new_comment = Comment()
    #         #     new_comment.user = request.user
    #         #     new_comment.user_name = request.user.username
    #         #     new_comment.user_email = request.user.email
    #         #     new_comment.user_url = \
    #         #         UserModel.objects.get(user=request.user).website
    #         #     new_comment.comment = comment_text
    #         #     new_comment.site = get_current_site(request)
    #         #     new_comment.content_object = trans_obj
    #         #     new_comment.save()

    return render(request, 'winnow/trans_detail.html',
                  {'object': trans_obj, 'interesting_count': str(int_counts),
                   'interesting_user_list': int_users_list})


def data(request):
    if not request.user.is_superuser:
        context = {}
        context['message'] = {
            'headline': "Access denied",
            'body': "You need to be a logged in superuser to view this page"}
        return render(request, 'winnow/message.html', context)

    from django.db.models import Sum
    if request.method == 'POST':
        dataset = request.POST['dataset']
        alltc = TransientCandidate.objects.filter(dataset__name=dataset)

        from django.conf import settings
        import os
        from django.utils import timezone
        dumpfilename = os.path.join(settings.MEDIA_ROOT,
                                    'db_dumps/%s_dump.txt' % (dataset))
        dumpfile = open(dumpfilename, 'w')
        dumpfile.write("#" + str(timezone.now()) + "\n")
        dumpfile.write(
            "#unique_id, object id, dataset id, file name, x_pix, y_pix, "
            "RA, Dec, height, width, original magnitude, "
            "reference magnitude, subtraction magnitude, ranking\n")

        for atc in alltc:
            aline = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " % \
                (atc.slug, atc.object_id, dataset, atc.filename, atc.x_pix,
                 atc.y_pix, atc.ra, atc.dec, atc.height, atc.width,
                 atc.mag_orig, atc.mag_ref, atc.mag_subt)

            rbclass = atc.ranking_set.all().\
                aggregate(Sum('rank'))['rank__sum']
            rbclass = rbclass if rbclass is not None else 0
            aline += "%d\n" % (rbclass)
            dumpfile.write(aline)
        dumpfile.close()

        from django.core.servers.basehttp import FileWrapper
        wrapper = FileWrapper(file(dumpfilename))
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(dumpfilename)
        return response

    else:
        datasets = Dataset.objects.all()
        return render(request, 'winnow/data_interface.html',
                      {'page_data': 'selected', 'datasets': datasets})


def rbmanager(request):
    if request.method == "POST":
        notification_failed = {'value': True, 'type': 'danger',
                               'message': 'The experiment could not be saved'}
        notification_passed = {'value': True, 'type': 'success',
                               'message': 'The experiment has been saved.'}
        exp_form = ExperimentForm(request.POST)
        if exp_form.is_valid():
            # Process form
            if request.user.is_authenticated():
                new_exp = exp_form.instance
                new_exp.user = request.user
                new_exp.save()

                # Create and save the associated features
                all_features = []
                for name, description in exp_form.cleaned_data['features']:
                    new_feat, created = Feature.objects.\
                        get_or_create(name=name.lower())
                    if description != '' and (new_feat.description is None
                                              or new_feat.description == ''):
                        new_feat.description = description

                    new_feat.save()
                    all_features.append(new_feat)
                new_exp.features.add(*all_features)

                notification = notification_passed
                exp_form = ExperimentForm()
            else:  # if user is not authenticated
                notification_failed['message'] = "You need to be logged in " \
                    "to upload an experiment."
                notification = notification_failed

        else:  # if form is not valid:
            notification = notification_failed

    else:  # if request.method == "GET" or otherwise
        exp_form = ExperimentForm()
        notification = {'value': False, 'type': '', 'message': ''}

    return render(request, 'winnow/rbmanager.html',
                  {'exp_form': exp_form,
                   'experiment_list': Experiment.objects.all(),
                   'notification': notification})
