import requests
import re
from bs4 import BeautifulSoup
import json

class BooruToString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": False}),
                "blacklist": ("STRING", {"default": "artist log, artist name, signature", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "booru_to_string"
    CATEGORY = "utils"
    
    def booru_to_string(self, url, blacklist):
        # Skip if no URL provided
        if not url or url.strip() == "":
            return ("",)
        
        # Parse blacklist
        blacklist_terms = []
        if blacklist:
            blacklist_terms = [term.strip().lower() for term in blacklist.split(",")]
        
        try:
            # Determine booru type and extract post ID
            post_id = self.extract_post_id(url)
            if not post_id:
                raise ValueError("Could not extract post ID from URL")
            
            # Get tags based on booru type
            if "gelbooru" in url.lower():
                tags = self.get_gelbooru_tags(post_id)
            elif "danbooru" in url.lower():
                tags = self.get_danbooru_tags(post_id)
            else:
                raise ValueError("Unsupported booru site. Only Gelbooru and Danbooru are supported.")
            
            # Filter tags (only general tags, no artist/copyright/character/metadata)
            filtered_tags = self.filter_tags(tags, blacklist_terms)
            
            # Format tags: replace underscores with spaces and escape parentheses
            formatted_tags = []
            for tag in filtered_tags:
                # Replace underscores with spaces
                formatted_tag = tag.replace("_", " ")
                # Escape parentheses
                formatted_tag = formatted_tag.replace("(", "\\(").replace(")", "\\)")
                formatted_tags.append(formatted_tag)
            
            # Join with commas and spaces
            result = ", ".join(formatted_tags)
            return (result,)
            
        except Exception as e:
            # Interrupt on any error
            raise RuntimeError(f"Booru To String error: {str(e)}")
    
    def extract_post_id(self, url):
        """Extract post ID from booru URL"""
        # Match patterns like /post/show/12345 or ?id=12345
        patterns = [
            r'/post/show/(\d+)',
            r'[?&]id=(\d+)',
            r'/posts/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_gelbooru_tags(self, post_id):
        """Get tags from Gelbooru API"""
        api_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id={post_id}"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data or 'post' not in data or not data['post']:
            raise ValueError("Post not found on Gelbooru")
        
        post = data['post'][0]
        tags = post.get('tags', '').split()
        return tags
    
    def get_danbooru_tags(self, post_id):
        """Get tags from Danbooru API"""
        api_url = f"https://danbooru.donmai.us/posts/{post_id}.json"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise ValueError("Post not found on Danbooru")
        
        # Get only general tags (category 0)
        tags = []
        tag_string = data.get('tag_string_general', '')
        if tag_string:
            tags.extend(tag_string.split())
        
        return tags
    
    def filter_tags(self, tags, blacklist_terms):
        """Filter out blacklisted tags"""
        filtered_tags = []
        
        for tag in tags:
            tag_lower = tag.lower()
            
            # Check if tag contains any blacklisted terms
            is_blacklisted = False
            for blacklist_term in blacklist_terms:
                if blacklist_term in tag_lower:
                    is_blacklisted = True
                    break
            
            if not is_blacklisted:
                filtered_tags.append(tag)
        
        return filtered_tags

# These mappings will be imported by __init__.py
NODE_CLASS_MAPPINGS = {
    "BooruToString": BooruToString
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BooruToString": "🏷️ Booru To String"
}