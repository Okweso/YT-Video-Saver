from django.shortcuts import render
from django.views.generic import View
from pytube import YouTube
from pytube.exceptions import PytubeError
from django.http import StreamingHttpResponse, HttpResponse
import requests

def stream_to_response(video_stream):
    # Get the URL of the video file
    video_url = video_stream.url
    
    # Request the video file with streaming enabled
    response = requests.get(video_url, stream=True)
    
    # Stream the video in chunks to the client
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            yield chunk

class home(View):
    def __init__(self, url=None):
        self.url = url

    def get(self, request):
        return render(request, 'myApp/home.html')

    def post(self, request):
        if request.POST.get('fetch-vid'):
            try:
                self.url = request.POST.get('given_url')
                video = YouTube(self.url)
                vidTitle = video.title
                vidThumbnail = video.thumbnail_url
                qual = []
                stream = []
                filesize = 0

                for vid in video.streams.filter(progressive=True):
                    qual.append(vid.resolution)
                    stream.append(vid)
                    filesize = "Size: " + str(round(vid.filesize/(1024 * 1024), 2)) + "MBs"

                context = {
                    'vidTitle': vidTitle,
                    'vidThumbnail': vidThumbnail,
                    'qual': qual,
                    'stream': stream,
                    'url': self.url,
                    'filesize': filesize
                }
                return render(request, 'myApp/home.html', context)
            except PytubeError as e:
                print(f"PytubeError: {e}")
                return HttpResponse("Please enter a valid YouTube URL or check your internet connection and try again.", status=400)
            except Exception as e:
                print(f"Unexpected error: {e}")
                return HttpResponse("An unexpected error occurred.", status=500)

        elif request.POST.get('download-vid'):
            try:
                self.url = request.POST.get('given_url')
                video = YouTube(self.url)
                video_stream = video.streams.filter(progressive=True, file_extension='mp4').first()

                response = StreamingHttpResponse(stream_to_response(video_stream), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{video.title}.mp4"'
                return response

            except PytubeError as e:
                print(f"PytubeError: {e}")
                return HttpResponse("Error downloading video: PytubeError occurred.", status=500)
            except Exception as e:
                print(f"Unexpected error: {e}")
                return HttpResponse("An unexpected error occurred during download.", status=500)

        return render(request, 'myApp/home.html')
