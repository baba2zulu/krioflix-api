from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fzmovies_api import Search, Navigate, DownloadLinks
from fzmovies_api.filters import RecentlyReleasedFilter, IMDBTop250Filter
import uvicorn

app = FastAPI(title="KrioFlix Bridge API")

# Enable CORS for Lovable/Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/trending")
async def get_trending():
    """Fetches trending movies using the IMDB Top 250 filter."""
    try:
        search = Search(query=IMDBTop250Filter())
        return {"results": search.all_results.movies[:20]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_movies(q: str):
    """Searches for movies by title."""
    try:
        search = Search(query=q)
        return {"results": search.all_results.movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resolve")
async def resolve_movie(movie_id: str):
    """
    Resolves a specific movie ID into a direct stream/download link.
    Architecture based on fzmovies navigation logic.
    """
    try:
        # 1. Reconstruct the movie object from ID (Mocking object for Navigate)
        # In a real scenario, you'd pass the movie object from the search result
        search = Search(query=movie_id)
        target_movie = search.all_results.movies
        
        # 2. Navigate to the file selection page
        movie_page = Navigate(target_movie).results
        
        # 3. Get quality options (480p is usually index 0, 720p index 1)
        # Defaulting to 480p for Salone Low-Data optimization
        file_option = movie_page.files 
        
        # 4. Extract final metadata and links
        link_data = DownloadLinks(file_option).results
        
        return {
            "title": target_movie.title,
            "stream_url": link_data.links,
            "size": link_data.size,
            "quality": "480p",
            "source": "fzmovies.cms"
        }
    except Exception as e:
        # Fallback to VidSrc Embed if fzmovies fails
        return {
            "fallback_embed": f"https://vidsrc.to/embed/movie/{movie_id}",
            "source": "vidsrc.to (Fallback)"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
