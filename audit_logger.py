import logging

logging.basicConfig(filename='audit.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_event(event_type, user, file_name):
    logging.info(f"{event_type} by {user}: {file_name}")
