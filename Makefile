
TARGET = 

# Place your Arduino libs here! It's okay to not define this.
#ARDUINO_LIBS = SoftwareSerial

# Either set this here or type `make upload BOARD_TAG=uno`
BOARD_TAG = mega2560 

# if there is a ARDUINO_UA_ROOT environment variable, it defines the
# root of the arduino_ua install.  If not, we assume it is in HOME
ifndef ARDUINO_UA_ROOT
  ARDUINO_UA_ROOT=$(HOME)
endif
include $(ARDUINO_UA_ROOT)/arduino-ua/mkfiles/ArduinoUA.mk

# Remember to `make clean` before `make upload`ing on a different type
# of board.

# You can also define DEBUG and other symbols like that here
DEFINITIONS = 
DEFINES := ${DEFINITIONS:%=-D%}

# Define your compiler flags. Remember to `+=` the rule.
#CFLAGS += -Wall -Werror -std=c99
#CXXFLAGS += -Wall -Werror
CPPFLAGS += $(DEFINES)

# load the bigger math library so you can printf floats.
LDFLAGS += -Wl,-u,vfprintf -lprintf_flt -lm
