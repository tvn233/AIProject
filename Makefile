PYTHON ?= python
.PHONY: setup demo eval eval-live test mcp-check
setup:
	$(PYTHON) -m pip install -r requirements.txt

demo:
	$(PYTHON) -m main

eval:
	$(PYTHON) -m scripts.evaluate

eval-live:
	$(PYTHON) -m scripts.evaluate --agent

test:
	$(PYTHON) -m unittest discover -s tests -v

mcp-check:
	$(PYTHON) -m src.mcp.mcp_client
