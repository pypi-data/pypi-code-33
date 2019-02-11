from pygame.locals import *

def get_key_value( key_code ):
    """ Lookup dictionaries of keyboard codes """
    number = { 
        K_0 : "0", K_1 : "1", K_2 : "2", K_3 : "3", K_4 : "4", K_5 : "5", K_6 : "6", K_7 : "7", K_8 : "8", K_9 : "9" }
    alpha = { 
        K_a : "a", K_b : "b", K_c : "c", K_d : "d", K_e : "e", K_f : "f", K_g : "g", K_h : "h", K_i : "i", K_j : "j", K_k : "k", K_l : "l", K_m : "m", K_n : "n", K_o : "o", K_p : "p", K_q : "q", K_r : "r", K_s : "s", K_t : "t", K_u : "u", K_v : "v", K_w : "w", K_x : "x", K_y : "y", K_z : "z" }
    special = { 
        K_SPACE : " ", K_LEFT : "LEFT", K_RIGHT : "RIGHT", K_UP : "UP", K_DOWN : "DOWN", K_RETURN : "ENTER", K_LALT : "ALT", K_RALT : "ALT", K_LCTRL : "CTRL", K_RCTRL : "CTRL", K_LSHIFT : "SHIFT", K_RSHIFT : "SHIFT", K_DELETE : "DELETE" }
    all_keys = { 
        **number, **alpha, **special }
    if key_code in all_keys:
        return all_keys[key_code]
    else:
        return None

