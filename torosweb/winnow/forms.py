from django import forms
from .models import Ranking, Experiment


class RankingForm(forms.ModelForm):
    RANKING_OPTIONS = ((1, 'Yes'),
                       (-1, 'No'),
                       (0, "I don't know"))
    rank = forms.ChoiceField(choices=RANKING_OPTIONS, widget=forms.RadioSelect, help_text="Options")
    isInteresting = forms.BooleanField(help_text = 'Mark as interesting', initial=False, required=False)
    
    class Meta:
        model = Ranking
        fields = ('rank', 'isInteresting')


class ExperimentForm(forms.ModelForm):
    features = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': "feature1: some description, feature2, "
            "feature3, feature4: another description"}),
        required=False)

    class Meta:
        model = Experiment
        exclude = ['user']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def clean(self):
        cleaned_data = super(ExperimentForm, self).clean()
        alg_name = self.cleaned_data.get('alg_name', None)
        if alg_name is not None:
            cleaned_data['alg_name'] = alg_name.title()

        def feature_set(feature_text_field):
            def parse_descriptions(astr):
                the_split = astr.split(':')
                if len(the_split) == 1:
                    return [astr.strip(), ""]
                else:
                    return [the_split[0].strip(), the_split[1].strip()]

            return [parse_descriptions(afeat)
                    for afeat in feature_text_field.split(',')]

        the_feat = self.cleaned_data.get('features', None)
        if the_feat is not None:
            cleaned_data['features'] = feature_set(the_feat)

        return cleaned_data
