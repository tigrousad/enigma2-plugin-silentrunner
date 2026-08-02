# SilentRunner – IPK packaging Makefile
#
# Usage (on any Linux system with Python 3 available):
#
#   make icons      – generate icon PNGs (run this first)
#   make ipk        – create silentrunner_1.0.0_all.ipk
#   make clean      – remove build artefacts
#
# The resulting .ipk can be installed on your receiver via:
#   opkg install silentrunner_1.0.0_all.ipk

PLUGIN_DIR   = /usr/lib/enigma2/python/Plugins/Extensions/SilentRunner
PACKAGE_NAME = enigma2-plugin-extensions-silentrunner
VERSION      = 1.0.0
ARCH         = all
IPK_NAME     = $(PACKAGE_NAME)_$(VERSION)_$(ARCH).ipk
BUILD_DIR    = /tmp/silentrunner_build

.PHONY: all icons ipk clean

all: icons ipk

icons:
	@echo "Generating icons..."
	cd ../icons && python3 make_icons.py
	@echo "Icons generated."

ipk: icons
	@echo "Building IPK: $(IPK_NAME)"

	# Clean and create build tree
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)$(PLUGIN_DIR)
	mkdir -p $(BUILD_DIR)/CONTROL

	# Copy plugin source files
	cp ../__init__.py   $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../plugin.py     $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../main.py       $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../runner.py     $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../explorer.py   $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../widgets.py    $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../skin.py       $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../utils.py      $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../version.py    $(BUILD_DIR)$(PLUGIN_DIR)/
	cp ../plugin.png    $(BUILD_DIR)$(PLUGIN_DIR)/

	# Copy icons/
	mkdir -p $(BUILD_DIR)$(PLUGIN_DIR)/icons
	cp ../icons/*.png   $(BUILD_DIR)$(PLUGIN_DIR)/icons/

	# Copy locale/
	mkdir -p $(BUILD_DIR)$(PLUGIN_DIR)/locale
	# (no .mo files in this release)

	# Control file
	cp CONTROL $(BUILD_DIR)/CONTROL/CONTROL

	# Build .ipk (ar archive of three members)
	cd $(BUILD_DIR) && \
		tar czf ./data.tar.gz   --owner=root --group=root -C . \
			$(subst /,,$(PLUGIN_DIR:/%=%)) && \
		echo "2.0" > ./debian-binary && \
		tar czf ./control.tar.gz --owner=root --group=root -C CONTROL . && \
		ar rcs $(IPK_NAME) debian-binary control.tar.gz data.tar.gz

	cp $(BUILD_DIR)/$(IPK_NAME) .
	@echo ""
	@echo "Done: packaging/$(IPK_NAME)"
	@echo ""
	@echo "Install on your receiver:"
	@echo "  opkg install $(IPK_NAME)"

clean:
	rm -rf $(BUILD_DIR)
	rm -f  *.ipk
