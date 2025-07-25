from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView


# from .serializers import PageSerializer
from .models import Page
from posts.models import Post

def page_detail(request,page_id):
    page = get_object_or_404(Page,id=page_id)
    posts = Post.objects.filter(page=page)
    ordered_posts = posts.order_by('-created_at')
    return render(request, 'pages/detail.html',{'page':page,'posts':ordered_posts})

# class ?(generics.ListAPIView):
#     ?