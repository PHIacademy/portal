import os
import requests
from urllib.parse import urlparse
from base64 import b64encode

def upload_to_blob(content, filename):
    """Upload content to Vercel Blob Storage"""
    try:
        token = os.getenv("BLOB_READ_WRITE_TOKEN")
        
        # Vercel Blob API endpoint
        url = "https://blob.vercel-storage.com"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "pathname": filename,
            "data": b64encode(content.encode('utf-8')).decode('utf-8'),
            "contentType": "text/html",
            "token": token
        }
        
        response = requests.put(
            f"{url}/{filename}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        # Return the public blob URL from the response
        return response.json().get("url")
        
    except Exception as e:
        raise Exception(f"Failed to upload to blob storage: {str(e)}")

def delete_from_blob(url):
    """Delete content from Vercel Blob Storage"""
    try:
        token = os.getenv("BLOB_READ_WRITE_TOKEN")
        parsed = urlparse(url)
        store_id = parsed.netloc.split('.')[0]  # Extract g4oa4bgcar3bwcyq from the hostname
        filename = os.path.basename(parsed.path)
        
        # Use the store ID in the deletion request
        headers = {
            "Authorization": f"Bearer {token}",
            "x-store-id": store_id
        }
        
        # Use the stored URL's hostname for deletion
        delete_url = f"https://{parsed.netloc}/{filename}"
        response = requests.delete(
            delete_url,
            headers=headers
        )
        response.raise_for_status()
        
    except Exception as e:
        raise Exception(f"Failed to delete from blob storage: {str(e)}")
