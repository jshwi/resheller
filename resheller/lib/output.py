#!/usr/bin/env python3


def usage(session=False, keylogger=False):
    if session:
        stdout = (
            "targets          --> view available targets\n"
            "session <number> --> select target by index\n"
        )

    elif not session and keylogger:
        stdout = (
            "keylogger <opt>    --> <start> --> start keylogger on target\n"
            "                       <dump>  --> retrieve logs from target\n"
        )
    else:
        stdout = (
            "help            --> print this help message\n"
            "download <path> --> download file from target\n"
            "upload <path>   --> upload file from target\n"
            "get <url>       --> download file from website to target\n"
            "screenshot      --> take screenshot on target\n"
            "check           --> check for admin privileges\n"
            "keylogger <opt> --> <start> --> start keylogger on target\n"
            "                    <dump>  --> retrieve logs from target\n"
            "quit            --> exit reverse shell\n"
        )
    return f"[*] Usage:\n\n{stdout}"
