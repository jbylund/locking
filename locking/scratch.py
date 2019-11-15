from . import FileLock

def main():
    lockname = "foo"
    with FileLock(lockname):
        print("got lock 1")
        with FileLock(lockname):
            print("got lock 2")

if "__main__" == __name__:
    main()

