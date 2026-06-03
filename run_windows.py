import logging
import sys
import traceback

try:
    from waitress import serve
except ImportError:
    print("ERROR: waitress is not installed!")
    print("Please install it with: pip install -r requirements.txt")
    sys.exit(1)

try:
    from app import app, create_db_and_seed
except ImportError as e:
    print(f"ERROR: Failed to import app: {e}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    # Set up basic logging for waitress
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    print("================================================================")
    print("Starting ICH Ticketing System on Windows via Waitress...")
    print("The system is binding to 0.0.0.0, making it accessible on the local network.")
    print("Other machines can access this server using: http://<THIS_MACHINE_IP>:8000")
    print("================================================================\n")
    
    # Ensure database and admin user exist before starting
    try:
        print("[*] Initializing database and seeding...")
        create_db_and_seed()
        print("[✓] Database initialized successfully.\n")
    except Exception as e:
        print(f"[✗] ERROR during database initialization: {e}")
        traceback.print_exc()
        print("\nFailed to start application due to database error.")
        sys.exit(1)
    
    # Bind to 0.0.0.0 to listen on all network interfaces
    try:
        print("[*] Starting Waitress server on 0.0.0.0:8000...")
        serve(app, host='0.0.0.0', port=8000)
    except Exception as e:
        print(f"[✗] ERROR: Failed to start server: {e}")
        traceback.print_exc()
        sys.exit(1)
