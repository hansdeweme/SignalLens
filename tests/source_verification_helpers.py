"""Small deterministic image/HTTP fixtures; no listener, DNS or external assets."""
import io
import socket
from PIL import Image
import numpy as np
import cv2


def image_bytes(fmt='PNG', transformed=False):
    noise = np.random.default_rng(41).integers(0, 256, (384, 384, 3), dtype=np.uint8)
    pixels = np.clip((cv2.GaussianBlur(noise, (9, 9), 2).astype(float) - 128) * 4 + 128, 0, 255).astype(np.uint8)
    im = Image.fromarray(pixels)
    if transformed:
        im = im.resize((300, 300), Image.Resampling.LANCZOS)
    stream = io.BytesIO()
    im.save(stream, format=fmt, quality=92)
    return stream.getvalue()


def wire(monkeypatch, responses, *, private_host=None, wrong_peer=False):
    """Exercise the production HTTP parser/redirect logic on controlled sockets."""
    import source_image_verification as module
    connections, resolutions, sent, sni = [], [], [], []
    def resolve(host, port, **kwargs):
        resolutions.append(host)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                 ('127.0.0.1' if host == private_host else '93.184.216.34', port))]
    class Socket:
        def __init__(self, *args):
            self.response = io.BytesIO(responses.pop(0))
        def settimeout(self, value):
            assert 0 < value <= 5
        def connect(self, address):
            connections.append(address)
        def getpeername(self):
            return ('127.0.0.1' if wrong_peer else '93.184.216.34', 443)
        def sendall(self, data):
            sent.append(data)
        def makefile(self, *args):
            return self.response
        def close(self):
            pass
        def shutdown(self, how):
            pass
    class TLS:
        def wrap_socket(self, sock, server_hostname):
            sni.append(server_hostname)
            return sock
    monkeypatch.setattr(module.socket, 'getaddrinfo', resolve)
    monkeypatch.setattr(module.socket, 'socket', Socket)
    monkeypatch.setattr(module.ssl, 'create_default_context', lambda: TLS())
    return connections, resolutions, sent, sni


def response(data, media='image/png'):
    return f'HTTP/1.1 200 OK\r\nContent-Type: {media}\r\nContent-Length: {len(data)}\r\n\r\n'.encode() + data
