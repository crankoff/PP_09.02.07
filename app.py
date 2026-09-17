"""FlowBoard entry point."""

from kanban.config import Config
from kanban.web import create_server


def main() -> None:
    config = Config.from_env()
    server = create_server(config)
    print(f"FlowBoard started on http://{config.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nFlowBoard stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
