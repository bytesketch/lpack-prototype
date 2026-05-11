# lpack-prototype

A lightweight experimental Linux packaging system for distributing applications across different Linux distributions using a single portable package format.

---

## What is `lpack`?

`lpack` is a prototype package manager and packaging format built to solve one simple problem:

> Linux app distribution across distros is fragmented and painful.

Different package formats (`.deb`, `.rpm`, `AppImage`, `Flatpak`, `Snap`) all solve parts of the problem, but each comes with trade-offs.

`lpack` is an experimental attempt to create:

- A simple package format
- Easy package building
- Clean installation/removal
- Portable app deployment
- Minimal dependencies
- Simple manifest-based packaging

The package format used is:

```text
.lpk
```

> NOTE: .lpk is basically a .zip with compression-level 9

---

# Features

- Build portable `.lpk` packages
- Install packages locally or system-wide
- Remove installed packages cleanly
- Search installed packages
- Desktop entry support
- Symlink executable management
- Package version upgrade/downgrade detection
- Minimal implementation
- Built entirely in Python

---

# How It Works

`lpack` packages are basically:

1. A compressed archive
2. Containing application files
3. Along with an obfuscated manifest

The builder:

- Reads `manifest.lpack`
- Collects application files
- Generates metadata
- Compresses everything into `.lpk`

The installer:

- Extracts package
- Reads manifest
- Installs files
- Creates symlinks
- Creates desktop entries

The remover:

- Removes installed files
- Removes symlinks
- Removes desktop entries cleanly

---

# Installation

## Requirements

- Python 3.11+
- Linux
- `pip`
- `make`

---

## Clone Repository

```bash
git clone https://github.com/bytesketch/lpack-prototype.git
cd lpack-prototype
```

---

## Setup Environment

```bash
make setup
```

This will:

- Create Python virtual environment
- Install dependencies
- Prepare build environment

---

# Build Binary

```bash
make build
```

Output will be generated in:

```text
dist/
```

---

# Install lpack

```bash
make install
```

System-wide install requires sudo permissions.

---

# Makefile Commands

| Command        | Description              |
| -------------- | ------------------------ |
| `make setup`   | Setup Python environment |
| `make build`   | Build executable         |
| `make install` | Install lpack            |
| `make clean`   | Remove build/cache files |
| `make help`    | Show help menu           |

---

# CLI Usage

## Build Package

```bash
lpack build .
```

or

```bash
lpack build /path/to/project
```

### Silent Mode

```bash
lpack build . --silent
```

---

## Install Package

### User Install

```bash
lpack install app.lpk
```

### System-wide Install

```bash
sudo lpack install app.lpk --system-wide
```

---

## Remove Package

### User Package

```bash
lpack remove my-package
```

### System-wide Package

```bash
sudo lpack remove my-package --system-wide
```

---

## Search Installed Packages

### List Packages

```bash
lpack search
```

### Inspect Package

```bash
lpack search my-package
```

> NOTE: If want to find system-wide installed lpk search do add `--system-wide`. Default is local install.

---

# Package Manifest

`manifest.lpack`

Example:

```json
{
  "package": {
    "name": "My App",
    "package": "my-app",
    "version": "1.0.0",
    "authors": ["yourname"]
  },

  "build_path": "dist/my-app",
  "description": "Example lpack application",

  "app": {
    "binary": "bin/my-app",
    "entry": "myapp"
  },

  "desktop": {
    "name": "My App",
    "icon": "res/icon.png",
    "exec": "my-app --gui"
  },

  "include": {
    "README.md": "docs/README.md"
  }
}
```

---

# Goals

- Simplicity
- Minimalism
- Cross-distro portability
- Easy developer workflow
- Clean package management
- Fully scriptable

---

# Limitations

This is currently a prototype.

Current limitations include:

- No dependency resolution
- No remote repositories
- No package signing
- No sandboxing
- No delta updates
- No automatic updates
- No rollback support

---

# Tech Stack

- Python
- Typer
- Rich
- PyInstaller

---

# Why I Built This

I wanted to experiment with solving Linux application distribution in a simpler way.

This project was mainly built as:

- A systems programming experiment
- A packaging format prototype
- A Linux tooling project
- A learning experience

---

# Examples

For example purpose, I have bundled VSCode's all official 3 variants as .lpk in [release-'example-LPKs'](https://github.com/bytesketch/lpack-prototype/releases/tag/example-LPKs).

You can test it by doing

```bash
sudo lpack install VSCode-1778006632-x64.lpk --system-wide
```

> NOTE: All rights of the inner part of VSCode is owned by Microsoft. And I do not claim it as my property. \
> If [microsoft](https://github.com/microsoft) wants to remove it, they can open issue. I'll do that cleanly.

---

# Contributing

Contributions, ideas, and experiments are welcome.

Feel free to:

- Open issues
- Suggest improvements
- Fork the project
- Test on different distros

---

# License

MIT License. See [LICENSE](LICENSE) for full info.

---

# Author

Ali Ahmad [@bytesketch](https://www.github.com/bytesketch)

Built with Python and Linux curiosity.
