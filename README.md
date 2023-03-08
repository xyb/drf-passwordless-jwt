# drf-passwordless-jwt

`drf-passwordless-jwt` is a RESTful API service that offers passwordless
authentication using JWT. In other words, it's a Single Sign-On (SSO)
service that allows users to log in without using a password.

## Features
- Email login token
- Obtain JWT token
- Verify JWT token
- Dummy accounts used for development and testing purposes.

## Usage

```sh
# Email login token
$ curl -X POST -d "email=xyb@test.com" localhost:8000/auth/email/
{"detail":"A login token has been sent to your email."}

Enter this token to sign in: 527389

# Obtain JWT token
$ curl -X POST -d "email=xyb@test.com&token=527389" localhost:8000/auth/jwt/
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Inh5YkB0ZXN0LmNvbSIsImV4cCI6MTY3NTI2Njg0NH0.a7RgJLEbeFSQeFZ93qjC2iHo_wabglwzBZ9fe9D-rfw","email":"xyb@test.com"}

# Verify JWT token
$ curl -X POST -d "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Inh5YkB0ZXN0LmNvbSIsImV4cCI6MTY3NTI2Njg0NH0.a7RgJLEbeFSQeFZ93qjC2iHo_wabglwzBZ9fe9D-rfw" \
  localhost:8000/auth/
{"email":"xyb@test.com","exp":"2023-02-01T15:54:04Z"}
```

It uses [Django REST framework](https://www.django-rest-framework.org/),
so you can also access this interface through your browser.

![](drf.webp)

## Dummy accounts

During development and testing, you may want to use dummy accounts to
save time. To do this, you can configure environment variables.
For example, if you want to use the email address a@a.com to log in,
you can set the environment variable:
```sh
$ export EMAIL_TEST_ACCOUNT_a_at_a_com=123456
```

Then, you can use the command:
```sh
$ curl -X POST -d "email=a@a.com&token=123456" localhost:8000/auth/jwt/
```

to directly obtain a JWT token without having to first obtain a login
token via email. This way, you can cut out the step of first getting
a login token via email, and immediately receive a JWT token.
This hack could save you significant time.

## Configuration

You should customize your configuration to suit your requirements.
All configurations can be set via environment variables.
The following are the configured default values:

```python
# 0: production, 1: devlopment
DJANGO_DEBUG = 1

# specify hosts seperated by commas
DJANGO_ALLOWED_HOSTS = '*'

# 1: print email to screen, not sending
EMAIL_BACKEND_TEST = 0

# email from
OTP_EMAIL_ADDRESS = 'xyb@mydomain.com'

# token expire time, default 5 minutes
OTP_TOKEN_EXPIRE_SECONDS = 300

# email subject
OTP_EMAIL_SUBJECT = 'Your Login Token'

# email text message
OTP_EMAIL_PLAINTEXT = 'Enter this code to sign in: %s'

# email html message template file
# set it to 'passwordless_zh_token_email.html' to use the built-in Chinese template.
OTP_EMAIL_HTML = 'passwordless_token_email.html'

# 1: ssl smtp
EMAIL_USE_SSL = 0

# 1: tls smtp
EMAIL_USE_TLS = 0

EMAIL_HOST = 'smtp.mydomain.com'

EMAIL_HOST_USER = 'xyb@mydomain.com'

EMAIL_HOST_PASSWORD = 'password'

EMAIL_PORT = 465

EMAIL_FROM = 'xyb@mydomain.com'

# fail if smtp server response too slow
EMAIL_TIMEOUT = 3

# regex, for example: '.*@mail1.com$|.*@mail2.com'
EMAIL_WHITE_LIST = r'.*'

# message on rejection
EMAIL_WHITE_LIST_MESSAGE = 'unacceptable email address'

# dummy account env prefix
EMAIL_TEST_ACCOUNT_PREFIX = 'EMAIL_TEST_ACCOUNT_'

# specify hosts separeated by commas
CORS_ALLOWED_ORIGINS = ''

# 1: accept any remote host
CORS_ALLOW_ALL_ORIGINS = 0

DB_ENGINE = 'django.db.backends.sqlite3'

DB_NAME = BASE_DIR / 'db.sqlite3'

DB_USER = 'postgres'

DB_PASSWORD = ''

DB_HOST = ''

DB_PORT = ''

# JWT secret string
JWT_SECRET = 'secret-for-jwt'

# JWT expire time, default 30 days
JWT_EXPIRE_SECONDS = 2592000
```

## Docker

During development, you can build and run it on your local host:

```sh
$ docker build -t auth .
$ docker run --rm -p 8000:8000 -e EMAIL_BACKEND_TEST=1 auth
```

There are pre-built [docker images](https://hub.docker.com/r/xieyanbo/drf-passwordless-jwt).
You can use docker-compose for deployment.
This is a template of `docker-compose.yml`:

```yaml
version: "3"

services:
  auth:
    image: xieyanbo/drf-passwordless-jwt:latest
    container_name: auth
    environment:
      - TZ=Asia/Hong_Kong
      - DJANGO_SECRET_KEY=secret-string
      - DJANGO_DEBUG=0
      - OTP_EMAIL_ADDRESS=xyb@mydomain.com
      - OTP_TOKEN_EXPIRE_SECONDS=300
      - OTP_EMAIL_SUBJECT=Your Login Token
      - OTP_EMAIL_PLAINTEXT=Enter this code to sign in: %s
      - OTP_EMAIL_HTML=passwordless_token_email.html
      - EMAIL_BACKEND_TEST=0
      - EMAIL_USE_SSL=0
      - EMAIL_USE_TLS=1
      - EMAIL_HOST=smtp.mydomain.com
      - EMAIL_PORT=465
      - EMAIL_HOST_USER=xyb@mydomain.com
      - EMAIL_HOST_PASSWORD=password
      - EMAIL_FROM=xyb@mydomain
      - EMAIL_WHITE_LIST=.*@mydomain.com$$|.*@mydomain2.com$$
      - EMAIL_WHITE_LIST_MESSAGE=for mydomain.com and mydomain2.com only
      - JWT_SECRET=secret-for-jwt
      - JWT_EXPIRE_SECONDS=2592000
    ports:
      - 8000:8000
    restart: always
```
