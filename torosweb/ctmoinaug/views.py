from django.shortcuts import render
from .models import Activity


def activity_detail(request):
    activities = Activity.objects.all()
    return render(request, 'ctmoinaug/activities.html', 
                  {'activities': activities, })
    