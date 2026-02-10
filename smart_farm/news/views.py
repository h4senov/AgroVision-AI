from django.shortcuts import render, get_object_or_404
from .models import News
from django.contrib.auth.decorators import login_required, user_passes_test

def is_staff_check(user):
    return user.is_staff


def news_list(request):
    news_items = News.objects.filter(is_published=True)
    return render(request, "news/news_list.html", {"news_items": news_items})


def news_detail(request, slug):
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    return render(request, "news/news_detail.html", {"news": news_item})


from django.shortcuts import render, redirect
from .forms import NewsForm

@login_required
@user_passes_test(is_staff_check)
def news_delete(request, slug):
    news_item = get_object_or_404(News, slug=slug)

    if request.method == "POST":
        news_item.delete()
        return redirect("news:news_list")

    return render(request, "news/news_confirm_delete.html", {
        "news": news_item
    })


@login_required
@user_passes_test(is_staff_check)
def news_update(request, slug):
    news_item = get_object_or_404(News, slug=slug)

    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect("news:news_detail", slug=news_item.slug)
    else:
        form = NewsForm(instance=news_item)

    return render(request, "news/news_form.html", {
        "form": form,
        "title": "Xəbəri redaktə et"
    })



from django.contrib.auth.decorators import login_required, user_passes_test
@login_required
@user_passes_test(is_staff_check)
def news_create(request):
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("news:news_list")
    else:
        form = NewsForm()

    return render(request, "news/news_form.html", {
        "form": form,
        "title": "Xəbər yarat"
    })
