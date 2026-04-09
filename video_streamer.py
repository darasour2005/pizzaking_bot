# video_streamer.py - MEDIA ENGINE V3.0
import logging
from aiohttp import web
from pyrogram import Client
import config

# The MTProto Client acting as a "User" bridge
stream_client = Client(
    "pizz_king_streamer",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.TELEGRAM_API_TOKEN,
    in_memory=True # Leverages the .session file you uploaded
)

async def stream_movie_endpoint(request):
    """
    Pipes Telegram video chunks directly to the browser.
    Zero-Omission Protocol: Supports partial content and seeking.
    """
    try:
        msg_id = int(request.match_info.get('message_id'))
        
        # Fetch metadata from the private channel
        msg = await stream_client.get_messages(config.MOVIE_CHANNEL_ID, msg_id)
        if not msg or not msg.video:
            logging.error(f"Media Fetch Failed: ID {msg_id} not found in channel.")
            return web.Response(text="Video not found", status=404)

        file_size = msg.video.file_size
        range_header = request.headers.get("Range")
        
        # 1. Logic Gate: Determine start byte for buffering/seeking
        start = 0
        if range_header:
            start = int(range_header.replace("bytes=", "").split("-")[0])

        # 2. Generator Logic: Stream chunks to prevent RAM overflow
        async def file_sender():
            async for chunk in stream_client.download_media(msg, offset=start, block=False):
                yield chunk

        # 3. Response Headers: Standard Streaming Protocol
        headers = {
            "Content-Type": msg.video.mime_type or "video/mp4",
            "Content-Range": f"bytes {start}-{file_size-1}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size - start),
            "Access-Control-Allow-Origin": "*"
        }
        
        # Return 206 for partial content (seeking) or 200 for full start
        return web.Response(body=file_sender(), status=206 if range_header else 200, headers=headers)

    except Exception as e:
        logging.error(f"Stream Engine Failure: {e}")
        return web.Response(text="Internal Streaming Error", status=500)
