# ReShellEr
### Reverse Shell servEr
    Expanded upon from "Multi-functioning Reverse Shell" in 
    "Master Ethical Hacking with Python!" by Joseph Delgadillo:
    https://www.udemy.com/course/ethical-hacking-python/

### Prerequisites
    Python3

### Install Dependencies
    If you are a user of virtual environments
    python3* install.py
    
    Package contains two modules:
        1. resheller (command and control centre)
        2. client/client.exe (Unix and Windows respectively)
        
    


## Getting Started
    * Includes two modules:
        * client.exe
        * resheller/server.py
    * Get client.exe on target Windows machine
    * Run shell commands from server.py

## Usage:
    help            --> print this help message
    download <path> --> download file from target
    upload <path>   --> upload file from target
    get <url>       --> download file from website to target
    screenshot      --> take screenshot on target
    check           --> check for admin privileges
    keylog <opt>    --> <start> --> start keylogger on target
                        <dump>  --> retrieve logs from target
    quit            --> exit reverse shell

<sup>* On windows command may simply be python when working within a 
python3 based virtual environment</sup>

## Author

    Stephen Whitlock

#
