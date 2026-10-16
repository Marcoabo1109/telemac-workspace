#/bin/bash

run_telfile.py alter -f -1 vnv_saint_lawrence-t2d/vnv1_seq/S9.gfortran/r2d_stlawrence.slf f2d_stlawrence.slf
run_telfile.py alter -f -1 vnv_saint_lawrence-t2d/vnv1_seq/S9.gfortran/ice_stlawrence.slf fce_stlawrence.slf

run_telfile.py alter -f -1 vnv_saint_lawrence-t2d/vnv2_seq/S9.gfortran/r2d_stlawrence.slf f2d_stlawrence_dynice.slf
run_telfile.py alter -f -1 vnv_saint_lawrence-t2d/vnv2_seq/S9.gfortran/ice_stlawrence.slf fce_stlawrence_dynice.slf
