kb_font_size = 250
kb_shape = (1,4) # row, col
kb_version = 2 # 1=dynamic keyboard, 2=static position, time-based selection

console_font_size = 150
dict_path = '../../dict/'
dict_filename = 'sample_dict.txt'
selection_allowed = 1 # 0 = disabled letter selection, 1 = enable letter selection
input_device = 0 # 0 = mouse, 1 = eye tracker
filter_window_size = 5 # effectively no filter when filter_window_size = 1
dynamic_screen = 1 # 0 = static screen (no function boxes), 1 = dynamic screen (function boxes)
keep_coordinates_log = 1 # 0 = no log kept, 1 = log kept
log_name = 'eye_coordinates.txt'

selection_delay = 10
if selection_allowed == 1:
	letter_selection_radius = 110
else:
	letter_selection_radius = 0