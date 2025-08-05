import re
from typing import Optional, Tuple

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove spaces and special characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it matches international format
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, cleaned))

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to international format"""
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Add + if not present
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    return cleaned

def parse_group_input(group_input: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse group input and return (group_id, username, invite_link)
    
    Args:
        group_input: Can be:
            - Telegram link: https://t.me/groupname or t.me/groupname
            - Username: @groupname or groupname
            - Group ID: -1001234567890 or 1234567890
    
    Returns:
        Tuple of (group_id, username, invite_link)
    """
    if not group_input:
        return None, None, None
    
    group_input = group_input.strip()
    
    # Check if it's a Telegram link
    if 't.me/' in group_input.lower():
        # Extract username from link
        match = re.search(r't\.me/([a-zA-Z0-9_]+)', group_input, re.IGNORECASE)
        if match:
            username = match.group(1)
            return None, username, group_input
    
    # Check if it's a username (starts with @ or just alphanumeric)
    elif group_input.startswith('@') or re.match(r'^[a-zA-Z0-9_]+$', group_input):
        username = group_input.lstrip('@')
        return None, username, None
    
    # Check if it's a group ID (numeric, possibly negative)
    elif re.match(r'^-?\d+$', group_input):
        group_id = group_input
        return group_id, None, None
    
    # If none of the above, treat as username
    else:
        username = group_input.lstrip('@')
        return None, username, None

def validate_api_credentials(api_id: str, api_hash: str) -> bool:
    """Validate API ID and API Hash format"""
    if not api_id or not api_hash:
        return False
    
    # API ID should be numeric
    if not api_id.isdigit():
        return False
    
    # API Hash should be 32 characters long and alphanumeric
    if len(api_hash) != 32 or not re.match(r'^[a-f0-9]+$', api_hash, re.IGNORECASE):
        return False
    
    return True

def validate_message_content(content: str) -> bool:
    """Validate message content"""
    if not content or len(content.strip()) == 0:
        return False
    
    # Check if content is not too long (Telegram limit is 4096 characters)
    if len(content) > 4096:
        return False
    
    return True

def sanitize_input(text: str) -> str:
    """Sanitize input text to prevent XSS and other attacks"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]
    
    return sanitized.strip()

