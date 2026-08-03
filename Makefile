LIVT ?= livt

.PHONY: sync test test-integration

sync:
	$(LIVT) sync --project "$(CURDIR)"

test:
	LIVT="$(LIVT)" bash ci/test-standard-library.sh

test-integration: sync
	mkdir -p "$(CURDIR)/.livt/reports/standard-library"
	$(LIVT) test --project "$(CURDIR)" --junit "$(CURDIR)/.livt/reports/standard-library/Livt.xml"
