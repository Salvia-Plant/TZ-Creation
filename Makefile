VERSION_FILE := app/version.json

.PHONY: version

$(VERSION_FILE) version:
	@printf '{\n "branch": "%s", \n "commit": "%s", \n "date": "%s",\n "tag": "%s"\n}\n'\
	"$$(git rev-parse --abbrev-ref HEAD)" \
	"$$(git rev-parse --short HEAD)" \
	"$$(git log -1 --format=%cI)" \
	"$$(git describe --tags --always --abbrev=0)" > $(VERSION_FILE)