# DeepTracker

DeepTracker is a Windows desktop dashboard for launching remote desktop clients and keeping a local list of recent connection shortcuts. It uses the system's Windows Remote Desktop client or an already installed RustDesk client.

## What it does

- Starts a Windows RDP session for a host you enter.
- Opens RustDesk and copies the peer ID you enter; complete the connection in RustDesk.
- Adds a shortcut to the local sidebar after you launch a connection.
- Checks whether an RDP port can be reached.
- Provides a local task list and dashboard for recent connections.

DeepTracker is a controller dashboard, not a remote agent. Installing it on another PC does not enroll that PC, expose its running apps or files, or start a remote session. RustDesk or Windows Remote Desktop must be configured separately. The remote PC owner must approve RustDesk access; Windows RDP uses Windows account authentication and must be enabled on a supported Windows edition.

This release does not capture screenshots, record screens or audio, access cameras or files, run commands on another PC, install a hidden background service, or start automatically with Windows. Recent connection addresses are stored locally in the current user's application data folder.

## Windows setup

Download `DeepTrackerSetup.exe` from the repository's **Releases** page, run it, and follow the installer. The installer is per-user and does not require administrator privileges. To build locally, use Windows with Python 3.12 and Inno Setup:

```powershell
python -m pip install -r requirements-build.txt
pyinstaller --noconfirm DeepTracker.spec
iscc installer\DeepTracker.iss
```

The finished installer is written to `dist-installer\DeepTrackerSetup.exe`. A GitHub Actions workflow builds the installer on pushes to `main` and when run manually. Tagged builds are published as GitHub Releases.

## Connect to a PC

1. For cross-platform support, install RustDesk from its official site on both PCs. Start RustDesk on the remote PC and get its ID from the person using it.
2. In DeepTracker, choose RustDesk, enter that ID, and select **Connect & Save**. DeepTracker opens RustDesk and copies the ID; finish connecting inside RustDesk.
3. The remote user must accept the session. Keep unattended access disabled unless you have deliberately configured it for your own machine.

For RDP, use **Windows RDP** and a trusted host name or IP. RDP hosting is supported by Windows Pro, Enterprise, Education, and Server editions, and should be protected with Network Level Authentication and a trusted network or VPN.

## Supported platforms

The setup in this repository is for Windows. RustDesk itself supports Windows, macOS, Linux, and Android, but DeepTracker does not install or manage RustDesk on those systems.

## Build automation

Run **Actions → Windows setup → Run workflow** to create a downloadable installer artifact. Push a tag such as `v1.0.0` to publish the generated installer on the repository's Releases page.
