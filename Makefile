LIVT ?= livt

.PHONY: sync test test-integration test-workspace test-workspace-integration test-workspace-iterators test-tools

sync:
	$(LIVT) sync --project "$(CURDIR)"

test:
	LIVT="$(LIVT)" bash ci/test-standard-library.sh

test-integration: sync
	mkdir -p "$(CURDIR)/.livt/reports/standard-library"
	$(LIVT) test --project "$(CURDIR)" --junit "$(CURDIR)/.livt/reports/standard-library/Livt.xml"

# Snapshot all sibling libraries; released dependency pins are never modified.
test-workspace:
	LIVT="$(LIVT)" python3 ci/test-workspace.py $(WORKSPACE_ARGS)

test-workspace-integration:
	LIVT="$(LIVT)" python3 ci/test-workspace.py --integration-only $(WORKSPACE_ARGS)

test-tools:
	python3 -m unittest discover -s ci -p 'test_*.py'

test-workspace-iterators:
	LIVT="$(LIVT)" python3 ci/test-workspace.py --iterators-only $(WORKSPACE_ARGS)

.PHONY: test-workspace-memory
test-workspace-memory:
	LIVT="$(LIVT)" python3 ci/test-memory.py $(WORKSPACE_ARGS)
