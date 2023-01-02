# drf_passwordless_jwt

```sh
$ docker build -t auth .
$ docker run --rm -p 8000:8000 -e EMAIL_BACKEND_TEST=1 auth

$ curl -X POST -d "email=xyb@test.com" localhost:8000/auth/email/
{"detail":"A login token has been sent to your email."}

Enter this token to sign in: 527389

$ curl -X POST -d "email=xyb@test.com&token=527389" localhost:8000/auth/jwt/
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Inh5YkB0ZXN0LmNvbSIsImV4cCI6MTY3NTI2Njg0NH0.a7RgJLEbeFSQeFZ93qjC2iHo_wabglwzBZ9fe9D-rfw","email":"xyb@test.com"}

$ curl -X POST -d "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Inh5YkB0ZXN0LmNvbSIsImV4cCI6MTY3NTI2Njg0NH0.a7RgJLEbeFSQeFZ93qjC2iHo_wabglwzBZ9fe9D-rfw" localhost:8000/auth/
{"email":"xyb@test.com","exp":"2023-02-01T15:54:04Z"}
```
