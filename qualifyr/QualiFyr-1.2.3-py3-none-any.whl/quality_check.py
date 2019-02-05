class QualityCheck:
    def __init__(self, metric_name, metric_value, conditions):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.check = None
        self.result = None

        self.check_metric(conditions)


    
    def check_metric(self, conditions):
        for check_result in ['failure', 'warning']:
            if check_result in conditions[self.metric_name]:
                condition_type = conditions[self.metric_name][check_result]['condition_type']
                condition_value = conditions[self.metric_name][check_result]['condition_value']
                # possible conditions
                # greater than
                if condition_type == 'gt':
                    self.check = '> {0}'.format(condition_value)
                    if self.metric_value > condition_value:
                        self.result = check_result.upper()
                        return
                # less than
                elif condition_type == 'lt':
                    self.check = '< {0}'.format(condition_value)
                    if self.metric_value < condition_value:
                        self.result = check_result.upper()
                        return
                # less than and greater than
                elif condition_type == 'lt_gt':
                    self.check = '< {0} and/or > {1}'.format(condition_value[0], condition_value[1])
                    if (self.metric_value < condition_value[0] or self.metric_value > condition_value[1]):
                        self.result = check_result.upper()
                        return
                # equal to
                elif condition_type == 'eq':
                    self.check = 'Equals {0}'.format(condition_value)
                    if self.metric_value == condition_value:
                        self.result = check_result.upper()
                        return
                # less than and greater than
                elif condition_type == 'ne':
                    self.check = 'Does not equal {0}'.format(condition_value)
                    if self.metric_value != condition_value:
                        self.result = check_result.upper()
                        return
                # any
                elif condition_type == 'any':
                    self.check = 'One of {0}'.format(', '.join(condition_value))
                    if self.metric_value in condition_value:
                        self.result = check_result.upper()
                        return
        self.result = 'PASS'
        return
    
    def to_tuple(self):
        return (self.metric_name, self.metric_value, self.check, self.result)