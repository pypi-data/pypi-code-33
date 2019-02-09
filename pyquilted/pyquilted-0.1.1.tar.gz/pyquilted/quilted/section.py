class Section:
    def serialize(self):
        base_dict = vars(self)
        section_dict = dict()
        # lowercase labels
        section_dict[base_dict['label'].lower()] = base_dict
        return section_dict
