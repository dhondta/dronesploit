# -*- coding: UTF-8 -*-
from sploitkit import *
from tinyscript.helpers import is_iterable
from yaml import dump


class State(Command):
    """ Display console's shared state """
    requirements = {'config': {'DEBUG': True}}
    
    def run(self):
        self.console.root.interfaces
        for k, v in self.console.state.items():
            print_formatted_text("\n{}:".format(k))
            v = v or ""
            if len(v) == 0:
                continue
            if is_iterable(v):
                if isinstance(v, dict):
                    v = dict(**v)
                for l in dump(v).split("\n"):
                    if len(l.strip()) == 0:
                        continue
                    print_formatted_text("  " + l)
            else:
                print_formatted_text(v)
        print_formatted_text("")

