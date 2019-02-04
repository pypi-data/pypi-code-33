##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017-18  SensiML Corporation.                                   #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


from ipywidgets import Layout, Button, VBox, HBox, Dropdown, Checkbox, Label, widgets
from sensiml.widgets.base_widget import BaseWidget
import qgrid
from pandas import DataFrame

class AutoSenseWidget(BaseWidget):

    def _get_query_list(self):
        q_list = self._dsk.list_queries()
        if q_list is not None:
            return ['']+list(q_list['Name'].values)
        else:
            return ['']

    def _on_button_clicked(self, b):
        self._b_run.disabled=True
        self._b_run.description='RUNNING...'
        self._b_run.icon=''

        try:
            self._run_pipeline_optimizer()
        except:
            self._reset_optimizer_button()

        self._reset_optimizer_button()

        #thread = threading.Thread(target=self._run_pipeline_optimizer)
        #thread.start()

    def _reset_optimizer_button(self):

        self._b_run.disabled=False
        self._b_run.description='Optimize Knowledge Pack'
        self._b_run.icon='play'

    def _run_pipeline_optimizer(self):
        query_name = self._w_query.value
        segmenter = str(self._w_segment.value)
        seed_choice = str(self._w_seed.value)
        accuracy = self._w_accuracy.value
        sensitivity = self._w_sensitivity.value
        features = self._w_features.value
        neurons = self._w_neurons.value
        iterations = self._w_iterations.value
        population_size = self._w_population_size.value
        reset = self._c_reset.value

        if not query_name:
            print("\nERROR: No query name specified!\n")
            return


        if self._dsk.pipeline is None:
            print("\nERROR: Pipeline is not set, use: dsk.pipeline='Pipeline Name'!\n")
            return


        params =  {'iterations': 2, # <--- Do two more iterations
                   'reset': True, # <--- Use reset=False to bypass initialization and pick up from the last run
                   'accuracy':accuracy,
                   'sensitivity':sensitivity,
                   'features':features,
                   'neurons':neurons,
                   'reset': reset,
                   'iterations':iterations,
                   'population_size':population_size,
                }



        add_windowing = False
        delta = None

        if segmenter == 'Query Segmenter':
            query = self._dsk.project.queries.get_or_create_query(query_name)
            if self._dsk.project.get_segmenters().loc[query.segmenter]['name'] == 'Manual':
                print("\n\nERROR: This Query only has manually labeled segments associated with it!\n\tSelect a Windowing Segmenter to run this pipeline.\n")
                return

        elif 'Windowing' in segmenter:
            if "(100)" in segmenter:
                delta = 100
            if "(250)" in segmenter:
                delta = 250
            if "(500)" in segmenter:
                delta = 500
            if "(1000)" in segmenter:
                delta = 1000

            add_windowing = True


        else:
            print("\n\nERROR: No segmentation algorithm was selected. Select a Segmenter to run this pipeline.\n")
            return

        self._dsk.project.query_optimize()

        self._dsk.pipeline.reset()
        self._dsk.pipeline.set_input_query(query_name)

        if add_windowing:
            self._dsk.pipeline.add_transform("Windowing", params={"window_size": delta,
								                                  "delta": delta })


        print("Auto Sense Params", params)
        print(self._dsk.pipeline.describe())
        self.results, self.summary = self._dsk.pipeline.auto({'seed': seed_choice,
                                                    'params':params,
                                                   })
        if self.summary is not None:
            self._w_results.df = self.summary['fitness_summary'][['accuracy', 'sensitivity', 'neurons','features']].astype(int).head()
            print("\nAutomation Pipeline Completed. Results saved in self.results, self.summary.")


    def _terminate_run(self, b):
        self._dsk.pipeline.stop_pipeline()

    def _select_seed(self, Name):
        if self._dsk and Name:
            self._w_seed_desc.value = self._dsk.seeds.get_seed_by_name(Name).description

    def _on_value_change(self, change):
        if self._dsk is None:
            return
        if self._dsk.pipeline and change['new']:
            self._dsk.pipeline.reset()
            self._dsk.pipeline.set_input_query(change['new'])
        else:
            print("No Pipeline Selected.")


    def _refresh(self, b=None):
        if self._dsk:
            self._w_query.options = self._get_query_list()
            self._w_query.values = self._w_query.options[0]
            self._w_seed.options = sorted(self._dsk.seeds.seed_dict.keys())

    def _clear(self):
        self._w_query.options = ['']
        self._w_query.value = ''

    def create_widget(self):

        self._w_query = Dropdown(description='Select Query', options=[], layout=Layout(width='85%'))
        self._w_segment = widgets.Dropdown(description = 'Segmenter',
            options=['', 'Query Segmenter', 'Windowing(100)', 'Windowing(250)', 'Windowing(500)', 'Windowing(1000)'])

        self._info_sensitivity = widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines the priority of Sensitivity, ie. the ability to determine individual event correctly.\nA higher value corresponds to a higher priority.',
            layout=Layout(width="10%",align_self='flex-end')
        )
        self._info_accuracy =  widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines the priority of accuracy, ie. the ability to differentiate events correctly.\nA higher value corresponds to a higher priority.',
            layout=Layout(width="10%",align_self='flex-end')
        )
        self._info_neurons = widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines the priority of the number of neurons which are the influence area of each event in the model.\nThe more neurons the more memory is used on the device.\nA higher value corresponds to a higher priority to favor models with fewer neurons.',
            layout=Layout(width="10%",align_self='flex-end')
        )
        self._info_features =  widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines the priority of the number of features, ie. the number of algorithms to differentiate the events correctly.\nLess features typically means less memory and lower latency.\nA higher value corresponds to a higher priority to favor models with fewer features.',
            layout=Layout(width="10%",align_self='flex-end')
        )


        self._info_population =  widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines how large the inital population is. A higher population means a larger initial search space is.\nA higher population typically produces better results but takes more time.',
            layout=Layout(width="10%",align_self='flex-end')
        )


        self._info_iterations =  widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Defines the number of iterations the model will go through.\n At each iteration a new population of models is created by mutating the previous iterations population.\nA higher number of iteration produces better results but takes more time.',
            layout=Layout(width="10%",align_self='flex-end')
            )

        self._w_seed = widgets.Dropdown(description='Seed', options=[],)
        self._w_seed_desc = widgets.Textarea(description='Description', rows=7, disable=True)
        self._w_intereact = widgets.interactive(self._select_seed, Name=self._w_seed)
        self._w_accuracy = widgets.FloatSlider(description = 'Accuracy', value=1.0, min=0.0, max=1.0, step=0.05, )
        self._w_sensitivity = widgets.FloatSlider(description = 'Sensitivity', value=1.0, min=0.0, max=1.0, step=0.05,)
        self._w_features = widgets.FloatSlider(description = 'Features', value=.8, min=0.0, max=1.0, step=0.05,)
        self._w_neurons = widgets.FloatSlider(description = 'Neurons', value=.8, min=0.0, max=1.0, step=0.05,)
        self._w_iterations = widgets.IntSlider(description = "Iterations", value=4, min=1, max=15, step=1,)

        self._w_population_size = widgets.IntSlider(description = "Population", value=25, min=10, max=75, step=1,  )
        self._c_reset = Checkbox(description='Reset', value=True)
        self._w_results = qgrid.show_grid(DataFrame(columns=['accuracy', 'sensitivity', 'neurons','features']),
                                             grid_options={'rowHeight':35, 'maxVisibleRows':5, 'minVisibleRows':5, 'editable':False,
                                                            'defaultColumnWidth':15, "forceFitColumns":True, 'sortable': False, 'filterable': False})
        self._w_results.layout.width = "95%"#unicode("250px")"
        self._w_results.layout.align_self='flex-end'


        self._b_run = Button(icon='play', description='Optimize Knowledge Pack', layout=Layout(width='98%', align_self='flex-end'))
        self._b_refresh = Button(icon="refresh", layout=Layout(width='15%'))
        self._b_terminate = Button(icon='stop', description='Terminate', layout=Layout(width='25%', align_self='flex-end'))
        self._b_iterate = Button(icon='redo', description='Iterate', layout=Layout(width='98%', align_self='flex-end'))

        self._w_query.observe(self._on_value_change, names='value')

        self._b_run.on_click(self._on_button_clicked)
        self._b_refresh.on_click(self._refresh)
        self._b_run.style.button_color = '#4cb243'
        self._b_terminate.on_click(self._terminate_run)

        self._refresh()


        self._widget =      HBox([
                                 VBox([HBox([self._w_query,self._b_refresh]),
                                       self._w_segment,
                                       self._w_intereact,
                                       self._w_seed_desc,
                                       self._b_run
                                      ]),
                                VBox([
                                    HBox([
                                        VBox([
                                            HBox([self._w_accuracy, self._info_accuracy],),
                                            HBox([self._w_sensitivity, self._info_sensitivity]),
                                            HBox([self._w_features, self._info_features]),
                                            ]),
                                        VBox(
                                            [HBox([self._w_neurons, self._info_neurons]),
                                            HBox([self._w_population_size, self._info_population]),
                                            HBox([self._w_iterations, self._info_iterations]),
                                            ])
                                        ]),

                                    self._w_results
                                    ],layout=Layout(width="66%")),
                                ], layout=Layout(width='100%'))
                           #


        return self._widget


