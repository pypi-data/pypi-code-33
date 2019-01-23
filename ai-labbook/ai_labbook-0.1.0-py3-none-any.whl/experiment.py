import os
import sys
import json
import random
import pickle
import functools
import numpy as np 

from datetime import datetime
from contextlib import contextmanager
from tensorboardX import SummaryWriter
from dotmap import DotMap
from glob import glob
from sh import git

from events import SimpleEventBus
from decorators import emit_log_event, namespaced_logger

DEFAULT_PROTOCOL = 3

class Experiment:
    def __init__(self, name, working_dir="", log_dir="results", seed=0, monitors=None, save_system_state=None, load_system_state=None, set_system_seed=None):
        self.monitors = {}
        self.event_bus = SimpleEventBus()

        self.state = DotMap()

        self.state.seed = seed
        self.state.name = name
        self.state.log_dir = log_dir
        self.state.working_dir = working_dir

        self.context_stack = []
        self.current_context = None

        # Callback to get the state of the experiment. Should return a dictionary of the system state
        self.save_system_state = save_system_state
        self.load_system_state = load_system_state
        self.set_system_seed = set_system_seed

        self.state.start_time = datetime.now().strftime('%b%d_%H-%M-%S')

        # Make the experiment name into something more suitable for directory naming
        self.state.tag = self.state.name.lower().replace(" ", "_")
        self.state.exp_dir = os.path.join(self.state.log_dir, self.state.tag, self.state.start_time)
        self.state.run_dir = os.path.join(self.state.exp_dir, "logs")
        self.state.ckp_dir = os.path.join(self.state.exp_dir, "checkpoints")
        self.state.git_dir = os.path.join(self.state.working_dir, ".experiments")
        
        # Create the directories for the experiment
        os.makedirs(self.state.exp_dir, exist_ok=True)
        os.makedirs(self.state.run_dir, exist_ok=True)
        os.makedirs(self.state.ckp_dir, exist_ok=True)

        self.writer = SummaryWriter(log_dir=self.state.run_dir)

        # Call initialisation functions to set experiment state
        self.set_seed(self.seed)

        if monitors:
            for m in monitors:
                m._attach(self)

    def __getattr__(self, name):            
        attr = self.state[name] if name in self.state else None

        if not attr and self.current_context:
            state = self.state[self.current_context]
            attr = state[name] if name in state else None

        return attr

    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        self.set_system_seed(seed)

    def _git_checkpoint(self):
        if not self.state.git_dir:
            return

        # Create the experiments repo and add it to the .gitignore to prevent issues with nested repos
        if not os.path.exists(self.state.git_dir):
            git.init(bare=self.state.git_dir)

            with open(os.path.join(self.state.git_dir, ".gitignore"), "a") as f:
                f.write("*\n")
        
        scoped_git = git.bake(f"--git-dir={self.state.git_dir}", f"--work-tree={os.path.realpath(self.state.working_dir)}")
        # Add all files to the repo
        scoped_git.add(".")
        scoped_git.commit(message=f"Labbook Auto Checkpoint: [{self.state.config.name}] @ {self.state.start_time}")

        self.state.hash = scoped_git.rev_parse("HEAD")

    def _git_archive(self):
        if self.state.git_path:
            fname = os.path.join(self.state.exp_dir, "src.tar.gz")
            sh.git.archive("--format=tar.gz", f"--output={fname}", "HEAD")

    @namespaced_logger
    @emit_log_event
    def log_metric(self, tag, value, step=None):
        self.writer.add_scalar(tag, value, step)

    @namespaced_logger
    @emit_log_event
    def log_metrics(self, group_tag, metrics={}, step=None):
        self.writer.add_scalars(group_tag, metrics, step)

    @namespaced_logger
    @emit_log_event
    def log_parameter(self, tag, value, step=None):
        self.writer.add_text(tag, value, step)

    def log_parameters(self, group_tag, params={}, step=None):
        for k, v in params:
            self.log_parameter(f"{group_tag}/{k}", v, step)

    @namespaced_logger
    @emit_log_event
    def log_tensor(self, tag, value, step=None):
        # Make an image grid from each tensor channel
        pass

    @namespaced_logger
    @emit_log_event
    def log_histogram(self, tag, values, step=None):
        self.writer.add_histogram(tag, values, step)

    @namespaced_logger
    @emit_log_event
    def log_image(self, tag, image, step=None):
        self.writer.add_image(tag, image, step)

    def log_code(self, archive=False):
        self._git_checkpoint()
        if archive: self._git_archive()

    def stash_file(self, file_path):
        sh.cp(f"file_path", self.exp_dir)

    def state_dict(self):
        return self.state.toDict()

    def load_state_dict(self, state):
        self.state = DotMap(state)
        self.set_seed(self.state.seed)

    def save(self, tag=None):
        state = {}
        state['system'] = self.save_system_state(self.state.ckp_dir, self.state) # Return the checkpoints name, or an array of names
        state['experiment'] = self.state_dict()
        state['monitors'] = {}

        for m in self.monitors:
            state['monitors'][m.name] = m.state_dict()

        tag = f"-{tag}" if tag else ""
        checkpoint_path = os.path.join(self.state.exp_dir, f"experiment{tag}.ckp")

        with open(checkpoint_path, "wb") as f:
            pickle.dump(state, f, DEFAULT_PROTOCOL)

        self.emit_event(ExpEvent.SAVE, checkpoint_path)

    # Check if experiment checkpoints exist, if they do then load them
    def load(self, path=None, tag=None):
        state = None
        tag = f"-{tag}" if tag else ""
        path = path or os.path.join(self.state.exp_dir, f"experiment{tag}.ckp")

        assert os.path.exists(path), "Could not find experiment checkpoint {}".format(path)
        
        with open(path, "rb") as f:
            state = pickle.load(f)

        self.load_system_state(state['system'])
        self.load_state_dict(state['experiment'])

        for m_name, m_state in state['monitors'].items():
            if m_name in self.monitors:
                self.monitors[m_name].load_state_dict(m_state)

        self.emit_event(ExpEvent.LOAD, self.state)

    def reproduce(self):
        self.set_seed(self.state.seed)
        # TODO: Reset all counters step, epoch, global_step
        # If state.hash then checkout that code
        # If code exists that isn't commited then throw an error

    # Called after every epoch
    def epoch(self):
        state = self.state

        if self.current_context:
            state = self.state[self.current_context]

        state.epoch = state.epoch + 1 if 'epoch' in state else 0
        state.step = 0

        self.emit_event(ExpEvent.EPOCH, state.epoch, context=self.current_context)

    # Called after every batch
    def step(self):
        state = self.state

        if self.current_context:
            state = self.state[self.current_context]

        state.step = state.step + 1 if 'step' in state else 0
        state.global_step = state.global_step + 1 if 'global_step' in state else 0

        self.emit_event(ExpEvent.STEP, state.global_step, context=self.current_context)

    @contextmanager
    def namespace(self, tag="train"):
        self.context_stack.append(self.current_context)
        self.current_context = tag

        yield

        if len(self.context_stack) > 0:
            self.current_context = self.context_stack.pop()
        else:
            self.current_context = None

    def register_monitor(self, monitor):
        if monitor.name in self.monitors:
            raise Exception("You cannot register the same monitor twice.")

        self.monitors[monitor.name] = monitor

        for e in monitor.events:
            self.event_bus.subscribe(e, monitor)
    
    def subscribe_event(self, event, handler):
        self.event_bus.subscribe(event, handler)

    def emit_event(self, event, *args, **kwargs):
        self.event_bus.emit(event, *args, **kwargs)

    @staticmethod
    def load(path):
        pass
