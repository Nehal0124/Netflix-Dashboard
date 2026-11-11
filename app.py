import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Netflix Data Analytics Dashboard",
    page_icon="🎬",
    layout="wide"
)

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
    .stApp { background-color: #101010; }
    h1, h2, h3 { color: #E50914 !important; }
    [data-testid="stMetric"] {
        background: #1c1c1c;
        border: 1px solid #333333;
        padding: 16px;
        border-radius: 12px;
    }
    [data-testid="stSidebar"] { background-color: #181818; }
    div[data-testid="stAlert"] { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
DATA_PATH = Path(__file__).parent / "data" / "data" / "data" / "netflix_titles.csv"

@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        data.columns = data.columns.str.strip().str.lower()
        return data
    except Exception as e:
        st.error(f"Could not load dataset: {e}")
        st.stop()

    required = {
        "show_id", "type", "title", "director", "cast", "country",
        "date_added", "release_year", "rating", "duration",
        "listed_in", "description"
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(sorted(missing)))

    data["date_added"] = pd.to_datetime(
        data["date_added"].astype("string").str.strip(),
        errors="coerce"
    )
    data["year_added"] = data["date_added"].dt.year
    data["release_year"] = pd.to_numeric(data["release_year"], errors="coerce")
    data["type"] = data["type"].astype("string").str.strip()
    data["country"] = data["country"].astype("string")
    data["rating"] = data["rating"].astype("string")
    data["listed_in"] = data["listed_in"].astype("string")
    return data

st.title("🎬 Netflix Data Analytics Dashboard")
st.caption("Explore Netflix movies, TV shows, genres, ratings and global content trends.")
st.divider()

if not DATA_PATH.exists():
    st.error("Dataset file not found.")
    st.markdown(
        "Please place **netflix_titles.csv** inside the project's **data** folder. "
        "The expected location is `Netflix_Dashboard_Project/data/netflix_titles.csv`."
    )
    st.info("The CSV should be the Netflix titles dataset with columns such as title, type, country, release_year, rating and listed_in.")
    st.stop()

try:
    df = load_data(DATA_PATH)
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🎛️ Dashboard Filters")
st.sidebar.caption("Choose filters to update all charts.")

types = sorted(df["type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect("Content type", types, default=types)

all_ratings = sorted(df["rating"].dropna().unique().tolist())
selected_ratings = st.sidebar.multiselect("Rating", all_ratings)

valid_years = df["release_year"].dropna()
if valid_years.empty:
    st.error("No valid release-year values found in the dataset.")
    st.stop()

min_year = int(valid_years.min())
max_year = int(valid_years.max())
default_start = max(min_year, 2000)
selected_years = st.sidebar.slider(
    "Release year range",
    min_value=min_year,
    max_value=max_year,
    value=(default_start, max_year)
)

country_options = sorted({
    country.strip()
    for value in df["country"].dropna()
    for country in str(value).split(",")
    if country.strip()
})
selected_countries = st.sidebar.multiselect("Country", country_options)

# ---------------- FILTER DATA ----------------
filtered = df[df["type"].isin(selected_types)].copy()
filtered = filtered[
    filtered["release_year"].between(selected_years[0], selected_years[1])
]

if selected_ratings:
    filtered = filtered[filtered["rating"].isin(selected_ratings)]

if selected_countries:
    country_pattern = "|".join(
        [__import__("re").escape(c) for c in selected_countries]
    )
    filtered = filtered[
        filtered["country"].fillna("").str.contains(country_pattern, regex=True)
    ]

if filtered.empty:
    st.warning("No titles match the selected filters. Try changing or clearing your filters.")
    st.stop()

# ---------------- KPI METRICS ----------------
st.subheader("📊 Key Metrics")
movie_count = int((filtered["type"] == "Movie").sum())
show_count = int((filtered["type"] == "TV Show").sum())
unique_countries = {
    c.strip()
    for value in filtered["country"].dropna()
    for c in str(value).split(",")
    if c.strip()
}

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total titles", f"{len(filtered):,}")
k2.metric("Movies", f"{movie_count:,}")
k3.metric("TV Shows", f"{show_count:,}")
k4.metric("Countries", f"{len(unique_countries):,}")

st.divider()

# ---------------- CONTENT TYPE + RELEASE YEAR ----------------
left, right = st.columns(2)

with left:
    st.subheader("Movies vs TV Shows")
    type_counts = filtered["type"].value_counts().rename_axis("Content type").reset_index(name="Titles")
    fig = px.pie(
        type_counts, names="Content type", values="Titles", hole=0.48,
        color_discrete_sequence=["#E50914", "#777777"]
    )
    fig.update_layout(template="plotly_dark", margin=dict(t=25, b=15, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Titles by Release Year")
    release_counts = (
        filtered.dropna(subset=["release_year"])
        .groupby("release_year").size().reset_index(name="Titles")
        .sort_values("release_year")
    )
    fig = px.line(
        release_counts, x="release_year", y="Titles", markers=True,
        labels={"release_year": "Release year", "Titles": "Number of titles"}
    )
    fig.update_traces(line_color="#E50914", marker_color="#E50914")
    fig.update_layout(template="plotly_dark", margin=dict(t=25, b=15, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- YEAR ADDED ----------------
st.subheader("📅 Netflix Titles Added by Year")
added_counts = (
    filtered.dropna(subset=["year_added"])
    .groupby("year_added").size().reset_index(name="Titles")
    .sort_values("year_added")
)
if not added_counts.empty:
    fig = px.bar(
        added_counts, x="year_added", y="Titles",
        labels={"year_added": "Year added to Netflix", "Titles": "Number of titles"},
        color="Titles", color_continuous_scale=["#5b0000", "#E50914"]
    )
    fig.update_layout(template="plotly_dark", margin=dict(t=25, b=15, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No valid date-added information is available for the selected titles.")

st.divider()

# ---------------- COUNTRY CHART ----------------
left, right = st.columns(2)

with left:
    st.subheader("🌍 Top 10 Content-Producing Countries")
    country_series = (
        filtered["country"].dropna().str.split(",").explode().str.strip()
    )
    country_counts = country_series[country_series.ne("")].value_counts().head(10)
    if not country_counts.empty:
        country_chart = country_counts.rename_axis("Country").reset_index(name="Titles")
        fig = px.bar(
            country_chart, x="Titles", y="Country", orientation="h",
            color="Titles", color_continuous_scale=["#5b0000", "#E50914"]
        )
        fig.update_layout(
            template="plotly_dark",
            yaxis={"categoryorder": "total ascending"},
            margin=dict(t=25, b=15, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Country information is not available.")

with right:
    st.subheader("⭐ Content Rating Distribution")
    rating_counts = filtered["rating"].fillna("Not specified").value_counts()
    rating_chart = rating_counts.rename_axis("Rating").reset_index(name="Titles")
    fig = px.bar(
        rating_chart, x="Rating", y="Titles",
        color="Titles", color_continuous_scale=["#5b0000", "#E50914"]
    )
    fig.update_layout(template="plotly_dark", margin=dict(t=25, b=15, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- GENRES ----------------
st.subheader("🎭 Top 10 Genres")
genre_series = (
    filtered["listed_in"].dropna().str.split(",").explode().str.strip()
)
genre_counts = genre_series[genre_series.ne("")].value_counts().head(10)
if not genre_counts.empty:
    genre_chart = genre_counts.rename_axis("Genre").reset_index(name="Titles")
    fig = px.bar(
        genre_chart, x="Genre", y="Titles",
        color="Titles", color_continuous_scale=["#5b0000", "#E50914"]
    )
    fig.update_layout(template="plotly_dark", margin=dict(t=25, b=15, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Genre information is not available.")

st.divider()

# ---------------- WORLD MAP ----------------
st.subheader("🗺️ Global Distribution of Netflix Content")
map_counts = (
    filtered["country"].dropna().str.split(",").explode().str.strip()
)
map_counts = map_counts[map_counts.ne("")].value_counts().reset_index()
map_counts.columns = ["country", "titles"]

if not map_counts.empty:
    fig = px.choropleth(
        map_counts,
        locations="country",
        locationmode="country names",
        color="titles",
        hover_name="country",
        color_continuous_scale="Reds",
        labels={"titles": "Number of titles"},
    )
    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=25, b=15, l=0, r=0),
        geo=dict(showframe=False, showcoastlines=True, bgcolor="#101010")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Country information is not available for the map.")

st.divider()

# ---------------- SEARCH + DATA PREVIEW ----------------
st.subheader("🔎 Search Netflix Titles")
search_text = st.text_input("Search by movie or TV show title", placeholder="e.g. Stranger Things")

search_results = filtered.copy()
if search_text.strip():
    search_results = search_results[
        search_results["title"].fillna("").str.contains(
            search_text.strip(), case=False, na=False
        )
    ]

st.caption(f"{len(search_results):,} matching records")
display_columns = [
    col for col in [
        "show_id", "type", "title", "director", "cast", "country",
        "date_added", "release_year", "rating", "duration",
        "listed_in", "description"
    ] if col in search_results.columns
]
st.dataframe(
    search_results[display_columns],
    use_container_width=True,
    hide_index=True
)

st.caption("Project: Netflix Data Analytics Dashboard | Built with Python, Pandas, Streamlit and Plotly")
