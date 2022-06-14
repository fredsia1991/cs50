from logging import PlaceHolder
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.shortcuts import render
import markdown2

from . import util

class newEntryForm(forms.Form):
    title = forms.CharField(label="Entry Title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8', 'placeholder':'Type here!'}))
    content = forms.CharField(label="Entry Content", widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows': 10}))
    edit = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
        "entry": markdown2.markdown(entryPage),
        "entryTitle": entry
    })

def search(request):
        value = request.GET.get('q','')
        #"GET" is usually to fetch data, instead of changing data
        if (util.get_entry(value)) is not None:
            return render(request, "encyclopedia/entry.html", {
                "entryTitle": value,
                "entry": util.get_entry(value)
            })
        else:
            # What we want to do here, is to iterate over each "Entry" that we have, and see if the input value
            # is in the title of these entries. 
            # We first create an empty list to store the entries that we have iterated over, and DO CONTAIN
            # the input value. We can then return a this "sbuStringEntries" as a list to the index page
            subStringEntries = []
            # Here, we iterate over each entry of our full list of entries
            for entry in util.list_entries():
                # We set the condition for input value being in each entry title (use .upper to control for capitalisation)
                if value.upper() in entry.upper():
                    # We add each entry with the relevant titles to our original list
                    subStringEntries.append(entry)
                
        return render(request, "encyclopedia/index.html", {
            "value" : value,
            "entries" : subStringEntries,
            "search" : True
        })

def newEntry(request):
    if request.method == "POST":
        # Go ahead and continue with rest of the function for creating a new entry
        # Next, we need to check if the entry that we are submitted already exists
        # We first capture the entry in the form of a form
        form = newEntryForm(request.POST)
        # We check if form is valid
        if form.is_valid():
            # Save each field from the form
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # Check if the current page exists OR that we are editting this page - if yes, then we save the page 
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return render(request, "encyclopedia/entry.html", {
                    "entryTitle": title,
                    "entry": content
                })
            else:
                return render(request, "encyclopedia/newEntry.html", {
                    "form": form,
                    "existing": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/newEntry.html", {
                "form": form,
                "existing": True,
                "entry": title
            })
    else:
        # Method is not "POST", therefore no new data is sent in to modify the existing database
        # We will render the same newEntry page
        return render(request, "encyclopedia/newEntry.html", {
            "form" : newEntryForm(),
            "existing" : False
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        form = newEntryForm()
        form.fields['title'].initial = entry
        form.fields['title'].widget = forms.HiddenInput()
        form.fields['content'].initial = entryPage
        form.fields['edit'].initial = True
        return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "edit": form.fields['edit'].initial,
            "entryTitle": form.fields["title"].initial
        })
