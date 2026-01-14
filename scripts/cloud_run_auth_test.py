import requests
from google.auth import default
from google.auth.transport.requests import Request


def get_identity_token(target_audience: str):
    """Get ID token using Google Auth library"""
    try:
        credentials, project = default()
        print(f"Got default credentials for project: {project}")

        # Check if we already have a token
        if credentials.id_token:
            return credentials.id_token

        # If not, refresh the credentials
        request = Request()
        credentials.refresh(request)

        # Now try to get the ID token
        if hasattr(credentials, "id_token"):
            return credentials.id_token

        print("Could not get ID token from credentials")
        return None

    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Credentials type: {type(credentials)}")
        raise


def test_access(url: str):
    print("Testing without auth...")
    response = requests.get(url)
    print(f"No auth response: {response.status_code}")

    print("\nTesting with auth...")
    token = get_identity_token(url)
    if not token:
        print("No token available")
        return

    print("Got token")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Auth response: {response.status_code}")

    if response.status_code != 200:
        print("Response headers:", response.headers)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test IAP-protected endpoint access")
    parser.add_argument("url", help="Service URL")
    args = parser.parse_args()

    test_access(args.url.rstrip("/"))
