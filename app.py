import pickle
import streamlit as st
import requests
import os

st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎥", layout="wide")

st.markdown("""
    <style>
        /* خلفية Netflix-style */
        .stApp {
            background-color: #0e0e0e;
            color: #f5f5f5;
            font-family: 'Segoe UI', sans-serif;
        }
        /* العنوان */
        .main-title {
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            color: #E50914;
            margin-bottom: 10px;
        }
        .subtext {
            text-align: center;
            font-size: 1.1rem;
            color: #bbbbbb;
            margin-bottom: 40px;
        }
        /* الكروت */
        .movie-card {
            background-color: #1a1a1a;
            border-radius: 15px;
            padding: 10px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }
        .movie-card:hover {
            transform: scale(1.05);
            background-color: #2a2a2a;
        }
        .movie-title {
            margin-top: 10px;
            font-weight: bold;
            font-size: 1rem;
            color: #ffffff;
        }
        .movie-info {
            font-size: 0.9rem;
            color: #cccccc;
            margin-top: 4px;
        }
        /* الأزرار */
        .stButton>button {
            background-color: #E50914;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            transition: background-color 0.3s ease;
            display: block;
            margin: 20px auto;
        }
        .stButton>button:hover {
            background-color: #b0070f;
        }
        /* شريط التقدم */
        div[data-testid="stProgress"] > div > div {
            background-color: #E50914;
        }
    </style>
""", unsafe_allow_html=True)


def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return ("https://via.placeholder.com/500x750?text=No+Image", "Unknown", "N/A")

        data = response.json()
        poster_path = data.get('poster_path')
        genres = ", ".join([g['name'] for g in data.get('genres', [])]) or "Unknown"
        rating = round(data.get('vote_average', 0), 1)

        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
        return poster_url, genres, rating
    except:
        return ("https://via.placeholder.com/500x750?text=Error", "Unknown", "N/A")


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_genres = []
    recommended_movie_ratings = []

    progress = st.progress(0)
    total = min(100, len(distances[1:]))

    for idx, i in enumerate(distances[1:total]):
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, genres, rating = fetch_movie_details(movie_id)

        recommended_movie_names.append(title)
        recommended_movie_posters.append(poster)
        recommended_movie_genres.append(genres)
        recommended_movie_ratings.append(rating)
        progress.progress((idx + 1) / total)

    progress.empty()
    return recommended_movie_names, recommended_movie_posters, recommended_movie_genres, recommended_movie_ratings


movies = pickle.load(open(os.path.join('model', 'movie_list.pkl'), 'rb'))
similarity = pickle.load(open(os.path.join('model', 'similarity.pkl'), 'rb'))
movie_list = movies['title'].values

st.markdown("<h1 class='main-title'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Discover movies similar to your favorites!</p>", unsafe_allow_html=True)

selected_movie = st.selectbox("🎞️ Choose a movie", movie_list)

if "recommended_movie_names" not in st.session_state:
    st.session_state.recommended_movie_names = []
if "recommended_movie_posters" not in st.session_state:
    st.session_state.recommended_movie_posters = []
if "recommended_movie_genres" not in st.session_state:
    st.session_state.recommended_movie_genres = []
if "recommended_movie_ratings" not in st.session_state:
    st.session_state.recommended_movie_ratings = []
if "num_movies" not in st.session_state:
    st.session_state.num_movies = 20
if "last_movie" not in st.session_state:
    st.session_state.last_movie = None

if st.button("Show Recommendations"):
    if st.session_state.last_movie != selected_movie:
        st.session_state.last_movie = selected_movie
        st.session_state.num_movies = 20
        (
            st.session_state.recommended_movie_names,
            st.session_state.recommended_movie_posters,
            st.session_state.recommended_movie_genres,
            st.session_state.recommended_movie_ratings
        ) = recommend(selected_movie)

if st.session_state.recommended_movie_names:
    num_to_show = min(st.session_state.num_movies, len(st.session_state.recommended_movie_names))
    total = len(st.session_state.recommended_movie_names)
    st.markdown(f"<h4 style='text-align:center;color:#bbb;'>Showing {num_to_show} of {total} recommended movies</h4>", unsafe_allow_html=True)

    cols = st.columns(5)
    for i in range(num_to_show):
        with cols[i % 5]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{st.session_state.recommended_movie_posters[i]}" width="100%" style="border-radius:10px;">
                    <p class="movie-title">{st.session_state.recommended_movie_names[i]}</p>
                    <p class="movie-info">⭐ {st.session_state.recommended_movie_ratings[i]} | 🎭 {st.session_state.recommended_movie_genres[i]}</p>
                </div>
            """, unsafe_allow_html=True)

    if num_to_show < total:
        st.markdown("<div style='text-align:center; margin-top:30px;'>", unsafe_allow_html=True)
        if st.button("🎥 See More Films"):
            st.session_state.num_movies += 20
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
