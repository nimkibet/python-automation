# Interception Command Line Installer

This directory contains the official **`install-interception.exe`** binary used to register and bind the Interception kernel-mode filter driver to Windows device stacks.

---

## Exact File Location
- **Executable:** `install-interception.exe`
- **Full Path:** `Interception\Interception\command line installer\install-interception.exe`

---

## Step-by-Step Installation Instructions

### 1. Open an Elevated Command Prompt
* Press the **Windows Key**.
* Type **`cmd`**.
* Right-click **Command Prompt** and choose **"Run as administrator"**.

### 2. Run the Installer
In your Administrator Command Prompt, navigate directly to this folder:
```cmd
cd /d "%~dp0"
```
*(Or navigate using the full path)*:
```cmd
cd /d "%USERPROFILE%\Desktop\money needed\Interception\Interception\command line installer"
```

Execute the installation command:
```cmd
install-interception.exe /install
```

### 3. Expected Output
```text
Interception successfully installed. You must reboot for it to take effect.
```

### 4. Reboot Windows (Required)
The driver will only bind to hardware ports (`kbdclass.sys` and `mouclass.sys`) upon system boot.
Reboot your machine immediately:
```cmd
shutdown /r /t 0
```

---

## Uninstallation Instructions
If you ever need to remove the driver:
```cmd
install-interception.exe /uninstall
shutdown /r /t 0
```
