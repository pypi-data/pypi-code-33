import nibabel


def anonymise(filename):
    try:
        nifti_file = nibabel.load(filename)

        hdr = nifti_file.get_header()
        if 'db_name' in hdr:
            hdr['db_name'] = 'XXXX'
        # else:
        # return {"error":"db_name not found, not anonymisable.", "OK":False}

        new_image = nibabel.Nifti1Image(nifti_file.get_data(), nifti_file.get_affine(), hdr)
        nibabel.save(new_image, filename)
        return {"OK": True}
    except Exception:
        return {"OK": False, "error": "Some NIFTI files are not accepted or are corrupted"}


def check_anonymised_file(filename):
    try:
        nifti_file = nibabel.load(filename)
        hdr = nifti_file.get_header()
        if 'db_name' in hdr and (str(hdr['db_name'].astype(str)) not in ['XXXX', '']):
            return {"OK": False}
        else:
            return {'OK': True}
    except Exception:
        return {"OK": False, "error": "Some NIFTI files are not accepted or are corrupted"}
