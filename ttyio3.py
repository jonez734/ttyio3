import os, sys
import tty, termios, fcntl
import time
import select
import socket
# import signal # non-blocking inputstring()
import re

from typing import Any, List

import colorclass

_RCSID = "$Id: ttyio.py,v 1.2 2003/09/25 14:20:55 jam Exp $"

DEBUG = False

# <http://www.python.org/doc/faq/library.html#how-do-i-get-a-single-keypress-at-a-time>
# http://craftsman-hambs.blogspot.com/2009/11/getch-in-python-read-character-without.html
def getch():
  fd = sys.stdin.fileno()

  oldterm = termios.tcgetattr(fd)

  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)

  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
  try:
      while 1:
              try:
                r, w, x = select.select([fd],[],[],0.250)
              except socket.error as e:
                echo("%r: %r" % (e.code, e.msg), level="error")
                if e.args[0] == 4:
                  echo("interupted system call (tab switch?)")
                  continue
                #if code <> errno.EINTR:
                #  raise
                
              if len(r) == 1:
                ch = sys.stdin.read(1)
                return ch
  finally:
      termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
      fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
      print ("\x1b[0m", end="")

  return ch

# <http://www.python.org/doc/faq/library.html#how-do-i-get-a-single-keypress-at-a-time>
# http://craftsman-hambs.blogspot.com/2009/11/getch-in-python-read-character-without.html
def getchbusywait():
  pass

# https://gist.github.com/sirpengi/5045885 2013-feb-27 in oftcphp sirpengi
# @since 20140529
# @since 20200719
def collapselist(lst):
    def chunk(lst):
        ret = [lst[0],]
        for i in lst[1:]:
            if ord(i) == ord(ret[-1]) + 1:
                pass
            else:
                yield ret
                ret = []
            ret.append(i)
        yield ret
    chunked = chunk(lst)
    ranges = ((min(l), max(l)) for l in chunked)
    return ", ".join("{0}-{1}".format(*l) if l[0] != l[1] else l[0] for l in ranges)

def accept(prompt, options, default="", debug=False, collapse=False):
  if debug is True:
    echo("ttyio3.accept.100: options=%s" % (options), level="debug")
        
  default = default.upper() if default is not None else ""
  options = options.upper()
  foo = list(set(options))
  foo = sorted(foo)
  if collapse is True:
    foo = collapselist(list(foo))
  else:
    foo = "".join(foo)
      
#  if isinstance(prompt, colorclass.Color) is False:
#    prompt = colorclass.Color(buf)
  prompt += " [%s]" % (foo)
      
  echo("%s: " % (prompt), end="")
#  sys.stdout.write("%s: " % (prompt))
  sys.stdout.flush()

  while 1:
    ch = getch().upper()
    
    if ch == "\n":
      return default
      if default is not None:
        return default
      else:
        return ch
    elif ch in options:
      return ch

def inputboolean(prompt, default=None):
	ch = accept(prompt, "YNTF", default)
	if ch == "Y":
		echo("Yes")
		return True
	elif ch == "T":
		echo("True")
		return True
	elif ch == "N":
		echo("No")
		return False
	elif ch == "F":
		echo("False")
		return False

def acceptboolean(prompt, default=None):
  echo("acceptboolean has been renamed to inputboolean", level="warn")
  return inputboolean(prompt, default)

# copied from bbsengine.py
def echo(buf="", stripcolor=False, level=None, datestamp=False, end="\n", auto=True, **kw):
  from dateutil.tz import tzlocal
  from datetime import datetime
  from time import strftime

  buf = str(buf)

  if datestamp is True:
    now = datetime.now(tzlocal())
    stamp = strftime("%Y-%b-%d %I:%M:%S%P %Z (%a)", now.timetuple())
    buf = "%s %s" % (stamp, buf)

  if level is not None:
    if level == "debug":
      buf = "{autoblue}%s{/autoblue}" % (buf)
    elif level == "warn":
      buf = "{autoyellow}%s{/autoyellow}" % (buf)
    elif level == "error":
      buf = "{autored}%s{/autored}" % (buf)
    elif level == "success":
      buf = "{autogreen}%s{/autogreen}" % (buf)

  if isinstance(buf, colorclass.Color) is False:
    buf = colorclass.Color(buf)

  if stripcolor is False:
    print(buf, end=end)
  else:
    print(buf.value_no_colors, end=end)
  return

# http://www.brandonrubin.me/2014/03/18/python-snippet-get-terminal-width/
def getterminalwidth():
  import subprocess
 
  command = ['tput', 'cols']
 
#  if sys.stdout.isatty() is False:
#    return False

  try:
    width = int(subprocess.check_output(command))
  except OSError as e:
    print("Invalid Command '{0}': exit status ({1})".format(command[0], e.errno))
    return False
  except subprocess.CalledProcessError as e:
    print("Command '{0}' returned non-zero exit status: ({1})".format(command, e.returncode))
    return False
  else:
    return width

def xtname(name):
  if sys.stdout.isatty() is False:
    return False
  echo("\x1b]0;%s\x07" % (name))
  return

def handlemenu(opts, title, items, oldrecord, currecord, prompt="option", defaulthotkey=""):
    hotkeys = {}

    hotkeystr = ""

    for item in items:
        label = item["label"].lower()
        hotkey = item["hotkey"].lower() if item.has_key("hotkey") else None
#        ttyio.echo("hotkey=%s" % (hotkey), level="debug")
        if hotkey is not None and hotkey in label:
            label = label.replace(hotkey.lower(), "[{autocyan}%s{/autocyan}]" % (hotkey.upper()), 1)
        else:
            label = "[{autocyan}%s{/autocyan}] %s" % (hotkey, label)
        if item.has_key("key"):
            key = item["key"]
            if oldrecord[key] != currecord[key]:
                buf = "%s: %s (was %s)" % (label, currecord[key], oldrecord[key])
            else:
                buf = "%s: %s" % (label, currecord[key])
        else:
            buf = label
        
        hotkeys[hotkey] = item # ["longlabel"] if item.has_key("longlabel") else None
        if hotkey is not None:
            hotkeystr += hotkey
        echo(buf,datestamp=False)
    
    if currecord != oldrecord:
      echo("{autoyellow}** NEEDS SAVE **{/autoyellow}", datestamp=False)
    
    echo()
  
    ch = accept(prompt, hotkeystr, defaulthotkey)
    ch = ch.lower()
    longlabel = hotkeys[ch]["longlabel"] if hotkeys[ch].has_key("longlabel") else None
    if longlabel is not None:
        echo("{autocyan}%s{/autocyan} -- %s" % (ch.upper(), longlabel), datestamp=False)
    else:
        echo("{autocyan}%s{/autocyan}" % (ch.upper()), datestamp=False)
    return hotkeys[ch]

# bbsengine.input*() moved to ttyio
# @since 20170419
def inputdate(prompt, oldvalue=None, **kw):
  if oldvalue is not None:
    buf = inputstring(prompt, datestamp(oldvalue), **kw)
  else:
    buf = inputstring(prompt, **kw)
  epoch = getdate.getdate(buf)
  tz = LocalTimezone()
  stamp = datetime.fromtimestamp(epoch, tz)
  return stamp # datetime.fromtimestamp(epoch)

# @see https://stackoverflow.com/questions/9043551/regex-that-matches-integers-only
def inputinteger(prompt, oldvalue=None, mask="^([+-]?[1-9]\d*|0)$") -> int:
  oldvalue = int(oldvalue) if oldvalue is not None else ""
  buf = inputstring(prompt, oldvalue, mask=mask)

  if buf is None or buf == "":
    return None
  
  try:
    res = int(float(buf))
  except:
    return None
  else:
    return res

def timeouthandler(signum, frame):
  echo("timeout handler")
  raise Exception
  return

# @since 20110323
# @since 20190913
# @since 20200626
# @since 20200729
# @since 20200901
def inputstring(prompt:str, oldvalue:str=None, opts:object=None, timeout=0, timeouthandler=timeouthandler, mask=None, **kw) -> str:
  import readline
  def preinputhook():
    readline.insert_text(str(oldvalue))
    readline.redisplay()

  if oldvalue is not None:
    readline.set_pre_input_hook(preinputhook)

  try:
    inputfunc = raw_input
  except NameError:
    inputfunc = input
  
  oldcompleter = readline.get_completer()
  olddelims = readline.get_completer_delims()

  multiple = kw["multiple"] if "multiple" in kw else None
  
  completer = kw["completer"] if "completer" in kw else None
  if completer is not None and callable(completer.completer) is True:
    if opts is not None and opts.debug is True:
      echo("setting completer function", level="debug")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.completer)
    if multiple is True:
      readline.set_completer_delims(", ")

  while True:
#    signal.signal(signal.SIGALRM, timeouthandler)
#    signal.alarm(timeout)

    prompt = colorclass.Color(prompt)
    try:
      buf = inputfunc(prompt)
    except KeyboardInterrupt:
      echo("INTR")
      raise
    except EOFError:
      echo("EOF")
      raise
    finally:
      print ("\x1b[0m", end="")
#      signal.alarm(0)

    if oldvalue is not None:
      readline.set_pre_input_hook(None)

    if buf is None or buf == "":
      if "noneok" in kw and kw["noneok"] is True:
        return None
      else:
        return oldvalue

    if mask is not None:
      echo(re.match(mask, buf), level="debug")

      if re.match(mask, buf) is None:
        echo("invalid input")
        echo()
        continue

    if multiple is True:
      completions = buf.split(",")
    else:
      completions = [buf]

    completions = [c.strip() for c in completions]

    if "verify" in kw and callable(kw["verify"]):
      verify = kw["verify"]
    else:
      result = buf
      break

    bang = []
    for c in completions:
      bang += c.split(" ")
    completions = bang
    validcompletions = []

    if opts is not None and opts.debug is True:
      echo("inputstring.200: verify is callable", level="debug")

    invalid = 0
    for c in completions:
      if verify(opts, c) is True:
        validcompletions.append(c)
      else:
        echo("%r is not valid" % (c))
        invalid += 1
        continue
    if invalid == 0:
      echo("inputstring.220: no invalid entries, exiting loop")
      result = validcompletions
      break

  readline.set_completer(oldcompleter)
  readline.set_completer_delims(olddelims)

  return result

def inputboolean(prompt, options="YN", default=""):
  ch = accept(prompt, options, default)
  if ch == "Y":
    echo("Yes")
    return True
  elif ch == "T":
    echo("True")
    return True
  elif ch == "N":
    echo("No")
    return False
  elif ch == "F":
    echo("False")
    return False
  return None

#def input(func, prompt, oldvalue, opts=None, completerinstance=None):
#    buf = func(prompt, oldvalue)
#    if "noneok" in opts and opts.noneok is True and (buf is None or buf == ""):
#        return None
#
#    if buf is not None and buf != "":
#        return buf
#
#    return oldvalue

class inputcompleter(object):
  def __init__(self, dbh, opts, table, primarykey):
    self.matches = []
    self.dbh = dbh
    self.opts = opts
    self.table = table
    self.primarykey = primarykey
    echo("ttyio3.inputcompleter.table=%s, .primarykey=%s" % (table, primarykey), level="debug")

  def getmatches(self, text):
    echo("ttyio3.inputcompleter.100: text=%s" % (text), level="debug")
    
    sql = "select %s from %s" % (self.primarykey, self.table)
    if text == "":
        dat = ()
    else:
        sql += " where %s ilike %s" % (self.primarykey)
        dat = (text+"%",)
    cur = self.dbh.cursor()
    try:
      cur.execute(sql, dat)
    except Exception as e:
      echo("ttyio3.inputcompleter.200: e=%s" % (e), level="error")

    res = cur.fetchall()

    foo = []
    for rec in res:
      foo.append(rec[self.primarykey])

    cur.close()
    
    return foo

  def completer(self, text, state):
    # ttyio.echo("completer.100: state=%r text=%r" % (state, text), level="debug")
    
    if state == 0:
      if text:
        self.matches = self.getmatches(text)
      else:
        self.matches = []

    if state < len(self.matches):
      return self.matches[state]
    
    return None

def areyousure(prompt="are you sure?", default="N", options="YN") -> bool:
  res = inputboolean(prompt, default=default, options=options)
  if res is True:
    return 0
  return 1

# @see https://stackoverflow.com/a/53981846
def readablelist(seq: List[Any], color:str="", itemcolor:str="") -> str:
    """Return a grammatically correct human readable string (with an Oxford comma)."""
    seq = [str(s) for s in seq]

    if len(seq) < 3:
      buf = "%s and %s" % (color, itemcolor)
      return buf.join(seq) # " and ".join(seq)

    buf = "%s, %s" % (color, itemcolor)
    return buf.join(seq[:-1]) + '%s, and %s' % (color, itemcolor) + seq[-1]

def settermios(fd):
  pass

# @since 20200917
# not working yet
def detectansi():
  if sys.stdout.isatty() is False:
    return False

  stdinfd = sys.stdin.fileno()

  oldtermios = termios.tcgetattr(stdinfd)
  oldflags = fcntl.fcntl(stdinfd, fcntl.F_GETFL)

  newattr = termios.tcgetattr(stdinfd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(stdinfd, termios.TCSANOW, newattr)

  # fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags)

  os.write(sys.stdout.fileno(), b"\033[6n")

  try:
    res = False
    for x in range(0, 8):
      ch = os.read(stdinfd, 1)
      if ch == b"\033":
        res = True
        break
  finally:
    termios.tcsetattr(stdinfd, termios.TCSAFLUSH, oldtermios)
    fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags)
  return res

# @since 20201013
class genericInputCompleter(object):
  def __init__(self:object, opts:object, tablename:str, primarykey:str):
    self.matches = []
    self.dbh = bbsengine.databaseconnect(opts)
    self.debug = opts.debug
    self.tablename = tablename
    self.primarykey = primarykey

    if self.debug is True:
      ttyio.echo("init genericInputCompleter object", level="debug")

  def getmatches(self, text):
    if self.debug is True:
      ttyio.echo("genericInputCompleter.110: called getmatches()", level="debug")
    sql = "select %s from %s where %s ilike %%s" % (self.primarykey, self.tablename, self.primarykey)
    dat = (text+"%",)
    cur = self.dbh.cursor()
    if self.debug is True:
      ttyio.echo("getmatches.140: mogrify=%r" % (cur.mogrify(sql, dat)), level="debug")
    cur.execute(sql, dat)
    res = cur.fetchall()
    if self.debug is True:
      ttyio.echo("getmatches.130: res=%r" % (res), level="debug")
    matches = []
    for rec in res:
      matches.append(rec[self.primarykey])

    cur.close()

    if self.debug is True:
      ttyio.echo("getmatches.120: matches=%r" % (matches), level="debug")

    return matches

  def completer(self:object, text:str, state):
    if state == 0:
      self.matches = self.getmatches(text)

    return self.matches[state]

if __name__ == "__main__":
  print(accept("[A, B, C, D]", "ABCD", None))
