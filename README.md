# openvpn-socks5
The application is a web server for managing multiple VPN connections and providing access to them in the form of local SOCKS5 proxies.

The web server creates many VPN connections, and users connect to the VPN like a regular proxy server. 

The repository contains a docker image of an OpenVPN client bound to a SOCKS proxy.

This supports configurations where certificates are concatenated into one .ovpn file.

## Web server

Before you start you need to install the dependencies from requirements.txt.

```console
$ pip install -r requirements.txt
```

### Run it

Run the server with:

```console
$ cd api
$ uvicorn main:app

INFO:     Started server process [23188]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Interactive API docs

Now go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs</a>.)

You will see the automatic interactive API documentation provided by Swagger UI.

## Docker image
### Run it

```console
$ docker run -it --cap-add=NET_ADMIN --device /dev/net/tun -p 1080:your_port --dns 8.8.4.4 -v /your/openvpn/directory:/vpn -d saronqw/openvpn-socks5
```

Or you can build your own image first, and then run it. 
```console
$ docker build -t image_name .
$ docker run -it --cap-add=NET_ADMIN --device /dev/net/tun -p 1080:your_port --dns 8.8.4.4 -v /your/openvpn/directory:/vpn -d image_name
```