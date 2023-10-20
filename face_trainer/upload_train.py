import requests

def main():
    print("UPLAOD FILE")

    url = 'http://raspberrypi.local:5000/upload'
    filepath = '../encodings.pickle'

    with open(filepath, 'rb') as f:
        requests.post(url, data=f)

    content = '<p>OK 200 : Done Upload</p>'
    print(content)
