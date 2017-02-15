kb_font_size = 200
kb_shape = (2,4) # row, col
kb_version = 2
'''1=dynamic keyboard, 2=static position, time-based selection, 3=max spacing layout, time-based selection,
4=SVM classification (not complete), 5=single key, visual feedback, 6=3 key layout, 7=single key, audio feedback
'''
kb_uniform_selection = 1 # 1 = uniform selection time for each letters

console_font_size = 20
dict_path = '../../dict/'
dict_filename = 'sample_dict.txt'
selection_allowed = 1 # 0 = disabled letter selection, 1 = enable letter selection
input_device = 0 # 0 = mouse, 1 = eye tracker
filter_window_size = 5 # effectively no filter when filter_window_size = 1
dynamic_screen = 1 # 0 = static screen (no function boxes), 1 = dynamic screen (function boxes)
keep_coordinates_log = 0 # 0 = no log kept, 1 = log kept
log_name = 'eye_coordinates.txt'
calibrate = False
collect_data = False
calibration_hold_time = 20 # seconds
mouselight_radius = 10
dc_dx = 100 # data collection x offset from edges
dc_dy = 100 # data collection y offset from edges
cal_letter = 'v'
SVM_window_size = 10
SVM_model_type = 1 # 1 = linear, 2 = rbf, 3 = poly, 4 = Linear2

selection_mechanism = 'blink' # valid entries are 'blink' or 'time' (only enabled for 2 key layout)
selection_delay = 1 # seconds
pre_audio_buffer = 1 # seconds
off_screen_threshold = selection_delay + 1 # seconds
only_open = True # when true, only count on-screen time
border_filter_offset = 30 # Defines valid places on screen. Offset is # of pixels in from physical screen edges (0 valid).
border_filter_enabled = True # When enabled, filters off screen points, otherwise off screen counted as blink

if selection_allowed == 1:
	letter_selection_radius = 110
else:
	letter_selection_radius = 0

if (kb_version == 7):
	filter_window_size = 1
if (kb_version == 3 and selection_mechanism == 'blink'):
	filter_window_size = 2

# Over-write standard settings with user settings
try:
    from user_settings import *
except ImportError:
    # No user settings defined, this is fine
    pass