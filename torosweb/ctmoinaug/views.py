from django.shortcuts import render
from .models import Activity
from .forms import ActivityForm

def activity_detail(request):
    if request.method == "POST":
        form = ActivityForm(request.POST) 
        if form.is_valid():
            activity = form.save()
            form = ActivityForm()
    else:
        form = ActivityForm()
    can_see_info = request.user.groups.filter(name='ctmo_admin').exists()
    print(can_see_info)
    activities = Activity.objects.all()
    return render(request, 'ctmoinaug/activities.html', 
                  {'activities': activities, 'form': form,
                  'do_disclose': can_see_info})
