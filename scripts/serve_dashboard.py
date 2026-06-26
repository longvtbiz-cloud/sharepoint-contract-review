import argparse
import json
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.dashboard_data import build_dashboard_data


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def refresh_dashboard_data(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "data.json"
    output.write_text(json.dumps(build_dashboard_data(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def serve_dashboard(host: str, port: int, directory: Path, refresh: bool = True) -> None:
    if refresh:
        refresh_dashboard_data(directory)

    handler = partial(NoCacheHandler, directory=str(directory))
    server = ThreadingHTTPServer((host, port), handler)
    url_host = "127.0.0.1" if host in {"0.0.0.0", ""} else host
    print(f"Serving governance dashboard at http://{url_host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server.")
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh and serve the local governance dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--directory", type=Path, default=Path("dashboard"))
    parser.add_argument("--no-refresh", action="store_true")
    parser.add_argument("--once", action="store_true", help="Refresh data and exit without starting a server.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.once:
        output = refresh_dashboard_data(args.directory)
        print(f"Refreshed {output}")
        return
    serve_dashboard(args.host, args.port, args.directory, refresh=not args.no_refresh)


if __name__ == "__main__":
    main()
