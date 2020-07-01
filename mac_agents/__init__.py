__all__ = ['read', 'write', 'update', 'Agent', 'create', 'jobs']


try:
    import importlib
except ImportError:
    import imp
import inspect
import mac_colors
import os
import plistlib
import subprocess
import sys

LOGS = os.path.join(os.environ["HOME"], "Library/Logs/LaunchAgents")


def read(path):
    """return a dictionary with plist file data"""
    if hasattr(plistlib, "load"):
        return plistlib.load(open(path, 'rb'))
    return plistlib.readPlist(path)


def write(path, data):
    """write data dictionary to a plist file"""
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    data = {k: v for k, v in data.items() if v is not None}
    if hasattr(plistlib, "dump"):
        plistlib.dump(data, open(path, 'wb'))
    else:
        plistlib.writePlist(data, path)


def update(path, **kwargs):
    """update plist file data"""
    old = dict(read(path))
    new = dict(old)
    new.update(kwargs)
    new = {k: v for k, v in new.items() if v}
    if old != new:
        write(path, new)


def load_source(name, path):
    try:
        return importlib.machinery.SourceFileLoader(name, path).load_module()
    except NameError:
        return imp.load_source(name, path)


class Job:
    """launchctl Job class. attrs: `pid`, `status`, `label`"""
    string = None
    pid = None
    status = None
    label = None

    def __init__(self, string):
        self.parse(string)

    def parse(self, string):
        self.string = string
        values = list(filter(None, string.split()))
        self.pid = (int(values[0]) if values[0] != "-" else None)
        self.status = (int(values[1]) if values[1] != "-" else None)
        self.label = values[2]

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.__str__()


"""
predefined keys:
label (Label)
args (ProgramArguments)
stdout (StandardOutPath)
stderr (StandardErrorPath)
"""


class Agent:
    """launchd.plist generator. Capital letter attrs/props as launchd.plist keys"""
    __readme__ = ["create", "rm", "read", "write", "update", "load", "unload"] + ["script", "path",
                                                                                  "Label", "ProgramArguments", "StandardOutPath", "StandardErrorPath", "WorkingDirectory"]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)

    def data(self):
        result = dict()
        for key, value in inspect.getmembers(self):
            if key[0] != "_" and key[0] == key[0].upper() and (bool(value) or value == 0):
                result[key] = value
        return result

    def create(self):
        """create launchd.plist file and `StandardOutPath`, `StandardErrorPath` logs"""
        self.write(self.data())
        for key in ["StandardOutPath", "StandardErrorPath"]:
            path = getattr(self, key, None)
            if path and not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
        return self

    def read(self):
        """return a dictionary with plist file data"""
        return read(self.path)

    def write(self, data):
        """write a dictionary to a plist file"""
        write(self.path, data)
        return self

    def keys(self):
        """return a list of all the keys in the plist dictionary"""
        return self.read().keys()

    def get(self, key, default=None):
        """return the value for key if key is in the plist dictionary, else default"""
        return self.read().get(key, default)

    def update(self, **kwargs):
        """update plist file data"""
        update(self.path, **kwargs)
        return self

    def disable(self):
        """set `Disabled` to true"""
        self.update(Disabled=True)
        return self

    def enable(self):
        """set `Disabled` to false"""
        self.update(Disabled=False)
        return self

    def load(self):
        """`launchctl load` plist file"""
        args = ["launchctl", "load", self.path]
        subprocess.check_call(args, stderr=subprocess.PIPE)
        return self

    def unload(self):
        """`launchctl unload` plist file"""
        args = ["launchctl", "unload", self.path]
        subprocess.check_call(args, stderr=subprocess.PIPE)
        return self

    def rm(self):
        """remove plist file (if exist)"""
        path = self.path
        if os.path.exists(path):
            os.unlink(path)
        return self

    @property
    def Label(self):
        """path.to.file.py"""
        if hasattr(self, "_label"):
            return getattr(self, "_label")
        path = self.script
        start = os.path.join(os.environ["HOME"], "Library/LaunchAgents")
        path = os.path.relpath(self.script, start)
        return ".".join(filter(None, path.split("/")))

    @Label.setter
    def Label(self, label):
        self._Label = label

    @property
    def Disabled(self):
        if getattr(self, "disabled", None):
            return getattr(self, "disabled", None)
        return os.path.splitext(self.script)[1] == ".sh"

    @Disabled.setter
    def Disabled(self, value):
        self.disabled = value

    @property
    def StartInterval(self):
        return getattr(self, "interval", None)

    @StartInterval.setter
    def StartInterval(self, interval):
        self.interval = interval

    @property
    def StartCalendarInterval(self):
        return getattr(self, "calendar", None)

    @StartCalendarInterval.setter
    def StartCalendarInterval(self, data):
        self.calendar = dict(data)

    @property
    def WorkingDirectory(self):
        """script file dirname"""
        if getattr(self, "_WorkingDirectory", None):
            return getattr(self, "_WorkingDirectory")
        return os.path.dirname(self.script)

    @WorkingDirectory.setter
    def WorkingDirectory(self, path):
        self._WorkingDirectory = str(path)

    @property
    def ProgramArguments(self):
        """['bash','-l','-c','python $script $plist']"""
        if hasattr(self, "_ProgramArguments"):
            return self._ProgramArguments
        """
`bash -l` load environment variables
        """
        script = self.script if " " not in self.script else '"%s"' % self.script
        plist = self.path if " " not in self.path else '"%s"' % self.path
        if os.path.splitext(self.script)[1] == ".py":
            return ["bash", "-l", "-c", 'python %s %s' % (script, plist)]
        if os.path.splitext(self.script)[1] == ".sh":
            return ["bash", "-l", script, plist]
        raise ValueError(self.script)

    @ProgramArguments.setter
    def ProgramArguments(self, args):
        self.args = list(args)

    @property
    def StandardOutPath(self):
        """`~/Library/Logs/LaunchAgents/$Label/out.log`"""
        if getattr(self, "_StandardOutPath", None):
            return self._StandardOutPath
        return os.path.join(LOGS, self.Label, "out.log")

    @StandardOutPath.setter
    def StandardOutPath(self, path):
        self.stdout = str(path)

    @property
    def StandardErrorPath(self):
        """`~/Library/Logs/LaunchAgents/$Label/err.log`"""
        if getattr(self, "_StandardErrorPath", None):
            return self._StandardErrorPath
        return os.path.join(LOGS, self.Label, "err.log")

    @StandardErrorPath.setter
    def StandardErrorPath(self, path):
        self.stderr = str(path)

    @property
    def path(self):
        """plist path - `file.py.plist`"""
        if hasattr(self, "_path"):
            return self._path
        return "%s.plist" % self.script

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def script(self):
        """script path - class module file"""
        if getattr(self, "_script", None):
            return getattr(self, "_script")
        return sys.modules[self.__class__.__module__].__file__

    @script.setter
    def script(self, path):
        self._script = path

    def __str__(self):
        return "<Agent %s>" % str(self.data)

    def __repr__(self):
        return "<Agent %s>" % str(self.Label)


def create(path):
    """create launchd.plist from python file and return plist path"""
    path = os.path.abspath(os.path.expanduser(path))
    cli = False
    if os.path.splitext(path)[1] == ".py":
        for line in open(path).read().splitlines():
            if "__name__" in line and "__main__" in line and line == line.lstrip():
                cli = True
        if not cli:
            print('SKIP: if __name__ == "__name__" line NOT FOUND (%s)' % path)
            return
        sys.path.append(os.path.dirname(path))
        module = load_source(path, path)
        classes = []
        for k, v in module.__dict__.items():
            if inspect.isclass(v) and issubclass(v, Agent):
                classes.append(v)
        if not len(classes):
            print("SKIP: mac_agents.Agent subclass NOT FOUND (%s)" % path)
        if len(classes) != 1:
            print("SKIP: %s mac_agents.Agent subclasses %s (%s)" %
                  (len(classes), classes, path))
        agent = classes[0]()
    if os.path.splitext(path)[1] == ".sh":
        agent = Agent()
    agent.script = path
    agent.create()
    return agent.path


def jobs():
    """return a list of launchctl Job objects (`pid`, `status`, `label`)"""
    result = []
    out = os.popen("launchctl list").read()
    rows = out.splitlines()[1:]
    for row in rows:
        job = Job(row)
        if os.path.splitext(job.label)[1] == ".py":
            result.append(job)
    return result
