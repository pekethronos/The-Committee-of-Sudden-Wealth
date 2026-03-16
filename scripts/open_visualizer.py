#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.server
import threading
import webbrowser
from functools import partial
from pathlib import Path


class VisualizerHTTPServer(http.server.HTTPServer):
    shutdown_flag = False


class VisualizerRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # type: ignore[override]
        self.server.shutdown_flag = True  # type: ignore[attr-defined]
        return super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a backtest log to the Prosperity 3 visualizer.")
    parser.add_argument("logfile", type=Path)
    parser.add_argument("--no-open", action="store_true", help="Print the visualizer URL instead of opening a browser.")
    args = parser.parse_args()

    logfile = args.logfile.resolve()
    handler = partial(VisualizerRequestHandler, directory=str(logfile.parent))
    server = VisualizerHTTPServer(("127.0.0.1", 0), handler)
    url = (
        "https://jmerle.github.io/imc-prosperity-3-visualizer/"
        f"?open=http://127.0.0.1:{server.server_port}/{logfile.name}"
    )
    print(url, flush=True)

    if not args.no_open:
        webbrowser.open(url)

    def serve() -> None:
        while not server.shutdown_flag:
            server.handle_request()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    thread.join()


if __name__ == "__main__":
    main()
