import io, json
import models.settings.config as config
import logging
#export json to file
def export_json_to_file(data):
    try:
        with open(config.export_json_file_full_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        logging.info("Data successfully exported")
    except Exception as e:
        logging.error("Error. " + str(e))
