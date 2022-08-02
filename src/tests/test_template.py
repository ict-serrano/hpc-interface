import pytest
import hpc.api.utils.template as template

@pytest.fixture
def hpc_service_params():
    return {
        "icase": 6,
        "id": 1,
        "Kalman_Filter": 1,
        "FFT_Filter": 1,
        "MinMaxTransform": 1,
        "R": 11,
        "R_range_offset": 0,
        "R_range_endset": 100,
        "workspace": "/home/javad/Desktop/SERRANO/serrano/serrano/serrano/data",
        "readInputData": "/Input_Data/IDEKO.csv",
        "binaryDataSignalPath": "/Input_Data/binaryInputData",
        "kalmanDataPath": "/Output_Data/KalmanFilter",
        "fftDataPath": "/Output_Data/FFTFilter",
        "minMaxDataPath": "/Output_Data/MinMaxUpdate",
        "binaryDataKNN": "/Input_Data/KNNbin",
        "binaryDataDTWx": "/Input_Data/DTWx",
        "binaryDataDTWy": "/Input_Data/DTWy",
        "binaryBSholes": "/Input_Data/DTWx",
        "num_MPI_Procs": 4,
        "numCommunicatoi": 4,
        "num_Thread": 1,
        "num_numa": 1,
        "num_core_numa": 4,
        "exe": "build/Seranno",
    }

def test_hpc_service_params_included(hpc_service_params):
    rendered_template = template.render(hpc_service_params)
    for param in hpc_service_params:
        assert param in rendered_template