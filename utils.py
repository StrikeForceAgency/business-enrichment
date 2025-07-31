def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_phone_numbers(text):
    import re
    pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{1,4}?\)?[-.\s]?)?(\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
    return re.findall(pattern, text)

def log_error(message):
    import logging
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    logging.error(message)

def manage_api_call_limits(call_count, limit=300):
    if call_count >= limit:
        time.sleep(60)  # Sleep for 1 minute after reaching the limit
        return 0
    return call_count