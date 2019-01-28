import numpy as np
import json


class landsat(object):

    @staticmethod
    def parse_sb_to_return_meta(sb, ts, band):
        timestamps = sorted(sb.timestamps.keys())
        if len(timestamps) == 0:
            return None, None, None

        metadata = json.loads(sb.timestamps[timestamps[ts]].properties["resource_metadata"])
        spacecraft_id = metadata["spacecraft_id"]
        sensor_id = metadata["sensor_id"]
        collection = metadata["collection_number"]
        return spacecraft_id, sensor_id, collection

    ####################################################################################################################
    # The PRE Collection QA Band is Available for LandSat 8 Only, i.e., LANDSAT_8 & PRE
    # https://landsat.usgs.gov/qualityband

    # Parse PRE Collection QA Band:
    # Bit 0 = 0 = not fill
    # Bit 1 = 0 = not a dropped frame
    # Bit 2 = 0 = not terrain occluded
    # Bit 3 = 0 = unused
    # Bit 4-5 = 01 = not water
    # Bit 6-7 = 00 = unused
    # Bit 8-9 = 00 = unused
    # Bit 10-11 = 01 = snow/ice
    # Bit 12-13 = 10 = not cirrus
    # Bit 14-15 = 11 = cloudy

    # For the single bits (0, 1, 2, and 3):
    # 0 = No, this condition does not exist
    # 1 = Yes, this condition exists
    #
    # For the Water bits (4-5)
    # 00 = No, this condition does not exist
    # 10 = Yes, this condition exists
    #
    # For the Snow/Ice bits (10-11):
    # 00 = No, this condition does not exist
    # 11 = Yes, this condition exists

    # The other double bits (6-7, 8-9, 12-13, and 14-15), read from left to right,
    # represent levels of confidence that a condition exists:
    #
    # 00 = Not Determined = Algorithm did not determine the status of this condition
    # 01 = No = Algorithm has low to no confidence that this condition exists (0-33 percent confidence)
    # 10 = Maybe = Algorithm has medium confidence that this condition exists (34-66 percent confidence)
    # 11 = Yes = Algorithm has high confidence that this condition exists (67-100 percent confidence).
    #
    # None of the currently populated bits are expected to exceed 80% accuracy in their reported assessment at this time.
    ####################################################################################################################

    ####################################################################################################################
    # The Landsat Collection 1 Level-1 Quality Assessment (QA) 16-bit Band
    # These Differ for Every SPACECRAFT_IT and SENSOR_ID
    # However, they differ by inclusion. I.e., LandSat8 has a Cirrus band; Landsat < 8 does not.
    # https://landsat.usgs.gov/collectionqualityband

    # Collection 1 QA Band:
    # Bit 0 : 0 = fill, 1 = not fill
    # Bit 1 : 0 = not a dropped frame or not terrain occulusion
    # Bit 2-3 = 0 = radiometric saturation
    # Bit 4 = 0 = cloud
    # Bit 5-6 = 00 = cloud confidence (45 TM and 8 only)
    # Bit 7-8 = 00 = cloud shadow confidence (45 TM and 8 only)
    # Bit 9-10 = 00 = snow/ice confidence
    # Bit 11-12 = 01 = cirrus confidence
    # Bit 12-15 = 00 = not used

    # For the single bits (0, 1, 2, and 3):
    # 0 = No, this condition does not exist
    # 1 = Yes, this condition exists
    #
    # For the Water bits (4-5)
    # 00 = No, this condition does not exist
    # 10 = Yes, this condition exists
    #
    # For the Snow/Ice bits (10-11):
    # 00 = No, this condition does not exist
    # 11 = Yes, this condition exists

    # The other double bits (6-7, 8-9, 12-13, and 14-15), read from left to right,
    # represent levels of confidence that a condition exists:
    #
    # 00 = Not Determined = Algorithm did not determine the status of this condition
    # 01 = No = Algorithm has low to no confidence that this condition exists (0-33 percent confidence)
    # 10 = Maybe = Algorithm has medium confidence that this condition exists (34-66 percent confidence)
    # 11 = Yes = Algorithm has high confidence that this condition exists (67-100 percent confidence).
    #
    # None of the currently populated bits are expected to exceed 80% accuracy in their reported assessment at this time.
    ####################################################################################################################


    ############################################################
    # Snow/Ice Like
    # 00 = No, this condition does not exist
    # 11 = Yes, this condition exists
    ############################################################
    @staticmethod
    def landsat_snowice(im):
        return im[:,:,:,0] * im[:,:,:,1]

    @staticmethod
    def landsat_snowice_validate(im):
        return np.all(im[:,:,:,0] - im[:,:,:,1] == 0)

    ############################################################
    # 2bit-Confidence Like
    # 00 = Not Determined = Algorithm did not determine the status of this condition
    # 01 = No = Algorithm has low to no confidence that this condition exists (0-33 percent confidence)
    # 10 = Maybe = Algorithm has medium confidence that this condition exists (34-66 percent confidence)
    # 11 = Yes = Algorithm has high confidence that this condition exists (67-100 percent confidence).
    # Note: We consider ALL NOT HIGH CONFIDENCE as Low Confidence.
    ############################################################
    @staticmethod
    def landsat_2bit_confidence(im):
        # c = im[:,:,0] + 0.5 * im[:,:,1] - 0.5
        # c[np.where(c == -0.5)] = float("nan")
        return landsat.landsat_snowice(im)

    @staticmethod
    def landsat_1bit_confidence(im):
        return im

    ############################################################
    # The 8bit QA consists of 16bit QA channels 8-15, reversed, so the bits are flipped.
    # Channel 2-3: Snow/Ice
    # Channel 4-5: cirrus
    # Channel 6-7: cloudy
    ############################################################
    @staticmethod
    def landsat_qa_collection_pre(qa_band, spacecraft_id):
        bits = np.flip(np.unpackbits(np.array(qa_band, dtype=np.uint8).view(np.uint8), axis=3), axis=3)
        mask = np.stack([landsat.landsat_snowice(bits[:,:,:,2:4]),
                         landsat.landsat_2bit_confidence(bits[:,:,:,4:6]),
                         landsat.landsat_2bit_confidence(bits[:,:,:,6:8])], axis=2)
        labels = [ "snowice", "cirrus", "cloudy" ]
        return mask, labels

    @staticmethod
    def landsat_qa_collection_01(qa_band, spacecraft_id, sensor_id):
        bits = np.unpackbits(np.array(qa_band, dtype=np.uint16).view(np.uint8), axis=3)
        bits = np.flip(np.concatenate([bits[:,:,:,8:16], bits[:,:,:,0:8]], axis=3), axis=3)
        masks = [landsat.landsat_1bit_confidence(bits[:,:,:,4]),
                 landsat.landsat_2bit_confidence(bits[:,:,:,7:9]),
                 landsat.landsat_2bit_confidence(bits[:,:,:,9:11])]
        labels = ["cloud", "cloud_shadow", "snowice"]
        # Image.fromarray(masks[0][0]*255).show()
        if spacecraft_id == "LANDSAT_8":
            masks.append(landsat.landsat_2bit_confidence(bits[:,:,:,11:13]))
            labels.append("cirrus")
        return np.stack(masks, axis=3), labels

    @staticmethod
    def landsat_qa_band(qa_band, spacecraft_id, sensor_id, collection):
        masks, labels = [], []
        if collection == "PRE":
            masks, labels = landsat.landsat_qa_collection_pre(qa_band, spacecraft_id)
        if collection == "01":
            masks, labels = landsat.landsat_qa_collection_01(qa_band, spacecraft_id, sensor_id)
        return masks, labels