import instaloader
from urllib.parse import urlparse
import os

def extract_shortcode(instagram_url):
    try:
        path = urlparse(instagram_url).path
        parts = path.strip("/").split("/")
        if "p" in parts:
            return parts[parts.index("p") + 1]
        elif "reel" in parts or "tv" in parts:
            return parts[1]
    except:
        return None

def download_images_from_post(url):
    shortcode = extract_shortcode(url)
    if not shortcode:
        print("Invalid URL")
        return

    os.makedirs("images", exist_ok=True)

    loader = instaloader.Instaloader(
        save_metadata=False,
        download_comments=False,
        compress_json=False,
        dirname_pattern="images"
    )

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.typename == "GraphImage":
            loader.download_pic(f"images/{shortcode}_image.jpg", post.url, post.date_utc)
        elif post.typename == "GraphSidecar":
            for i, res in enumerate(post.get_sidecar_nodes()):
                loader.download_pic(f"images/{shortcode}_image_{i+1}", res.display_url, post.date_utc)
        else:
            print("Not an image or carousel.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    instagram_url = "https://www.instagram.com/p/DKVPhQWIzVi/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=="
    download_images_from_post(instagram_url)
