import pickle
import streamlit as st
import requests
import os

# ====== دالة لجلب صورة الفيلم ======
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ====== دالة التوصيات ======
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:]:  # نأخذ كل النتائج
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


# ====== واجهة Streamlit ======
st.header('🎬 Movie Recommender System')

# تحميل البيانات
movies = pickle.load(open(os.path.join('model', 'movie_list.pkl'), 'rb'))
similarity = pickle.load(open(os.path.join('model', 'similarity.pkl'), 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# ====== Session State ======
if "recommended_movie_names" not in st.session_state:
    st.session_state.recommended_movie_names = []
if "recommended_movie_posters" not in st.session_state:
    st.session_state.recommended_movie_posters = []
if "num_movies" not in st.session_state:
    st.session_state.num_movies = 20
if "last_movie" not in st.session_state:
    st.session_state.last_movie = None

# ====== زر التوصيات ======
if st.button('Show Recommendation'):
    # لو المستخدم اختار فيلم جديد → نعيد التعيين
    if st.session_state.last_movie != selected_movie:
        st.session_state.last_movie = selected_movie
        st.session_state.num_movies = 20
        st.session_state.recommended_movie_names, st.session_state.recommended_movie_posters = recommend(selected_movie)

# ====== عرض النتائج ======
if st.session_state.recommended_movie_names:
    num_to_show = min(st.session_state.num_movies, len(st.session_state.recommended_movie_names))
    total = len(st.session_state.recommended_movie_names)

    st.subheader(f"Showing {num_to_show} of {total} recommended movies")

    cols = st.columns(5)
    for i in range(num_to_show):
        with cols[i % 5]:
            st.text(st.session_state.recommended_movie_names[i])
            st.image(st.session_state.recommended_movie_posters[i])

    # زر عرض المزيد
    if num_to_show < total:
        if st.button("عرض المزيد 🎞️"):
            st.session_state.num_movies += 20
            st.experimental_rerun()
