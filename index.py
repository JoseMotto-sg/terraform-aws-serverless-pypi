import json
import os
import re
import string
import sys

import boto3

BASE_PATH = os.getenv('BASE_PATH', '').strip('/')
ANCHOR = string.Template('<a href="$href">$name</a><br>')
INDEX = string.Template(
    '<!DOCTYPE html><html><head><title>$title</title></head>'
    '<body><h1>$title</h1>$anchors</body></html>'
)

S3 = boto3.client('s3')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_PAGINATOR = S3.get_paginator('list_objects')
S3_PRESIGNED_URL_TTL = int(os.getenv('S3_PRESIGNED_URL_TTL', '900'))


# Lambda helpers


def get_index():
    """ GET /{BASE_PATH}/

        :return dict: Response
    """
    index = S3.get_object(Bucket=S3_BUCKET, Key='index.html')
    body = index['Body'].read().decode()
    res = proxy_reponse(body)
    return res


def get_package_index(name):
    """ GET /{BASE_PATH}/<pkg>/

        :param str name: Package name
        :return dict: Response
    """
    # Get keys for given package
    pages = S3_PAGINATOR.paginate(Bucket=S3_BUCKET, Prefix=f'{name}/')
    keys = [
        key.get('Key')
        for page in pages
        for key in page.get('Contents') or []
    ]

    # Convert keys to presigned URLs
    hrefs = [presign(key) for key in keys]

    # Extract names of packages from keys
    names = [os.path.split(x)[-1] for x in keys]

    # Construct HTML
    anchors = [
        ANCHOR.safe_substitute(href=href, name=name)
        for href, name in zip(hrefs, names)
    ]
    body = INDEX.safe_substitute(
        title=f'Links for {name}',
        anchors=''.join(anchors)
    )

    # Convert to Lambda proxy response
    resp = proxy_reponse(body)

    # Return Lambda prozy response
    return resp


def get_response(path):
    """ GET /{BASE_PATH}/*

        :param str path: Request path
        :return sict: Response
    """
    try:
        name = re.match(f'^{BASE_PATH}/([^/]+)$', path).group(1)
    except AttributeError:
        name = None

    # GET /{BASE_PATH}/*
    if name:
        return get_package_index(name)

    # GET /{BASE_PATH}
    elif BASE_PATH == path:
        return get_index()

    # GET /
    elif '' == path:
        return redirect(f'/{BASE_PATH}')

    # 403 Forbidden
    return reject(403)


def presign(key):
    """ Presign package URLs.

        :param str key: S3 key to presign
        :return str: Presigned URL
    """
    url = S3.generate_presigned_url(
        'get_object',
        ExpiresIn=S3_PRESIGNED_URL_TTL,
        HttpMethod='GET',
        Params={'Bucket': S3_BUCKET, 'Key': key},
    )
    return url


def proxy_reponse(body, content_type=None):
    """ Convert HTML to API Gateway response.

        :param str body: HTML body
        :return dict: API Gateway Lambda proxy response
    """
    content_type = content_type or 'text/html'
    # Wrap HTML in proxy response object
    return {
        'body': body,
        'headers': {'Content-Type': f'{content_type}; charset=UTF-8'},
        'statusCode': 200,
    }


def redirect(path):
    """ Redirect requests.

        :param str path: Rejection status code
        :return dict: Redirection response
    """
    return {'statusCode': 301, 'headers': {'Location': path}}


def reject(status_code):
    """ Bad request.

        :param int status_code: Rejection status code
        :return dict: Rejection response
    """
    return {'statusCode': status_code}


# Lambda handlers


def proxy_request(event, *_):
    """ Handle API Gateway proxy request. """
    print(f'EVENT {json.dumps(event)}')
    print(f'BASE_PATH {BASE_PATH!r}')

    # Get HTTP request method/path
    method = event.get('httpMethod')
    path = event.get('path').strip('/')

    # Get HTTP response
    if method in ['GET', 'HEAD']:
        res = get_response(path)
    else:
        res = reject(403)

    # Return proxy response
    print(f'RESPONSE {json.dumps(res)}')
    return res


def reindex_bucket(event, *_):
    """ Reindex S3 bucket. """
    print(f'EVENT {json.dumps(event)}')

    # Get package names from common prefixes
    pages = S3_PAGINATOR.paginate(Bucket=S3_BUCKET, Delimiter='/')
    pkgs = (
        x.get('Prefix').strip('/')
        for page in pages
        for x in page.get('CommonPrefixes')
    )

    # Construct HTML
    anchors = (ANCHOR.safe_substitute(href=pkg, name=pkg) for pkg in pkgs)
    body = INDEX.safe_substitute(
        title='Simple index',
        anchors=''.join(anchors)
    )

    # Upload to S3 as index.html
    res = S3.put_object(Bucket=S3_BUCKET, Key='index.html', Body=body.encode())
    return res


if __name__ == '__main__':  # pragma: no cover
    try:
        path = sys.argv[1]
        event = {'path': path, 'httpMethod': 'GET'}
    except IndexError:
        this = os.path.basename(__file__)
        raise SystemExit(f"usage: python {this} <url-path>")
    proxy_request(event)
