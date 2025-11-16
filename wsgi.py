from app import create_app

# gunicorn इस 'application' वेरिएबल को कॉल करेगा
application = create_app()
