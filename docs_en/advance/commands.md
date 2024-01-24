⚙️ Using Command Line
---

DrissionPage provides some convenient command line commands for basic settings, instead of using temporary configuration files.

The main command for the command line is `dp`, and the format is:

```shell
dp full command name or abbreviation <parameters>
```

## ✅️️ Set Browser Path

| Full Name                | Abbreviation  | Parameters  | Description            |
|:-----------------------:|:-------------:|:-----------:|:---------------------:|
| --set-browser-path | -p                      | browser path | Set the browser path in the configuration file |

**Example:**

```shell
# Full format
dp --set-browser-path D:\chrome\Chrome.exe

# Abbreviated format
dp -p D:\chrome\Chrome.exe
```

## ✅️️ Set User Data Path

| Full Name                | Abbreviation  | Parameters    | Description                |
|:-----------------------:|:-------------:|:-------------:|:-------------------------:|
| --set-user-path    | -u                      | user data folder path | Set the user data path in the configuration file |

**Example:**

```shell
# Full format
dp --set-user-path D:\chrome\user_data

# Abbreviated format
dp -u D:\chrome\user_data
```

## ✅️️ Copy Default INI File to Current Path

| Full Name                    | Abbreviation  | Parameters  | Description                |
|:---------------------------:|:-------------:|:-----------:|:-------------------------:|
| --configs-to-here        | -c                      | None           | Copy the default configuration file to the current path |

**Example:**

```shell
# Full format
dp --configs-to-here

# Abbreviated format
dp -c
```

## ✅️️ Launch Browser

This command is used to launch the browser and wait for the program to take over.

| Full Name                       | Abbreviation  | Parameters  | Description                |
|:------------------------------:|:-------------:|:-----------:|:-------------------------:|
| --launch-browser           | -l                      | port number  | Launch the browser, pass in the port number, where 0 indicates using the value in the configuration file |

**Example:**

```shell
# Full format
dp --launch-browser 9333

# Abbreviated format
dp -l 0
```

