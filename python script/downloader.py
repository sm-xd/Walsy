import instaloader
from urllib.parse import urlparse
import sys

def extract_shortcode(instagram_url):
    try:
        path = urlparse(instagram_url).path
        parts = path.strip("/").split("/")
        if "p" in parts:
            return parts[parts.index("p") + 1]
        elif "reel" in parts or "tv" in parts:
            return parts[1]  # for reels or tv
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return None

def download_images_from_post(url):
    shortcode = extract_shortcode(url)
    if not shortcode:
        print("Invalid Instagram post URL.")
        return

    loader = instaloader.Instaloader(
        save_metadata=False,
        download_comments=False,
        compress_json=False
    )

    try:
        print(f"Fetching post: {shortcode}")
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.typename == "GraphImage":
            # Single image post
            loader.download_pic(f"{shortcode}_image.jpg", post.url, post.date_utc)
        elif post.typename == "GraphSidecar":
            # Carousel post
            for i, res in enumerate(post.get_sidecar_nodes()):
                loader.download_pic(f"{shortcode}_image_{i+1}.jpg", res.display_url, post.date_utc)
        else:
            print("Post is not an image or carousel.")
    except Exception as e:
        print(f"Failed to download: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python insta_wallpaper_downloader.py <instagram_post_url>")
    else:
        download_images_from_post(sys.argv[1])
