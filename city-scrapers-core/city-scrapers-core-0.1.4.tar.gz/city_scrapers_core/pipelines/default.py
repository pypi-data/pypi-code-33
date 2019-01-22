from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.decorators import ignore_jscalendar


class DefaultValuesPipeline:
    """Sets default values for Meeting items"""

    @ignore_jscalendar
    def process_item(self, item, spider):
        item.setdefault("description", "")
        item.setdefault("all_day", False)
        item.setdefault("location", {})
        item.setdefault("links", [])
        item.setdefaults("time_notes", "")
        item.setdefaults("classification", NOT_CLASSIFIED)
        item.setdefaults("status", TENTATIVE)
        return item
