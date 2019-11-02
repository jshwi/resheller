from sys import argv


def build():
    try:
        assert argv[1]
        install()
        exit(0)
    except IndexError:
        pass


def main():
    build()
    title = Title()
    server = Server()
    title.clear_screen()
    title.resheller()
    server.sock_object()
    server.thread()
    title.header()
    server.control_centre()