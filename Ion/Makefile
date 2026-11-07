CC := gcc

CFLAGS := -Wall -Wextra -Wpedantic -std=c11 -Ilib
LDFLAGS :=
LDLIBS := -lm -lgpiod

SERVICES := batteryheater logsmain flightmain
SRC_DIR := src/ion/services
LIB_DIR := src/ion/lib
EXAMPLE_DIR := examples
BUILD_DIR := build
BIN_DIR := bin

LIB_SRCS := \
	$(LIB_DIR)/hdc2080.c \
	$(LIB_DIR)/logs.c \
	$(LIB_DIR)/motors.c \
	$(LIB_DIR)/ms5607.c \
	$(LIB_DIR)/stepper.c \
	$(LIB_DIR)/current.c \
	$(LIB_DIR)/thermistor.c

LIB_OBJS := $(patsubst $(LIB_DIR)/%.c,$(BUILD_DIR)/%.o,$(LIB_SRCS))

FLIGHT_OBJ := $(BUILD_DIR)/flightmain.o
BATTERY_OBJ := $(BUILD_DIR)/batteryheater.o
LOGS_OBJ := $(BUILD_DIR)/logsmain.o

EXAMPLE_SRCS := $(wildcard $(EXAMPLE_DIR)/*.c)
EXAMPLE_BINS := $(patsubst $(EXAMPLE_DIR)/%.c,$(BIN_DIR)/%,$(EXAMPLE_SRCS))

.PHONY: all clean rebuild examples directories run test ion-fresh run-ex setup-deps verify-yaml

all: directories \
	$(BIN_DIR)/flightmain \
	$(BIN_DIR)/batteryheater \
	$(BIN_DIR)/logsmain \
	examples

$(BIN_DIR)/flightmain: $(FLIGHT_OBJ) $(LIB_OBJS)
	$(CC) $^ $(LDFLAGS) $(LDLIBS) -o $@

$(BIN_DIR)/batteryheater: $(BATTERY_OBJ) $(LIB_OBJS)
	$(CC) $^ $(LDFLAGS) $(LDLIBS) -o $@

$(BIN_DIR)/logsmain: $(LOGS_OBJ) $(LIB_OBJS)
	$(CC) $^ $(LDFLAGS) $(LDLIBS) -o $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: $(LIB_DIR)/%.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

examples: directories $(LIB_OBJS) $(EXAMPLE_BINS)

$(BIN_DIR)/%: $(EXAMPLE_DIR)/%.c $(LIB_OBJS)
	$(CC) $(CFLAGS) $< $(LIB_OBJS) $(LDFLAGS) $(LDLIBS) -o $@

directories:
	mkdir -p $(BUILD_DIR)
	mkdir -p $(BIN_DIR)

clean:
	rm -rf $(BUILD_DIR)
	rm -f $(BIN_DIR)/*
	rm -rf .venv
	rm -rf dist *.egg-info

rebuild: clean all

run:
	uv sync
	uv run ion

test:
	PYTHONPATH=src uv run python -m unittest discover -s tests

setup-deps:
	@echo "Installing system dependencies..."
	sudo apt-get update && sudo apt-get install -y libyaml-dev

verify-yaml:
	@echo "Verifying PyYAML C-bindings..."
	uv run python -c "import yaml; print('SUCCESS: CLoader found' if hasattr(yaml, 'CLoader') else 'FAILURE: Pure-python YAML installed')"

ion-fresh: setup-deps clean
	$(MAKE) run
	@echo "Forcing PyYAML rebuild to ensure bindings..."
	uv pip install --force-reinstall --no-cache-dir --no-binary=pyyaml pyyaml
	$(MAKE) verify-yaml

run-ex:
	./.run_example.sh $(ex)

.PHONY: install-services uninstall-services

install-services:
	@echo "Installing systemd services..."
	@for service in $(SERVICES); do \
		sudo cp ../systemd-services/$$service.service /etc/systemd/system/; \
	done
	sudo systemctl daemon-reload
	@for service in $(SERVICES); do \
		sudo systemctl enable $$service; \
		sudo systemctl restart $$service; \
	done
	@echo "Services installed and started."

uninstall-services:
	@for service in $(SERVICES); do \
		sudo systemctl stop $$service; \
		sudo systemctl disable $$service; \
		sudo rm -f /etc/systemd/system/$$service.service; \
	done
	sudo systemctl daemon-reload
	@echo "Services removed."
