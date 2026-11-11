"""Entry point for easyrepo."""

from easyrepo.app import EasyRepoApp


def main() -> None:
    app = EasyRepoApp()
    app.run()


if __name__ == "__main__":
    main()
