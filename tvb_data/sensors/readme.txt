
Naming convention:
- [sensor_type]_[provenance_or_type]_[number_of_sensors].[extension]
- all lower case



eeg_unitvector_62.txt.bz2
--------------------------

EEG sensor orientations and labeling.
They originate from http://www.brainproducts.com/

The orientations have been aligned with the tvb default surfaces, specifically rotated by -90 along +z.
( the transformation was done from the tvb h5 after import by tvb_data/sensors/view_h5_3d.py:_rotate_eeg_sensors )

