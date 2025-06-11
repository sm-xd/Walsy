import os
import io
import instaloader
import logging
import requests
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

def extract_shortcode(instagram_url: str):
    try:
        path = urlparse(instagram_url).path
        parts = path.strip("/").split("/")
        if "p" in parts:
            return parts[parts.index("p") + 1]
        elif "reel" in parts or "tv" in parts:
            return parts[1]
    except Exception:
        return None

async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    shortcode = extract_shortcode(url)
    if not shortcode:
        await update.message.reply_text("Invalid Instagram URL.")
        return

    loader = instaloader.Instaloader(
        save_metadata=False,
        download_comments=False,
        compress_json=False,
        dirname_pattern=".",  # Won’t be used
        download_video_thumbnails=False,
    )

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        images = []

        if post.typename == "GraphImage":
            images.append(post.url)
        elif post.typename == "GraphSidecar":
            images = [node.display_url for node in post.get_sidecar_nodes()]
        else:
            await update.message.reply_text("This post doesn't contain images.")
            return

        await update.message.reply_text("Sending wallpapers 📸...")
        for img_url in images:
            img_data = requests.get(img_url).content
            await update.message.reply_photo(photo=io.BytesIO(img_data))

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Failed to download the post. Try with a public post URL.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any public Instagram post/reel/tv URL to get the wallpapers!")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))
    app.run_polling()

if __name__ == "__main__":
    main()
