# -*- coding: UTF-8 -*-
import builtins as bi
from prompt_toolkit import print_formatted_text
from sploitkit import *


bi.print_formatted_text = print_formatted_text
bi.Command = Command
bi.Config = Config
bi.FrameworkConsole = FrameworkConsole
bi.Module = Module
bi.Option = Option
bi.Path = Path

