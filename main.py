#!/usr/bin/env python3

###########
# WARNING #
###########
#
# If you intend to play with this project as a challenge to solve, do not
# read this source file, it contains spoilers.
#
# You've been warned.

import json
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from base64 import urlsafe_b64encode, urlsafe_b64decode
from bottle import route, request, template

ENCRYPTION_KEY = get_random_bytes(16)
ENCRYPTION_IV  = get_random_bytes(8)

def encrypt(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR, nonce=ENCRYPTION_IV)
    return cipher.encrypt(data)

def decrypt(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR, nonce=ENCRYPTION_IV)
    return cipher.decrypt(data)


def decode_params(encoded_params):
    if not encoded_params:
        return
    result = {}
    decoded = decrypt(urlsafe_b64decode(encoded_params + "===")).decode("utf8")
    for pair in decoded.split("&"):
        key,value = pair.split("=", 1)
        if key == "page":
            result["page"] = value
        elif key == "maintenance":
            result["maintenance"] = value
        elif key == "loggedin":
            result["loggedin"] = value
        elif key == "admin":
            result["admin"] = value
        elif key == "userid":
            result["userid"] = value
    return result


def encode_params(params):
    result =  "page="         + params["page"]
    if "maintenance" in params:
        result += "&maintenance=" + params["maintenance"]
    if "loggedin" in params:
        result += "&loggedin="    + params["loggedin"]
    if "admin" in params:
        result += "&admin="       + params["admin"]
    if "userid" in params:
        result += "&userid="      + params["userid"]
    return urlsafe_b64encode(encrypt(result.encode("utf8"))).decode("utf8").strip("=")


def base_page_url(page):
    return '/?params=' + encode_params({'page':page,'loggedin':'false','admin':'false','userid':'0'})

@route("/")
def show_index():
    USERS = { 0:"Not found",
              1:"nancy28",
              2:"fred69",
              3:"cathy88",
              4:"ben1337" }

    params = decode_params(request.query.params)

    if not params or "page" not in params or params["page"] == "home":
        maintenance = True
        if params and "maintenance" in params:
            maintenance = params["maintenance"] == "true"
        return template(open("templates/home.html").read(),
                        no_params=(params is None),
                        maintenance=maintenance,
                        home_url=("/?params=" + encode_params({'page':'home','maintenance':'true'})),
                        profile_url=base_page_url("profile"),
                        admin_url=base_page_url("administration"),
                        aboutus_url=base_page_url("aboutus"))

    elif params["page"] == "profile":
        loggedin = params["loggedin"] == "true"
        is_admin = params["admin"] == "true"
        uid = int(params["userid"])

        return template(open("templates/profile.html").read(),
                        loggedin=(params["loggedin"] == "true"),
                        is_admin=(params["admin"] == "true"),
                        username=USERS.get(int(params["userid"]), 0),
                        uid=uid)

    elif params["page"] == "administration":
        return template(open("templates/administration.html").read(),
                        is_admin=(params["admin"] == "true"))

    elif params["page"] == "aboutus":
        return open("templates/aboutus.html").read()

    else:
        return template(open("templates/404.html").read(),
                        home_url=("/?params=" + encode_params({'page':'home','maintenance':'true'})))


if __name__ == "__main__":
    import bottle
    bottle.run(host="127.0.0.1", port=9876)

#page=home&maintenance=true
#page=administration&loggedin=false&admin=false&userid=0
#page=profile&loggedin=false&admin=false&userid=0
#page=aboutus&loggedin=false&admin=false&userid=0
