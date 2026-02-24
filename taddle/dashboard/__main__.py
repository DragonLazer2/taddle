from __future__ import annotations

from .app import DashboardApp


def main() -> None:
    app = DashboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
