# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from services.publications import create_publication,update_publication,delete_publication
from services.blog import create_blog,update_blog,delete_blog
from services.club_talk import create_card,update_card,delete_card
from services.about_us import create_member,update_member,delete_member


initialize_app()

@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")

