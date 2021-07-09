from marmtouch.experiments.base import Experiment

from collections import Counter
import random
import time
from pathlib import Path

import pygame

class Memory(Experiment):
    keys = 'trial','trial_start_time','condition','cue_touch','cue_RT','sample_touch','sample_RT','cue_duration','delay_duration','sample_duration','correct_duration','incorrect_duration'
    name = 'Memory'
    info_background = (0,0,0)
    def _run_delay(self,duration):
        """ Run a delay based for provided duration. Returns last touch during delay period if there was one. """
        self.screen.fill(self.background)
        self.flip()
        start_time = current_time = time.time()
        info = {'touch':0,'RT':0}
        while (current_time - start_time) < duration:
            current_time = time.time()
            tap = self.get_first_tap(self.parse_events())
            if not self.running:
                return
            if tap is not None:
                info = {'touch':1, 'RT': current_time-start_time, 'x':tap[0], 'y':tap[1]}
        return info

    def _show_cue(self,stimuli,timing,rel_tol=2):
        tolerance = stimuli['cue']['radius']*rel_tol

        self.screen.fill(self.background)
        self.draw_stimulus(**stimuli['cue'])
        self.flip()

        start_time = current_time = time.time()
        info = {'touch':0,'RT':0}
        while (current_time-start_time) < timing['cue_duration']:
            current_time = time.time()
            tap = self.get_first_tap(self.parse_events())
            if not self.running:
                return
            if tap is not None:
                if abs(stimuli['cue']['loc'][0]-tap[0])<tolerance and abs(stimuli['cue']['loc'][1]-tap[1])<tolerance:
                    info = {'touch':1, 'RT': current_time-start_time, 'x':tap[0], 'y':tap[1]}
        return info

    def _show_sample(self,stimuli,timing,rel_tol=2):
        tolerance = stimuli['cue']['radius']*rel_tol

        self.screen.fill(self.background)
        for target in stimuli['targets']:
            self.draw_stimulus(**target)
        self.flip()

        start_time = current_time = time.time()
        info = {'touch':0,'RT':0}
        while (current_time-start_time) < timing['sample_duration']:
            current_time = time.time()
            tap = self.get_first_tap(self.parse_events())
            if not self.running:
                return
            if tap is None:
                continue
            else:
                if abs(stimuli['cue']['loc'][0]-tap[0])<tolerance and abs(stimuli['cue']['loc'][1]-tap[1])<tolerance:
                    info = {'touch':1, 'RT': current_time-start_time, 'x':tap[0], 'y':tap[1]}
                    #reward and show correct for correct duration
                    self.screen.fill(self.background)
                    self.draw_stimulus(**stimuli['correct'])
                    self.flip()
                    self.good_monkey()
                    start_time = time.time()
                    while (time.time()-start_time) < timing['correct_duration']: 
                        self.parse_events()
                    #clear screen and exit
                    self.screen.fill(self.background)
                    self.flip()
                    break
                else:
                    info = {'touch':2, 'RT': current_time-start_time, 'x':tap[0], 'y':tap[1]}
                    #show incorrect for incorrect duration
                    self.screen.fill(self.background)
                    self.draw_stimulus(**stimuli['incorrect'])
                    self.flip()
                    start_time = time.time()
                    while (time.time()-start_time) < timing['incorrect_duration']:
                        self.parse_events()
                    #clear screen and exit
                    self.screen.fill(self.background)
                    self.flip()
                    break
        #else: #no response?
        return info

    def run(self):
        self.initialize()
        self.info = {condition: Counter() for condition in self.conditions.keys()}

        trial = 0
        self.running = True
        self.start_time = time.time()
        while self.running:
            self.update_info(trial)
            
            #iti
            start_time = time.time()
            while time.time()-start_time<5:
                self.parse_events()
                if not self.running:
                    return
            if not self.running:
                return
            
            #initialize trial parameters
            if self.blocks is None:
                condition = random.choice(list(self.conditions.keys()))
            else:
                condition = self.get_condition()

            stimuli = {stimulus: self.get_item(self.conditions[condition][stimulus]) for stimulus in ['cue','correct','incorrect']}
            stimuli['targets'] = [self.get_item(target) for target in self.conditions[condition]['targets']]

            timing = {f"{event}_duration": self.get_duration(event) for event in ['cue','delay','sample','correct','incorrect']}
            trial_start_time = time.time() - self.start_time
            trialdata = dict(trial=trial,trial_start_time=trial_start_time,condition=condition,cue_touch=0,sample_touch=0,cue_RT=0,sample_RT=0,**timing)

            self.TTLout['sync'].pulse(.1)
            self.camera.start_recording((self.data_dir/f'{trial}.h264').as_posix())

            #run trial
            cue_result = self._show_cue(stimuli, timing)
            if cue_result is None:
                break
            if cue_result['touch'] >= 0: #no matter what
                delay_result = self._run_delay(timing['delay_duration'])
                if delay_result is None:
                    break
                if delay_result.get('touch',0) >= 0: #no matter what
                    sample_result = self._show_sample(stimuli, timing)
                    if sample_result is None:
                        break
                    trialdata.update({
                        'cue_touch': cue_result.get('touch',0),
                        'cue_RT': cue_result.get('RT',0),
                        'sample_touch': sample_result.get('touch',0),
                        'sample_RT': sample_result.get('RT',0)
                    })
            outcome = trialdata['sample_touch']

            #wipe screen
            self.screen.fill(self.background)
            self.flip()

            self.camera.stop_recording()
            self.dump_trialdata(trialdata)
            trial += 1
            self.info[f"Condition {condition}, Delay: {timing['delay']}"][outcome] += 1
            if self.blocks is not None:
                self.update_condition_list(correct=(outcome==1))

    def update_info(self,trial):
        info = f"{self.params['monkey']} {self.params['task']} Trial#{trial}\n"
        for condition, condition_info in self.info.items():
            info += f"{condition}: {condition_info[1]: 3d} correct, {condition_info[2]: 3d} incorrect\n"
        overall = sum(self.info.values(),Counter())
        info += f"Overall: {overall[1]: 3d} correct, {overall[2]: 3d} incorrect, {overall[0]: 3d} no response\n"
        
        self.info_screen.fill(self.info_background)
        for idx, line in enumerate(info.splitlines()):
            txt = self.font.render(line,True,pygame.Color('GREEN'))
            txt = pygame.transform.rotate(txt,90)
            self.info_screen.blit(txt, (idx*30,30))
        self.flip()
