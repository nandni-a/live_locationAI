import gradio as gr
import requests

GOOGLE_API_KEY = "AIzaSyB4bn0LrJAoypY06cCmr8NIqAU-2FWCqv8"  # Replace this with your real key

def fetch_nearby_places(lat, lng, place_type):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 1500,
        "type": place_type,
        "key": GOOGLE_API_KEY
    }
    res = requests.get(url, params=params).json()
    places = res.get("results", [])

    output_blocks = []

    for place in places[:5]:  # limit to top 5 results
        name = place.get("name", "Unknown")
        rating = place.get("rating", "N/A")
        address = place.get("vicinity", "No address")
        open_now = place.get("opening_hours", {}).get("open_now", None)
        place_id = place.get("place_id")
        lat_dest = place["geometry"]["location"]["lat"]
        lng_dest = place["geometry"]["location"]["lng"]

        # Generate Google photo URL
        if "photos" in place:
            photo_ref = place["photos"][0]["photo_reference"]
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
        else:
            photo_url = None

        # Get review from place details
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "review",
            "key": GOOGLE_API_KEY
        }
        review_text = ""
        try:
            detail_res = requests.get(details_url, params=details_params).json()
            review_text = detail_res["result"]["reviews"][0]["text"]
            if len(review_text) > 200:
                review_text = review_text[:200] + "..."
        except:
            review_text = "No reviews available."

        link = f"http://127.0.0.1:5000/?lat={lat_dest}&lng={lng_dest}&name={name}"

        html = f"""
        <div style='border:1px solid #ccc;padding:10px;margin-bottom:10px;border-radius:10px'>
          <h4>📍 {name} ({rating}⭐️)</h4>
          <p><b>🗺️ Address:</b> {address}</p>
          {'<p><b>🟢 Open now</b></p>' if open_now else '<p><b>🔴 Closed</b></p>'}
          {f"<img src='{photo_url}' style='max-width:100%;height:auto;border-radius:10px;' />" if photo_url else ""}
          <p><b>📝 Review:</b> {review_text}</p>
          <a href="{link}" target="_blank">➡️ Navigate to this place</a>
        </div>
        """
        output_blocks.append(html)

    return "\n".join(output_blocks) if output_blocks else "No results found."

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🗺️ Find and Navigate to Nearby Places")

    with gr.Row():
        lat = gr.Textbox(label="Your Latitude")
        lng = gr.Textbox(label="Your Longitude")
        place_type = gr.Dropdown(choices=["cafe", "library", "restaurant", "pharmacy", "book_store"], value="cafe")

    search_btn = gr.Button("🔍 Find Nearby Places")
    result_html = gr.HTML()

    search_btn.click(fn=fetch_nearby_places, inputs=[lat, lng, place_type], outputs=result_html)

demo.launch()
