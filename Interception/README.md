# Interception Driver Installation & Setup

## Overview

**Interception** is a low-level, kernel-mode input filter driver for Windows. It operates at the kernel layer (directly interacting with `mouclass.sys` and `kbdclass.sys`), enabling the simulation and capture of real hardware-level mouse and keyboard events.

Unlike standard Windows API calls such as `SendInput`, `mouse_event`, or `keybd_event`, events sent through the Interception driver **do not have the `LLMHF_INJECTED` flag**. To the Windows operating system, browsers, anti-cheat, and detection systems, these inputs appear as physical hardware device inputs.

---

## Directory Structure

```text
Interception/
└── Interception/
    ├── command line installer/        <-- Contains install-interception.exe
    │   ├── install-interception.exe
    │   └── README.md
    ├── library/                       <-- Headers & compiled dynamic libraries (.dll, .lib)
    │   ├── interception.h
    │   ├── x64/
    │   │   ├── interception.dll
    │   │   └── interception.lib
    │   └── x86/
    │       ├── interception.dll
    │       └── interception.lib
    ├── samples/                       <-- Demonstration and diagnostic binaries
    └── licenses/                      <-- License documentation (LGPL v3.0)
```

---

## How to Install the Driver (Step-by-Step)

> **Important:** Installing a kernel driver requires **Administrator privileges** and a **system restart** to take effect.

### Method 1: Automated Installation via Command Prompt

1. Open **Command Prompt** or **PowerShell** as **Administrator**:
   * Press `Win + S`, type `cmd`, right-click **Command Prompt**, and select **Run as administrator**.

2. Navigate to the exact installer directory:
   ```cmd
   cd /d "%USERPROFILE%\Desktop\money needed\Interception\Interception\command line installer"
   ```
   *(Or the relative path from the project root: `cd "Interception\Interception\command line installer"`)*

3. Run the installer:
   ```cmd
   install-interception.exe /install
   ```

4. You will see the confirmation message:
   ```text
   Interception successfully installed. You must reboot for it to take effect.
   ```

5. **Restart your computer**:
   ```cmd
   shutdown /r /t 0
   ```

---

## How to Verify the Driver is Active

After restarting Windows, open a Command Prompt and run:
```cmd
python -c "import interception; interception.auto_capture_devices(); print('Interception driver loaded and working!')"
```
If this prints the success message without errors, the driver is fully active and ready to be used by the automation bots.

---

## How to Uninstall the Driver (If Ever Needed)

1. Open **Command Prompt as Administrator**.
2. Navigate to the installer directory:
   ```cmd
   cd /d "%USERPROFILE%\Desktop\money needed\Interception\Interception\command line installer"
   ```
3. Run the uninstall command:
   ```cmd
   install-interception.exe /uninstall
   ```
4. Restart your computer to complete the driver removal:
   ```cmd
   shutdown /r /t 0
   ```
