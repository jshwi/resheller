from lib.title import Title
from server.server import Server


def main():
    title = Title()
    server = Server()
    title.clear_screen()
    title.resheller()
    server.sock_object()
    server.thread()
    title.header()
    server.control_centre()
