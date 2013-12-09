import sys
from sfxtracker.app import main

if __name__ == '__main__':
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        main(host, port)
    else:
        main()