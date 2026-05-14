import logging
from waitress import serve
from app import app, create_db_and_seed

if __name__ == '__main__':
    # Set up basic logging for waitress
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    print("================================================================")
    print("Starting ICH Ticketing System on Windows via Waitress...")
    print("The system is binding to 0.0.0.0, making it accessible on the local network.")
    print("Other machines can access this server using: http://<THIS_MACHINE_IP>:8000")
    print("================================================================\n")
    
    # Ensure database and admin user exist before starting
    create_db_and_seed()
    
    # Bind to 0.0.0.0 to listen on all network interfaces
    serve(app, host='0.0.0.0', port=8000)
