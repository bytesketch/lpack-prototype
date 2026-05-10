.PHONY: build help clean install

help:
	@echo "=============================================="
	@echo "|          lpack-prototype makefile          |"
	@echo "=============================================="
	@echo "Run 'make setup'   (one-time)."
	@echo "Run 'make build'   to build."
	@echo "Run 'make install' to install"
	@echo "Run 'make clean'   to remove caches and build."

setup:
	@echo "Checking python..."
	@python3 --version
	@echo "Setting up environment..."
	@python -m venv .venv
	@echo "Checking dependencies..."
	@./.venv/bin/python3 -m pip install -r requirements.txt --upgrade pip
	@echo "System ready, now run 'make build' to build app."

build:
	@echo "Building..."
	@./.venv/bin/pyinstaller --name lpack --collect-all rich --collect-all typer src/main.py --noconfirm

clean:
	@echo "Cleaning..."
	@rm -rf build
	@rm -rf dist
	@rm -f *.spec
	@echo "Cleaning successfull."

install:
	@echo "Installing... (sudo needed)"
	@sudo rm -rf /opt/lpack
	@sudo cp -r dist/lpack /opt/
	@sudo rm -f /usr/bin/lpack
	@sudo ln -s /opt/lpack/lpack /usr/bin/lpack
	@echo "Install successful."
