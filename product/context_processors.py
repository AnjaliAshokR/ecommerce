from .models import Category, Brand


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def menu_links_brand(request):
    link = Brand.objects.all()
    return dict(link=link)
