import gradio as gr
import requests
import folium
import polyline
from folium.plugins import MarkerCluster

GOOGLE_API_KEY = "AIzaSyBOrTlQezmexIXDVpBpDRkghijcVlUKiUg"

def locate_and_route(lat, lng, keyword, destination, radius):
    m = folium.Map(location=[lat, lng], zoom_start=16)
    folium.Marker([lat, lng], popup="You", icon=folium.Icon(color="red")).add_to(m)

    # Nearby search
    places = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params={
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword,
            "key": GOOGLE_API_KEY
        }).json()

    cluster = MarkerCluster().add_to(m)
    for place in places.get("results", []):
        p_loc = place["geometry"]["location"]
        folium.Marker(
            [p_loc["lat"], p_loc["lng"]],
            popup=place.get("name", "Place"),
            icon=folium.Icon(color="blue")
        ).add_to(cluster)

    # Directions
    if destination:
        direction = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params={
                "origin": f"{lat},{lng}",
                "destination": destination,
                "mode": "walking",
                "key": GOOGLE_API_KEY
            }).json()

        if direction.get("routes"):
            points = polyline.decode(direction["routes"][0]["overview_polyline"]["points"])
            folium.PolyLine(points, color="green", weight=5).add_to(m)

    return m._repr_html_()

gradio_app = gr.Interface(
    fn=locate_and_route,
    inputs=[
        gr.Number(label="Latitude"),
        gr.Number(label="Longitude"),
        gr.Dropdown(["ATM", "Restaurant", "Hotel", "Hospital", "Pharmacy", "Cafe"], label="Place Type"),
        gr.Textbox(label="Destination"),
        gr.Slider(minimum=100, maximum=5000, value=1000, step=100, label="Search Radius (meters)")
    ],
    outputs=gr.HTML()
)
