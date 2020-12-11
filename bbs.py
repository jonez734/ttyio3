import ttyio3 as ttyio
import bbsengine4 as bbsengine
from threading import Timer

# import signal

import readline

global done

class IdleTimeout(Exception):
    pass

# def timeouthandler(signum, frame):
#     ttyio.echo("IDLE")
#     raise IdleTimeout

def hello():
    global done
    print ("yes!")
    done = True
#    raise IdleTimeout
    return

def main():
    global done
    done = False
    while not done:
        ttyio.echo("top of loop")
        t = Timer(5, hello)
        t.start()
        ttyio.inputstring("gfd main: ", timeout=0, noneok=True)# , timeouthandler=timeouthandler)
        ttyio.echo("foo")
        done = True
        readline.redisplay()
        ttyio.echo("bottom of loop")
        t.cancel()
if __name__ == "__main__":
    main()
