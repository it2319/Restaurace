from django.shortcuts import render, get_object_or_404
from django.conf import settings
import os

from .models import Restaurace, Oteviraci_doba


def home(request):
	return render(request, "index.html")

def restaurant_list(request):
    # prepare list of image files in media/restaurace (sorted)
    images_dir = os.path.join(settings.MEDIA_ROOT, 'restaurace')
    image_files = sorted(
        fn for fn in os.listdir(images_dir)
        if fn.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ) if os.path.isdir(images_dir) else []

    restaurants = list(Restaurace.objects.order_by('id'))
    restaurants_context = []
    for idx, r in enumerate(restaurants):
        if getattr(r, 'image', None):
            url = r.image.url
        elif idx < len(image_files):
            url = settings.MEDIA_URL + f"restaurace/{image_files[idx]}"
        else:
            url = None
        restaurants_context.append({
            'id': r.pk,
            'name': r.nazev,
            'image_url': url,
        })
    return render(request, 'restaurants/restaurace_seznam.html', {'restaurants': restaurants_context})

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurace, pk=pk)
    opening_hours = Oteviraci_doba.objects.filter(Restaurace=restaurant).order_by('den')
    # compute fallback image by restaurant position if model image missing
    image_url = None
    if getattr(restaurant, 'image', None):
        image_url = restaurant.image.url
    else:
        images_dir = os.path.join(settings.MEDIA_ROOT, 'restaurace')
        image_files = sorted(
            fn for fn in os.listdir(images_dir)
            if fn.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ) if os.path.isdir(images_dir) else []
        # find index of this restaurant in ordered list
        ordered = list(Restaurace.objects.order_by('id'))
        try:
            idx = next(i for i, r in enumerate(ordered) if r.pk == restaurant.pk)
            if idx < len(image_files):
                image_url = settings.MEDIA_URL + f"restaurace/{image_files[idx]}"
        except StopIteration:
            image_url = None

    context = {
        'restaurant': restaurant,
        'opening_hours': opening_hours,
        'image_url': image_url,
    }
    return render(request, 'restaurants/restaurace_detail.html', context=context)