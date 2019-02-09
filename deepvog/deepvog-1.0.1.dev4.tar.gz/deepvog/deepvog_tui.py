import urwid
import numpy
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Tell tensorflow to shut up!
import sys
import subprocess
from .model.DeepVOG_model import load_DeepVOG
from glob import glob

import warnings
warnings.filterwarnings("ignore") # Suppress warnings



class Button_centered(urwid.Button):
    def __init__(self, label, on_press=None, user_data=None):
        super(Button_centered, self).__init__( label, on_press=None, user_data=None)
        self._label.align = 'center'
class EditionStorer(object):
    def __init__(self):
        self.Editors = dict()
    def set_editor(self,key, label, align, attr_map = None, focus_map = None):
        self.Editors[key] = urwid.AttrMap(urwid.Edit(label, align=align), attr_map, focus_map)
    def get_editor(self, key):
        return self.Editors[key]

class CheckboxStorer(object):
    def __init__(self):
        self.boxes = dict()
    def set_box(self,key, label, attr_map = None, focus_map = None):
        self.boxes[key] = self.boxes.get(key, urwid.AttrMap(urwid.CheckBox(label, state = False), attr_map, focus_map))
    def get_box(self, key):
        return self.boxes[key]

class deepvog_jobman(object):
    def __init__(self, gpu_num, flen, scaling):
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID" 
        os.environ["CUDA_VISIBLE_DEVICES"]=gpu_num
        self.model = load_DeepVOG()
        self.flen = flen
        self.scaling = scaling
        
    def fit(self, vid_path, output_json_path):
        inferer = deepvog.gaze_inferer(self.model, self.flen, self.scaling)
        inferer.fit(vid_path)
        inferer.save_eyeball_model(output_json_path) 


class deepvog_tui(object):
    def __init__(self, base_dir):
        # Parameters and directories of a session
        self.base_dir = base_dir
        self.flen = 6
        self.mm2px_scaling = 1/0.015
        self.GPU_number = "0"
        self.fitting_dir = "fitting_videos"
        self.eyeballmodel_dir = "eyeball_models"
        self.inference_dir = "inference_videos"
        self.results_dir = "results"
        

        # Fitting/Inference parameters
        self.selected_fitting_vids = dict()
        self.execution_code = "exit"

        # urwid setting
        self.main_interface_title = "DeepVOG"
        self.main_menu_choices = ["Set parameters and directories",
                                  "Fit 3D eyeball models",
                                  "Gaze inference",
                                  "Instruction",
                                  "About us",
                                  "Exit"]
        self.palette = [('reversed', 'standout', '')]
        self.main_widget = None
        self.main_loop = None
        self.fitting_checkboxes = CheckboxStorer()
        self.editors = EditionStorer()
        self.editors.set_editor("flen", "", "right", focus_map="reversed")
        self.editors.set_editor("scaling", "", "right", focus_map="reversed")
        self.editors.set_editor("GPU", "", "right", focus_map="reversed")
        self.editors.set_editor("fitting_dir", "", "right", focus_map="reversed")
        self.editors.set_editor("eyeballmodel_dir", "", "right", focus_map="reversed")
        self.editors.set_editor("inference_dir", "", "right", focus_map="reversed")
        self.editors.set_editor("results_dir", "", "right", focus_map="reversed")
    
    # Main menu
    def _main_menu(self, title, choices):
        body = [urwid.Text(title, align="center"), urwid.Divider()]
        button_dict = dict()

        for choice in choices:
            button_dict[choice] = urwid.Button(choice)
            body.append(urwid.AttrMap(button_dict[choice], None, focus_map= 'reversed'))
        urwid.connect_signal(button_dict["Exit"], 'click', self.exit_program)
        urwid.connect_signal(button_dict["Set parameters and directories"], 'click', self.onClick_set_parameters_from_main)
        urwid.connect_signal(button_dict["Fit 3D eyeball models"], 'click', self.onClick_fit_models_from_main)
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    # "Set parameters" page
    def onClick_set_parameters_from_main(self, button):
        # Title and divider
        title_set_params = urwid.Text("Set parameters and directories\nYour base directory is {}".format(self.base_dir), align="center")
        div = urwid.Divider()

        # Ask and answer
        ask_flen = urwid.Text('Focal length of the camera (in mm):\n', align="left")
        answer_flen = self.editors.get_editor("flen")
        
        ask_scaling = urwid.Text('Pixel scaling (mm/pixel):\n', align="left")
        answer_scaling = self.editors.get_editor("scaling")

        ask_GPU = urwid.Text('GPU number:\n', align="left")
        answer_GPU = self.editors.get_editor("GPU")

        ask_fitting_dir = urwid.Text('Directory of fitting videos:\n', align="left")
        answer_fitting_dir = self.editors.get_editor("fitting_dir")

        ask_eyeballmodel_dir = urwid.Text('Directory of fitted 3D eyeball models:\n', align="left")
        answer_eyeballmodel_dir = self.editors.get_editor("eyeballmodel_dir")

        ask_inference_dir = urwid.Text('Directory of videos for gaze estimation:\n', align="left")
        answer_inference_dir = self.editors.get_editor("inference_dir")

        ask_results_dir = urwid.Text('Directory of output results:\n', align="left")
        answer_results_dir = self.editors.get_editor("results_dir")

        # Buttons for save/back
        back_button = Button_centered("Back and save")
        urwid.connect_signal(back_button, 'click', self.onClick_back_from_params)
        
        # Constructing piles and columns
        ask_pile = urwid.Pile([ask_flen, ask_scaling,ask_GPU, ask_fitting_dir, ask_eyeballmodel_dir, ask_inference_dir, ask_results_dir])
        answer_pile = urwid.Pile([answer_flen, div, answer_scaling, div, answer_GPU, div, answer_fitting_dir, div, answer_eyeballmodel_dir, div, answer_inference_dir, div, answer_results_dir])
        interaction_columns = urwid.Columns([ask_pile, answer_pile])
        whole_fill = urwid.Filler(urwid.Pile([title_set_params,
                                              div,
                                              interaction_columns,
                                              urwid.AttrMap(back_button, None, 'reversed')] ))

        # Set the interface
        self.main_widget.original_widget = whole_fill
    
    # Fitting models page (select files for fitting)
    def onClick_fit_models_from_main(self, button):
        title_fit_models = urwid.Text("Fit 3D eyeball models\n Your directory of fitting videos is {}".format(self.get_fitting_dir()), align="center")
        div = urwid.Divider()
        vids_paths, vids_names = self.grab_paths_and_names(self.get_fitting_dir())
        box_dict = dict()
        fitting_list_body = [title_fit_models, div]

        # select all checkboxes
        self.fitting_checkboxes.set_box("select all", "select all", focus_map = 'reversed')
        urwid.connect_signal(self.fitting_checkboxes.get_box("select all").original_widget, 'change', self.onChange_fitting_selectall, (vids_names, vids_paths))
        fitting_list_body.append(self.fitting_checkboxes.get_box("select all"))
        # Start button
        start_button = Button_centered("Start fitting")
        urwid.connect_signal(start_button, 'click', self.onClick_start_from_fitting)

        # Back button
        back_button = Button_centered("Back and save")
        urwid.connect_signal(back_button, 'click', self.onClick_back_to_main)
        
        # Check box for all videos
        for vid_path, vid_name in zip(vids_paths,vids_names):
            self.fitting_checkboxes.set_box(vid_name, vid_name, focus_map= 'reversed')
            urwid.connect_signal(self.fitting_checkboxes.get_box(vid_name).original_widget, 'change', self.onChange_fitting_checkbox, (vid_name, vid_path))
            fitting_list_body.append(self.fitting_checkboxes.get_box(vid_name))

        fitting_list_body.append(urwid.AttrMap(start_button, None, 'reversed'))
        fitting_list_body.append(urwid.AttrMap(back_button, None, 'reversed'))
        
        fitting_list_walker = urwid.ListBox(urwid.SimpleFocusListWalker(fitting_list_body))
        self.main_widget.original_widget = fitting_list_walker

        return fitting_list_walker
    
    # Clicking "back and save" in "Set up parameters" page
    def onClick_back_from_params(self, button):
        if self.editors.get_editor("flen").original_widget.edit_text is None:
            self.flen = self.editors.get_editor("flen").original_widget.edit_text
        else:
            self.flen = float(self.editors.get_editor("flen").original_widget.edit_text)
        if self.editors.get_editor("scaling").original_widget.edit_text is None:
            self.mm2px_scaling = self.editors.get_editor("scaling").original_widget.edit_text
        else:
            self.mm2px_scaling = float(self.editors.get_editor("scaling").original_widget.edit_text)
        
        # Save parameters as attributes
        self.GPU_number = self.editors.get_editor("GPU").original_widget.edit_text
        self.fitting_dir = self.editors.get_editor("fitting_dir").original_widget.edit_text
        self.eyeballmodel_dir = self.editors.get_editor("eyeballmodel_dir").original_widget.edit_text
        self.inference_dir = self.editors.get_editor("inference_dir").original_widget.edit_text
        self.results_dir = self.editors.get_editor("results_dir").original_widget.edit_text
        self.main_widget.original_widget = self._main_menu(self.main_interface_title, self.main_menu_choices)

    # Confirmation page for fitting 3D eyeballs
    def onClick_start_from_fitting(self, button):
        title = urwid.Text("(Confirm before you start) Eyeball models will be fit to the videos below.\nEyeball models will be stored in {}".format(self.get_models_dir()), align="center")
        div = urwid.Divider()
        confirmation_page_list = [title, div]
        for vid_name in self.selected_fitting_vids.keys():
            confirmation_page_list.append(urwid.Text(self.selected_fitting_vids[vid_name], align = 'left'))
        # Start button
        start_button = Button_centered("Confirm")
        urwid.connect_signal(start_button, 'click', self.onClick_start_fitting)

        # Back button
        back_button = Button_centered("Back")
        urwid.connect_signal(back_button, 'click', self.onClick_fit_models_from_main)


        confirmation_page_list.append(urwid.AttrMap(start_button, None, 'reversed'))
        confirmation_page_list.append(urwid.AttrMap(back_button, None, 'reversed'))
        confirmation_page_list_walker = urwid.ListBox(urwid.SimpleFocusListWalker(confirmation_page_list))
        self.main_widget.original_widget = confirmation_page_list_walker

    

    def onClick_back_to_main(self, button):
        self.main_widget.original_widget = self._main_menu(self.main_interface_title, self.main_menu_choices)

    def onChange_fitting_selectall(self, check_box, new_state, vid_data):
        (vids_names, vids_paths) = vid_data
        if new_state == True:
            for key in self.fitting_checkboxes.boxes.keys():
                self.fitting_checkboxes.get_box(key).original_widget.set_state(True, do_callback=False)
            for vid_name, vid_path in zip(vids_names, vids_paths):
                self.selected_fitting_vids[vid_name] = vid_path
        else:
            for key in self.fitting_checkboxes.boxes.keys():
                self.fitting_checkboxes.get_box(key).original_widget.set_state(False, do_callback=False)
            for vid_name, vid_path in zip(vids_names, vids_paths):
                if self.selected_fitting_vids.get(vid_name) is not None:
                    self.selected_fitting_vids.pop(vid_name)

    def onChange_fitting_checkbox(self, check_box, new_state, vid_data):
        (vid_name, vid_path) = vid_data
        if new_state == True:
            self.selected_fitting_vids[vid_name] = vid_path
        if new_state == False:
            if self.selected_fitting_vids.get(vid_name) is not None:
                self.selected_fitting_vids.pop(vid_name)
                

    def execution_outsideTUI(self):
        
        if self.execution_code == "exit":
            print("\nProgram exited.")
        if self.execution_code == "fit":
            print("\nFitting starts")
            self.deepVOG_fitting()
            # After fitting, start the main interface again
            self.run_tui()
        if self.execution_code == "infer":
            print("\nInference starts")
            self.deepVOG_inference()
            self.run_tui()


    def deepVOG_fitting(self):
        jobman = deepvog_jobman(self.GPU_number, self.flen, self.mm2px_scaling)
        for vid_name in self.selected_fitting_vids.keys():

            vid_path = self.selected_fitting_vids[vid_name]
            vid_name_root = os.path.splitext(os.path.split(vid_path)[1])[0]
            output_json_path = os.path.join(self.base_dir, self.eyeballmodel_dir, vid_name_root + ".json")
            jobman.fit(vid_path, output_json_path)
    def deepVOG_inference(self):
        pass

    def run_tui(self):
        self.main_widget = urwid.Padding(self._main_menu(self.main_interface_title, self.main_menu_choices), left=2, right=2)
        self.main_loop = urwid.Overlay(self.main_widget, urwid.SolidFill(u"\N{MEDIUM SHADE}"), 
                            align= 'center', width= ('relative', 60), valign= 'middle', height= ('relative', 60),
                            min_width=20, min_height=9)
        
        
        self.loop_process = urwid.MainLoop(self.main_loop, self.palette)
        self.loop_process.run()

        self.execution_outsideTUI()


    def get_fitting_dir(self):
        return os.path.join(self.base_dir, self.fitting_dir)
    def get_models_dir(self):
        return os.path.join(self.base_dir, self.eyeballmodel_dir)

    # After confirmation, start fitting outside of tui.
    def onClick_start_fitting(self, button):
        self.execution_code = "fit"
        raise urwid.ExitMainLoop()
    def onClick_start_inference(self, button):
        self.execution_code = "infer"
        raise urwid.ExitMainLoop
    def exit_program(self, button):
        self.execution_code = "exit"
        raise urwid.ExitMainLoop
    @staticmethod
    def grab_paths_and_names(target_dir, extensions = [""]):
        """
        Please add dot to the extension, for example, extensions = [".mp4", ".avi", ".pgm"]
        """
        # Grap all paths
        all_paths = []
        for extension in extensions:
            paths = glob(os.path.join(target_dir, "*" + extension))
            all_paths += paths
        all_paths = sorted(all_paths)

        all_names = list(map(lambda x : os.path.split(x)[1], all_paths))
        return all_paths, all_names



if __name__ == "__main__":
    if len(sys.argv)>1:

        tui = deepvog_tui(str(sys.argv[1]))
        tui.run_tui()
