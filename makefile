.PHONY: build help clean install

help:
	@echo "|==========================================================|"
	@echo "|          lpack-prototype makefile                        |"
	@echo "|==========================================================|"
	@echo "| Run 'make setup'   (one-time).                           |"
	@echo "| Run 'make build'   to build.                             |"
	@echo "| Run 'make install' to install                            |"
	@echo "| Run 'make clean'   to remove caches and build.           |"
	@echo "|----------------------------------------------------------|"
	@echo "| Run 'make build install' after setup. (one-line command) |"
	@echo "|==========================================================|"

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
	@rm -rf lpack
	@rm -rf ./*/*/__pycache__
	@rm -rf ./*/__pycache__
	@echo "Cleaning successful."

install:
	@echo "Installing... (sudo needed)"
	@./.venv/bin/python3 src/main.py build
	@sudo ./.venv/bin/python src/main.py install lpack/build/lpack-1.0-prototype.lpk --system-wide
