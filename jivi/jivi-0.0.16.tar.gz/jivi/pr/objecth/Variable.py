from jivi.pr.Object import Object

class Variable(Object):
	attr = []
	attr.append(dict(n='name',r=1,a='_field-name'))
	attr.append(dict(n='data_type',r=1,a='_data-type,datatype'))
	attr.append(dict(n='initial',r=1,a='_initial,init'))
	attr.append(dict(n='label',r=1,a='_label'))
	attr.append(dict(n='decimals',r=1,a='_decimals'))
	attr.append(dict(n='order',r=1,a='_order'))
	attr.append(dict(n='extent',r=1,a='_extent'))
	attr.append(dict(n='help',r=1,a='_help'))
	attr.append(dict(n='desc',r=1,a='_desc'))
	attr.append(dict(n='col_label',r=1,a='_col-label'))
	attr.append(dict(n='view_as',r=1,a='_view-as'))
	attr.append(dict(n='charset',r=1,a='_charset'))
	attr.append(dict(n='collation',r=1,a='_collation'))
	attr.append(dict(n='fetch_type',r=1,a='_fetch-type'))
	