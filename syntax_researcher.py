import ctypes
import os
import sys
import tkinter as tk
import dearpygui.dearpygui as dpg
from Cpp_library import cpp_library
import textwrap
import time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
dpg.create_context()

root = tk.Tk()
user_width = root.winfo_screenwidth()
user_height = root.winfo_screenheight()
root.destroy()

DESIGN_WIDTH = 1920.0
DESIGN_HEIGHT = 1080.0

ratio_x = user_width / DESIGN_WIDTH
ratio_y = user_height / DESIGN_HEIGHT



def scale_x(val):
    return int(val * ratio_x)

def scale_y(val):
    return int(val * ratio_y)
viewport_w = scale_x(600)
viewport_h = scale_y(400)


dpg.create_viewport(title="Cpp Syntax Researcher", width=viewport_w, height=viewport_h)

try:
    dpg.set_viewport_small_icon("Cppguide.ico")
    dpg.set_viewport_large_icon("Cppguide.ico")
except Exception as e:
    print(f"Could not set icon: {e}")
dpg.show_viewport()

dpg.setup_dearpygui()

calculated_height = 0

def button_callback(ID, Nothing, user_data):
    dpg.delete_item("results_container", children_only=True)
    dpg.delete_item("lines_container", children_only=True)
    concept_data = cpp_library.get(user_data)
    
    pos = [scale_x(575), scale_y(35)]
    
    glow = dpg.add_text(
        f"---{user_data}---", 
        pos=[pos[0] + scale_x(2), pos[1] + scale_y(1)], 
        color=[255, 50, 255, 255], 
        parent="results_container"
    )
    
    title = dpg.add_text(f"---{user_data}---", pos=pos, color=[255, 50, 255, 255], parent="results_container")
    
    dpg.bind_item_font(title, big_bold_font)
    dpg.bind_item_font(glow, big_bold_font)

    dpg.add_spacer(height=scale_y(20), parent="results_container")

    syntax_lines = concept_data["syntax"].split("\n")
    desc_lines = concept_data["desc"].split("\n")
    
    max_chars = max(len(line) for line in syntax_lines) if syntax_lines else 0
    total_lines = len(syntax_lines)
    
    dynamic_width = max(scale_x(150), (max_chars * scale_x(9)) + scale_x(30)) 
    dynamic_height = max(scale_y(50), (total_lines * scale_y(20)) + scale_y(30))

    COLOR_DEFAULT = [220, 220, 224, 255]
    COLOR_TITLE = [230, 219, 116, 255]
    COLOR_KEYWORD = [255, 146, 43, 255]
    COLOR_STRING = [31, 255, 166, 255]
    COLOR_COMMENT = [128, 128, 128, 255]
    COLOR_PREPROCESSOR = [198, 120, 221, 255]
    COLOR_LITERAL = [230, 219, 116, 255]

    KEYWORDS = {
        "alignas", "alignof", "auto", "bool", "break", "case", "catch",
        "char", "char8_t", "char16_t", "char32_t", "class", "const",
        "consteval", "constexpr", "constinit", "const_cast", "continue",
        "co_await", "co_return", "co_yield", "decltype", "default",
        "delete", "do", "double", "dynamic_cast", "else", "enum",
        "explicit", "export", "extern", "float", "for", "friend", "goto",
        "if", "inline", "int", "long", "mutable", "namespace", "new",
        "noexcept", "nullptr", "operator", "private", "protected",
        "public", "register", "reinterpret_cast", "requires", "return",
        "short", "signed", "sizeof", "static", "static_assert",
        "static_cast", "struct", "switch", "template", "this",
        "thread_local", "throw", "try", "typedef", "typeid", "typename",
        "union", "unsigned", "using", "virtual", "void", "volatile",
        "wchar_t", "while"
    }

    LITERALS = {"true", "false", "nullptr"}
    def draw_cpp_line(line):
        i = 0

        while i < len(line):

            if line.startswith("//", i):
                item = dpg.add_text(line[i:], color=COLOR_COMMENT)
                dpg.bind_item_font(item, code_font)
                break
                
            if line[i] == "#":
                item = dpg.add_text(line[i:], color=COLOR_PREPROCESSOR)
                dpg.bind_item_font(item, code_font)
                break

                # String or character: "hello" or 'A'
            if line[i] == '"' or line[i] == "'":
                quote = line[i]
                start = i
                i += 1
                escaped = False

                while i < len(line):
                    if line[i] == quote and not escaped:
                        i += 1
                        break

                    if line[i] == "\\" and not escaped:
                        escaped = True
                    else:
                        escaped = False

                    i += 1

                item = dpg.add_text(line[start:i], color=COLOR_STRING)
                dpg.bind_item_font(item, code_font)
                continue

                # Word: int, return, class, variableName...
            if line[i].isalpha() or line[i] == "_":
                start = i
                i += 1

                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    i += 1

                word = line[start:i]

                if word in LITERALS:
                    color = COLOR_LITERAL
                elif word in KEYWORDS:
                    color = COLOR_KEYWORD
                else:
                    color = COLOR_DEFAULT

                item = dpg.add_text(word, color=color)
                dpg.bind_item_font(item, code_font)
                continue

                # Normal character: spaces, brackets, operators, numbers, etc.
            item = dpg.add_text(line[i], color=COLOR_DEFAULT)
            dpg.bind_item_font(item, code_font)
            i += 1

    syntax_x = scale_x(575) - ((len(f"---{user_data}---") + 6) * scale_x(22)) / 2
    syntax_y = scale_y(100)
        
    syntax = dpg.add_text("SYNTAX:", color=COLOR_TITLE, pos=[syntax_x, syntax_y], parent="results_container")
    dpg.bind_item_font(syntax, BIGcode_font)
        
    group_x = scale_x(575) - ((len(f"---{user_data}---") + 6) * scale_x(22)) / 2
    group_y = scale_y(150)
        
    with dpg.group(pos=[group_x, group_y], parent="results_container"):
        with dpg.child_window(width=dynamic_width, height=dynamic_height, no_scrollbar=True) as code_box:
            for line in syntax_lines:
                with dpg.group(horizontal=True, horizontal_spacing=1):
                        draw_cpp_line(line)
                        
                            
        dpg.bind_item_theme(code_box, code_box_theme)

        desc_y = dynamic_height + scale_y(200)
        description = dpg.add_text("DESCRIPTION:", color=COLOR_TITLE, pos=[group_x, desc_y], parent="results_container")
        dpg.bind_item_font(description, BIGcode_font)
        
        current_line_y = dynamic_height + scale_y(240) 
        line_spacing = scale_y(22) 
        
        for paragraph in desc_lines:
           
            wrapped_chunks = textwrap.wrap(paragraph, width=150)
            
            if not wrapped_chunks:
                current_line_y += line_spacing
                continue
                
            for chunk in wrapped_chunks:
                with dpg.group(horizontal=True, horizontal_spacing=1, pos=[group_x, current_line_y], parent="results_container"):
                    line_item = dpg.add_text(chunk, color=COLOR_DEFAULT)
                    dpg.bind_item_font(line_item, code_font)
                current_line_y += line_spacing

def check_input(ID, user_input):
    text = user_input.lower()
    i = 0
    dpg.delete_item("results_container", children_only=True)
    dpg.delete_item("lines_container", children_only=True)
    
    for key in cpp_library.keys():
        if text in key and text != "" and text != " ":
            new_button = dpg.add_button(
                label=key, 
                parent="results_container", 
                width=scale_x(300),
                height=scale_y(20),
                callback=button_callback, 
                user_data=key            
            )
            dpg.bind_item_theme(new_button, text_button_theme)
            i += 1
            
    if i == 0 and text != "":
        dpg.add_text("not found", parent="results_container")
        
    elif i != 0 and text != "" and text != " ":
        if i == 1:
            calculated_height = scale_y(50)
        else:
            calculated_height = scale_y(50) + (i - 1) * scale_y(25)
            
        x_left = 0
        x_right = scale_x(375)  
        y_top = scale_y(30)
        y_bottom = calculated_height 
        
        line_color = [255, 255, 255, 100]
        line_thick = 1
        
        dpg.draw_line(p1=[x_left, y_top], p2=[x_right, y_top], parent="lines_container", color=line_color, thickness=line_thick)
        dpg.draw_line(p1=[x_left, y_bottom], p2=[x_right, y_bottom], parent="lines_container", color=line_color, thickness=line_thick)
        dpg.draw_line(p1=[x_left, y_top], p2=[x_left, y_bottom], parent="lines_container", color=line_color, thickness=line_thick)
        dpg.draw_line(p1=[x_right, y_top], p2=[x_right, y_bottom], parent="lines_container", color=line_color, thickness=line_thick)


with dpg.theme() as text_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [255, 255, 255, 30])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [255, 255, 255, 60])
        dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.0, 0.5)
        

font_large_size = max(20, scale_y(40))
font_small_size = max(10, scale_y(15))
font_medium_size = max(15, scale_y(30))


with dpg.font_registry():
    with dpg.font("C:\\Windows\\Fonts\\arial.ttf", font_large_size) as big_bold_font: 
        pass
    with dpg.font("C:\\Windows\\Fonts\\consola.ttf", font_small_size) as code_font:
        pass
    with dpg.font("C:\\Windows\\Fonts\\consola.ttf", font_medium_size) as BIGcode_font:
        pass


with dpg.theme() as code_box_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [20, 20, 23, 255])
        dpg.add_theme_color(dpg.mvThemeCol_Border, [60, 60, 65, 255])
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)


with dpg.window(tag="primary_window", no_title_bar=True, no_move=True, no_resize=True):

    input_check = dpg.add_input_text(hint="Search here...", callback=check_input)

    dpg.add_draw_node(tag="lines_container")
    
    with dpg.group(pos=[scale_x(15), scale_y(40)]):
        dpg.add_group(tag="results_container")  
    
dpg.set_primary_window("primary_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
