"""ollama_tunnel.py — SSH tunnel to a remote Ollama server.

Opens a local port forward: localhost:LOCAL_PORT → REMOTE_HOST:REMOTE_PORT
via an SSH host you configure.

Usage:
    python scripts/ollama_tunnel.py            # foreground, blocks until Ctrl-C
    python scripts/ollama_tunnel.py --check    # verify tunnel then exit

Environment variables (loaded from .env) — MC_SSH_HOST is required:
    MC_SSH_HOST     SSH host (required; no default)
    MC_SSH_USER     SSH username (default: current local user)
    MC_SSH_PORT     SSH port (default: 22)
    MC_PASSWORD     SSH password
    OLLAMA_REMOTE_HOST  Host on the remote side (default: localhost)
    OLLAMA_REMOTE_PORT  Ollama port on remote (default: 11434)
    OLLAMA_LOCAL_PORT   Local port to bind (default: 11434)

After the tunnel is open, point AOBench at the local forwarded port:
    OLLAMA_BASE_URL=http://localhost:11434 LLM_PROVIDER=ollama aobench run ...
"""

from __future__ import annotations

import getpass
import os
import signal
import socket
import sys
import threading
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import paramiko
except ImportError:
    sys.exit("paramiko is required: pip install paramiko>=2.12.0")


# ── Config ────────────────────────────────────────────────────────────────────

# No site-specific defaults: this script is published, so a hard-coded host,
# username or port would expose a real SSH target. Configure these in .env.
SSH_HOST        = os.environ.get("MC_SSH_HOST", "")
SSH_USER        = os.environ.get("MC_SSH_USER", "") or getpass.getuser()
SSH_PORT        = int(os.environ.get("MC_SSH_PORT", "22"))
SSH_PASSWORD    = os.environ.get("MC_PASSWORD", "")

if not SSH_HOST:
    sys.exit(
        "MC_SSH_HOST is not set.\n"
        "This script needs the SSH host of your own Ollama server. Set it in .env:\n"
        "    MC_SSH_HOST=your-ssh-host\n"
        "    MC_SSH_USER=your-username     # optional, defaults to your local user\n"
        "    MC_SSH_PORT=22                # optional\n"
        "The full variable list is in this file's module docstring."
    )

REMOTE_HOST     = os.environ.get("OLLAMA_REMOTE_HOST", "localhost")
REMOTE_PORT     = int(os.environ.get("OLLAMA_REMOTE_PORT", "11434"))
LOCAL_PORT      = int(os.environ.get("OLLAMA_LOCAL_PORT", "11434"))


# ── Tunnel handler ────────────────────────────────────────────────────────────

def _forward_channel(local_sock: socket.socket, transport: paramiko.Transport) -> None:
    peer = local_sock.getpeername()
    try:
        chan = transport.open_channel(
            "direct-tcpip",
            (REMOTE_HOST, REMOTE_PORT),
            peer,
        )
    except Exception as exc:
        print(f"[tunnel] channel open failed: {exc}", file=sys.stderr)
        local_sock.close()
        return

    def pump(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        finally:
            try:
                src.close()
            except Exception:
                pass
            try:
                dst.close()
            except Exception:
                pass

    t1 = threading.Thread(target=pump, args=(local_sock, chan), daemon=True)
    t2 = threading.Thread(target=pump, args=(chan, local_sock), daemon=True)
    t1.start()
    t2.start()


def _accept_loop(
    server_sock: socket.socket,
    transport: paramiko.Transport,
    stop_event: threading.Event,
) -> None:
    server_sock.settimeout(1.0)
    while not stop_event.is_set():
        try:
            client_sock, _ = server_sock.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        threading.Thread(
            target=_forward_channel, args=(client_sock, transport), daemon=True
        ).start()


# ── Public API ────────────────────────────────────────────────────────────────

def open_tunnel() -> tuple[paramiko.SSHClient, socket.socket, threading.Event]:
    """Connect to SSH host and start local port-forward listener.

    Returns (ssh_client, server_sock, stop_event).
    Call stop_event.set() + ssh_client.close() to tear down.
    """
    if not SSH_PASSWORD:
        sys.exit(
            "MC_PASSWORD not set. Add it to .env or set the environment variable."
        )

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[tunnel] connecting to {SSH_USER}@{SSH_HOST}:{SSH_PORT} …", flush=True)
    ssh.connect(
        hostname=SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        password=SSH_PASSWORD,
        look_for_keys=False,
        allow_agent=False,
        timeout=15,
    )
    print(f"[tunnel] connected. forwarding localhost:{LOCAL_PORT} → {REMOTE_HOST}:{REMOTE_PORT}", flush=True)

    transport = ssh.get_transport()
    transport.set_keepalive(30)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", LOCAL_PORT))
    server_sock.listen(10)

    stop_event = threading.Event()
    threading.Thread(
        target=_accept_loop, args=(server_sock, transport, stop_event), daemon=True
    ).start()

    return ssh, server_sock, stop_event


def check_tunnel() -> bool:
    """Open tunnel, probe Ollama /api/tags, print available models, close."""
    import urllib.request
    import json

    ssh, server_sock, stop_event = open_tunnel()
    time.sleep(0.5)  # let listener thread start
    ok = False
    try:
        url = f"http://localhost:{LOCAL_PORT}/api/tags"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        models = [m["name"] for m in data.get("models", [])]
        print(f"[tunnel] Ollama reachable. Models available: {models}")
        ok = True
    except Exception as exc:
        print(f"[tunnel] Ollama probe failed: {exc}", file=sys.stderr)
    finally:
        stop_event.set()
        server_sock.close()
        ssh.close()
    return ok


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    check_mode = "--check" in sys.argv

    if check_mode:
        sys.exit(0 if check_tunnel() else 1)

    ssh, server_sock, stop_event = open_tunnel()
    print(f"[tunnel] ready. Set OLLAMA_BASE_URL=http://localhost:{LOCAL_PORT} before running aobench.")
    print("[tunnel] Press Ctrl-C to stop.")

    def _shutdown(sig, frame):
        print("\n[tunnel] shutting down …")
        stop_event.set()
        server_sock.close()
        ssh.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
