from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import requests
import json
from .forms import SignupForm
import pandas as pd
import pickle

movies = pd.DataFrame(pickle.load(open('movies_dict.pkl','rb')))
similarity = pickle.load(open('similarity.pkl','rb'))

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
        
    context = { 'form': form }
    return render(request, 'signup.html', context)


def getMovies(request):
    return JsonResponse({'movies': movies['title'].values.tolist()})

def recommend(request, movie_name):
    if request.method == 'GET':
        movie_index = movies[movies['title'] == str(movie_name)].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].id

            recommended_movies.append(movies.iloc[i[0]].title)

            # fetch poster from API
            recommended_movies_posters.append(fetch_poster(movie_id))
        return JsonResponse({'movies': recommended_movies, 'posters': recommended_movies_posters})

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=75caf8ac9c2238657c106482f493d73b&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path