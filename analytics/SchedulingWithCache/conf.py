MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB
PB = 1024 * TB

# job processing related constants
JOB_START_DELAY = 1
STEP = 600
MAX_CES_PER_TASK = 99
CORE_NUMBERS = [1, 4, 6, 8, 10, 12, 16, 24, 32, 48, 64, 128]

# cache related constants
CACHE_TB_PER_1K = 20
LWM = 0.90
HWM = 0.95
PER_FILE_RATE = GB / 8 / 3  # one Gbps
THROUGHPUT_BIN = 1800  # in seconds
PER_FILE_RATE *= THROUGHPUT_BIN

# emulation options
PERIODS = ['SEP', 'OCT', 'NOV', 'DEC']  # must be listed in order
KINDS = ['prod']  # anal
DONT_CACHE = []

BASE_DIR = 'analytics/SchedulingWithCache/'
TITLE = 'fast'
STEPS_TO_FILE = True
BINS = 1800  # this is bin width in seconds. Only for printouts and plotting.
