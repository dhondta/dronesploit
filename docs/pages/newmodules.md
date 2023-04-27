# New Modules

## 1. Check for available modules

First, check that what you're trying to achieve is not already implemented in an [existing module](https://github.com/dhondta/dronesploit/tree/master/dronesploit/_src/modules).

## 2. Is it WiFi- or radio-controlled ?

This will condition the machinery you will need to implement your new module.

## 3. Check for available features

This machinery is at the [root of the package](https://github.com/dhondta/dronesploit/tree/master/dronesploit). Its structure is logically made:

- `drones`: this folder is for specific drone-related features
- `radio`: this folder is reserved for radio features
- `wifi`: this folder is reserved for WiFi features (connection, deauthentication, scanning)

## 4. Prototype a script

In order to integrate your work to DroneSploit, you will need to test it first. It is advised to script your interaction/attack on your drone and to test it before writing your module.

Be sure to split what is speficic to:

- The **technology**, i.e. WiFi or radio signals ; this is generic and could serve for various modules (e.g. [mixins](https://github.com/dhondta/dronesploit/blob/master/dronesploit/wifi/mixin.py)).
- A particular **brand** of drone ; this could serve for multiple modules and this will go into the `drones` folder (e.g. [Hobbico](https://github.com/dhondta/dronesploit/blob/master/dronesploit/drones/hobbico.py)),
- A **model** of drone (e.g. [C-Me](https://github.com/dhondta/dronesploit/blob/master/dronesploit/_src/modules/exploit/hobbico/cme.py)).

This way, the integration will be straightforward and you will avoid losses of time and reinventing the wheel.

## 5. Contribute to DroneSploit

From this point, the different parts of the prototype script can now be integrated into DroneSploit.

- **Technology**: This part is to put in `radio`, `wifi`, ... depending on what is already implemented or what could be modified/improved. For WiFi, be sure to include a [regular expression in the drone filter](https://github.com/dhondta/dronesploit/blob/master/dronesploit/wifi/drone.py), that is, in the `DRONE_REGEX` constant. Note that, if technology-specific modules are worth adding, these can be put into the [`auxiliary` category folder](https://github.com/dhondta/dronesploit/tree/master/dronesploit/_src/modules/auxiliary/) (e.g. [`auxiliary/wifi/wpa2psk_crack`](https://github.com/dhondta/dronesploit/blob/master/dronesploit/_src/modules/auxiliary/wifi/crack.py)).
- **Brand**: This part typically contains proxy `Module`-inherited classes (see example in [`hobbico.py`](https://github.com/dhondta/dronesploit/blob/master/dronesploit/drones/hobbico.py)) to be added to the existing or created into a new brand-named subpackage.
- **Model**: This part will be split by module or by group of related modules in files under the [`_src` folder](https://github.com/dhondta/dronesploit/tree/master/dronesploit/_src).

!!! note "Use of `Module` class attributes"
    
    When writing modules, the following class attributes can be used (see [this example](https://github.com/dhondta/dronesploit/blob/master/dronesploit/_src/modules/auxiliary/wifi/crack.py)):
    
    - `config`: for adding module configuration options
    - `path`: for setting the path to the module from within the CLI (e.g. the source file could be `commands/my-drone/model` with a module named `MyFirstModule` ; without `path` set, it would give `commands/my-drone/model/my_first_module`, but the path can be overriden to get for instance `commands/others/my_first_module` by setting `path="commands/others"`)
    - `requirements`: this dictionary allows to set requirements that will prevent the module from being used if some are not met (multiple keys can be used to set lists of granular requirements, i.e. `python` for checking that a Python package is installed, or `system` for checking that a CLI tool exists)
    
    Be sure to define enough requirements.

