# Description: Makefile for the project
CODE_DIR = src

format:
	black $(CODE_DIR)
	isort $(CODE_DIR)

lint:
	black --check $(CODE_DIR)
	isort --check $(CODE_DIR)
