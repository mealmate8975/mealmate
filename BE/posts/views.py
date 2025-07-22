from django.shortcuts import render
from rest_framework.views import APIView, generics

from .serializers import PostSerializer
from .models import Post

def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/feed.html',{'posts':posts})

class PostListAPI(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer