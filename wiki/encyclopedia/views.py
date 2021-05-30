from django.shortcuts import render
from django import forms
from . import util
from django.http import HttpResponseRedirect
import markdown2
from django.urls import reverse
from django.utils.safestring import mark_safe
import random

class addPageForm(forms.Form):
    pageTitle= forms.CharField(widget= forms.TextInput(attrs={"placeholder":"Add Title"}), min_length=1, label='')
    pageContent= forms.CharField(widget=forms.Textarea(attrs={"rows":18, "cols":20, "placeholder":"Add Content"}), min_length=1, label='')
class editPageForm(forms.Form):
    pageTitle= forms.CharField(widget= forms.TextInput(attrs={"readonly":"readonly"}), min_length=1, label='')
    pageContent= forms.CharField(widget=forms.Textarea(attrs={"rows":18, "cols":20, "placeholder":"Add Content"}), min_length=1, label='')

'''
    gets the homepage with all the entries
    - first checkes if method is get to know if user is trying to search
        -if so, then no exception will be thrown
    -if not searching, the user will be displayed all the entries
'''
def index(request):
    try:
        return search(request)
    except:
        return render(request, "encyclopedia/index.html", {
            "title":"All Pages",
            "entries": util.list_entries()
        })

'''
    checks if form is filled
        - if it is then parse it and save entry before redirecting to homepage
        - if entry already exists, give an error and display the same form (filled)
    if not filled
        - render a new form
'''
def createPage(request):
    if request.method=="POST":
        form=addPageForm(request.POST)
        if form.is_valid():
            pgTitle=form.cleaned_data["pageTitle"]
            if util.get_entry(pgTitle)==None:
                #success
                pgContent=form.cleaned_data["pageContent"]
                util.save_entry(pgTitle,pgContent)
                return HttpResponseRedirect(reverse(index))
            else:
                return render(request, "encyclopedia/newPage.html", {
            "errorPresent":True,
            "error": "Error: Same name page already exists.",
            "form": form
        })

    return render(request, "encyclopedia/newPage.html", {
            "form": addPageForm()
        })
'''
    similar to createPage. checks if form is filled, if so then parses and updates the entry
    if not, then give the user the form filled with the current content
'''
def editPage(request, entry1):
    if request.method=="POST":
        form=editPageForm(request.POST)
        if form.is_valid():
            pgTitle=form.cleaned_data["pageTitle"]
            #success
            pgContent=form.cleaned_data["pageContent"]
            util.save_entry(pgTitle,pgContent)
            return HttpResponseRedirect(reverse(content,args=[pgTitle]))
    markD=util.get_entry(entry1)
    form=editPageForm()
    form.fields["pageTitle"].initial=entry1
    form.fields["pageContent"].initial=markD
    return render(request, "encyclopedia/newPage.html", {
            "edit":True,
            "form": form,
            "entry":entry1
        })

'''
    checks if user sent a get request(wanted to search)
        - if so look for matching entries, and display a list of them
        - if a perfect match is found and no other entries starts with the query redirect user to the page
    if not get request
        -throw exception
    
'''
def search(request):
    if request.method =='GET':
        search=request.GET.get('q')
        entries=util.list_entries()
        searchRes=[]
        exactmatch=''
        for entry in entries:
            if search.lower()==entry.lower():
                exactmatch=entry
                searchRes.append(entry)
            elif entry.lower().startswith(search.lower()):
                searchRes.append(entry)
        if exactmatch!='' and searchRes==[]:
            return content(request,exactmatch)
        return render(request, "encyclopedia/index.html", {
            "title": "Search results for: \""+search+"\"" ,
            "entries": searchRes,
            "isEmpty": len(searchRes)==0
        })
    else:
        raise Exception("")
'''
    get random page and redirect user to that page
'''
def randPage(request):
    pagelist=util.list_entries()
    entry=random.choice(pagelist)
    return HttpResponseRedirect(reverse(content,args=[entry]))

'''
    Convert entry from markdown to html and render it
'''
def content(request, entry):
    try:
        return search(request)
    except:
        block=util.get_entry(entry)
        html=markdown2.markdown(block)
        return render(request,"encyclopedia/content.html",{
            "title":entry,
            "body":html,
        })

'''
        # my implementation of adding a link (inefficient) => use regexes
        block=f.read().splitlines()
        pageHead=block[0]
        pageHead=pageHead.replace("# ","")
        block=block[1:]
        # Find markdowns and replace with the coresponding html
        for i in range(len(block)):
            b=block[i]
            # adding links
            start=b.find('[')
            if start!=-1 and b.find('\[')==-1:
                end=b.find(']')
                linkend=b.find(')',end)
                link=b[end+2:linkend]
                linktext=b[start+1:end]
                alt="<a href=\""+link+"\">"+linktext+"</a>"
                b=b.replace("["+linktext+"]"+"("+link+")",alt)
            block[i]=b
'''