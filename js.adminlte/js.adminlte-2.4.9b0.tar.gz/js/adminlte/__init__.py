from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('adminlte', 'resources')

adminlte_css = Resource(library, 'css/adminlte.css',
						minified='css/adminlte.min.css',
						depends=[bootstrap_css])

adminlte_skin_blue_css = Resource(library,'css/skin-blue.css',
									minified='css/skin-blue.min.css',
									depends=[adminlte_css])

adminlte_js = Resource(library, 'js/adminlte.js',
	                   minified='js/adminlte.min.js',
	                   depends=[bootstrap_js, adminlte_skin_blue_css],
					   bottom = True)
datetimepicker_css = Resource(library,
							'plugins/datetimepicker/jquery.datetimepicker.css',
							minified = 'plugins/datetimepicker/jquery.datetimepicker.min.css',
							depends = [adminlte_css])

datetimepicker_js = Resource(library,
							'plugins/datetimepicker/jquery.datetimepicker.js',
							minified = 'plugins/datetimepicker/jquery.datetimepicker.min.js',
							depends = [adminlte_js],
							bottom = True)

datepicker_css = Resource(library, 'plugins/bootstrap-datepicker/bootstrap-datepicker.css',
						minified = 'plugins/bootstrap-datepicker/bootstrap-datepicker.min.css',
						depends = [adminlte_css])

datepicker_js = Resource(library, 'plugins/bootstrap-datepicker/bootstrap-datepicker.js',
						minified = 'plugins/bootstrap-datepicker/bootstrap-datepicker.min.js',
						depends = [adminlte_js,datepicker_css],
						bottom = True)

timepicker_css = Resource(library, 'plugins/bootstrap-timepicker/bootstrap-timepicker.css',
						minified = 'plugins/bootstrap-timepicker/bootstrap-timepicker.min.css',
						depends = [adminlte_css])

timepicker_js = Resource(library, 'plugins/bootstrap-timepicker/bootstrap-timepicker.js',
						minified = 'plugins/bootstrap-timepicker/bootstrap-timepicker.min.js',
						depends = [adminlte_js, timepicker_css],
						bottom = True)

bootstrap_wysihtml5_css = Resource(library, 'plugins/bootstrap-wysihtml5/bootstrap3-wysihtml5.css',
									minified = 'plugins/bootstrap-wysihtml5/bootstrap3-wysihtml5.min.css',
									depends = [adminlte_css])

bootstrap_wysihtml5_js = Resource(library, 'plugins/bootstrap-wysihtml5/bootstrap3-wysihtml5.js',
									minified = 'plugins/bootstrap-wysihtml5/bootstrap3-wysihtml5.min.js',
									depends = [adminlte_js, bootstrap_wysihtml5_css],
									bottom = True)

icheck_css = Resource(library, 'plugins/iCheck/all.css',
                      depends = [adminlte_css])

icheck_js = Resource(library, 'plugins/iCheck/icheck.js',
					minified = "plugins/iCheck/icheck.min.js",
					depends = [adminlte_js,icheck_css],
					bottom = True)

pace_css = Resource(library, 'plugins/pace/pace.css',
					minified = 'plugins/pace/pace.min.css',
					depends = [adminlte_css])

pace_js = Resource(library, 'plugins/pace/pace.js',
                   minified = 'plugins/pace/pace.min.js',
				   depends = [adminlte_js,pace_css],
				   bottom = True)

slimscroll_js = Resource(library, 'plugins/slimscroll/jquery.slimscroll.js',
					minified = 'plugins/slimscroll/jquery.slimscroll.min.js',
					depends = [adminlte_js],
					bottom = True
					)



		
all_plugins_js = Resource(library, 'all.js',
					depends=[adminlte_js, slimscroll_js, pace_js, icheck_js, bootstrap_wysihtml5_js,
					       timepicker_js, datepicker_js],
						   bottom = True)







