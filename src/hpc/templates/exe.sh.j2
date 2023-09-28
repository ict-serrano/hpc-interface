#!/bin/bash
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH -t 0-01:00 # Runtime in D-HH:MM
#SBATCH --cpus-per-task=1 # Request that ncpus be allocated per process
#SBATCH --ntasks-per-node=128 # Max number of processes

{# Template parameters - schema for the template is in openapi spec

params = {
    # kernel
    icase: -1..3

    # Select a group of kernels, belonging to a use case 
    ideko_kernel: 0..1
    inbestme_kernel: 0..1

    # Pack the output into CSV
    csv_output: 0..1

    # signal processing - if icase == 1
    filter:
        kalman: 0..1 
        fft: 0..1
        min_max: 0..1
        savitzky_golay: 0..1
        black_scholes: 0..1
        wavelet: 0..1

    # kalman filter config
    kalman:
        r: 10
    
    # fft filter config
    fft: {}

    # min max filter config 
    min_max: {}

    # savitzky golay filter config
    savitzky_golay: {}

    # black scholes filter config
    black_scholes: {}

    # wavelet filter config
    wavelet: {}

    # kmean config
    kmean:
        cluster_number: 2
        epsilon_criteria: 0.00001
    
    # knn config
    knn:
        cluster_number: 2
        k_nearest_neighbor: 7
    
    # benchmark state
    benchmark_state: 0

    # parallelization parameters
    num_mpi_procs: 4
    num_thread: 1

    # approximation computing techniques
    perforation_stride: 1

    # transprecision techniques
    precision_scenario: 1

    # hardware config
    num_numa: 8
    num_core_numa: 16

    # workspace
    root_dir: "${HOME}/serrano"
    workspace: "/data"
    profiling_workspace: "/profile"

    # data path
    read_input_data: "/Init_Data/raw_data_input_fft/acceleration_cycle_260.csv"
    input_data_double: "/Input_Data/Double_Data_Type/signalFilter"
    input_data_float: "/Input_Data/Float_Data_Type/signalFilter"
    inference_knn_path: "/Init_Data/inference_data_position/"
    clustering_label_path: "/Output_Data/KMean/KMean_cluster.csv"

    # exe path
    exe: "build/SERRANO"
}

#}

# Selecting the kernel
# -1: Clear the binary data
#  0: (packing2CSVformat=0) Read the original csv file and make binary signal,
#  0: (packing2CSVformat=1) Read binary output files and make output csv
#  1: Signal processing
#  2: KMean clustering
#  3: KNN classification  
icase={{ params.icase }}

# Select a group of kernels, belonging to a use case
IDEKO_Kernel={{ params.ideko_kernel }}
INBestMe_Kernel={{ params.inbestme_kernel }}

# Packing the into CSV format
# Must be 0 for icase in [-1, 1, 2, 3]
packing2CSVformat={{ params.csv_output }}

# Benchmark state
BenchmarkState={{ params.benchmark_state }}

# Applying specific filter (1: filter apply, 0: filter does not apply)
Kalman_Filter={{ params.filter.kalman }}
FFT_Filter={{ params.filter.fft }}
MinMax_Transform={{ params.filter.min_max }}
SavitzkyGolay_Transform={{ params.filter.savitzky_golay }}
BlackScholes={{ params.filter.black_scholes }}
WaveletFiltering={{ params.filter.wavelet }}

# Kalman filter parameters
R={{ params.kalman.r }}

# KNN parameters
K_nearest_neighbor={{ params.knn.k_nearest_neighbor }}
Cluster_number_KNN={{ params.knn.cluster_number }}

# KMean parameters
number_cluster_kmean={{ params.kmean.cluster_number }}
epsilon_criteria={{ "%.8f" | format(params.kmean.epsilon_criteria) }}

# Parallelization parameters
num_MPI_Procs={{ params.num_mpi_procs }}
num_Thread={{ params.num_thread }}

# Approximation computing techniques
perforation_stride={{ params.perforation_stride }}

# Transprecision techniques
precision_scenario={{ params.precision_scenario }}

# Hardware configuration
num_numa={{ params.num_numa }}
num_core_numa={{ params.num_core_numa }}

# Setting up the workspace
root_dir={{ params.root_dir }}
workspace=${root_dir}{{ params.workspace }}
profiling_workspace=${root_dir}{{ params.profiling_workspace }}

# Path for input and output data
readInputData={{ params.read_input_data }}
inputDataDouble={{ params.input_data_double }}
inputDataFloat={{ params.input_data_float }}
inferenceKNNPath={{ params.inference_knn_path }}
clustering_label={{ params.clustering_label_path }}

EXE={{ params.exe }}

# changing to root dir
cd ${root_dir}

# loading modules
module load tools/cmake/3.21.5
module load compiler/gcc/11.2.0
module load mpi/openmpi/4.1.1-gcc-11.2.0
module load numlib/fftw/3.3.10-openmpi-4.1.1-gcc-11.2.0
# cd build
# source ../module/modNode01Exe.sh
# cd ..

# clear binary data: icase=-1
# packing2CSVformat must be zero
mpirun \
    --mca pml ob1 --mca btl tcp,self \
    --bind-to core \
    -n $num_MPI_Procs \
    $EXE \
    -1 $BenchmarkState \
    $Kalman_Filter $FFT_Filter \
    $BlackScholes $SavitzkyGolay_Transform \
    $R \
    $K_nearest_neighbor $Cluster_number_KNN \
    $number_cluster_kmean $epsilon_criteria \
    $perforation_stride $precision_scenario \
    $num_numa $num_core_numa \
    $num_Thread \
    $workspace $profiling_workspace \
    $readInputData $inputDataDouble $inputDataFloat $inferenceKNNPath \
    $IDEKO_Kernel $INBestMe_Kernel 0 \
    $WaveletFiltering $clustering_label

# generate binary data: icase=0
# in this case packing2CSVformat must be zero, since we generate binary
mpirun \
    --mca pml ob1 --mca btl tcp,self \
    --bind-to core \
    -n $num_MPI_Procs \
    $EXE \
    0 $BenchmarkState \
    $Kalman_Filter $FFT_Filter \
    $BlackScholes $SavitzkyGolay_Transform \
    $R \
    $K_nearest_neighbor $Cluster_number_KNN \
    $number_cluster_kmean $epsilon_criteria \
    $perforation_stride $precision_scenario \
    $num_numa $num_core_numa \
    $num_Thread \
    $workspace $profiling_workspace \
    $readInputData $inputDataDouble $inputDataFloat $inferenceKNNPath \
    $IDEKO_Kernel $INBestMe_Kernel 0 \
    $WaveletFiltering $clustering_label

# run the kernel: icase=$icase
# in this case packing2CSVformat must be zero
mpirun \
    --mca pml ob1 --mca btl tcp,self \
    --bind-to core \
    -n $num_MPI_Procs \
    $EXE \
    $icase $BenchmarkState \
    $Kalman_Filter $FFT_Filter \
    $BlackScholes $SavitzkyGolay_Transform \
    $R \
    $K_nearest_neighbor $Cluster_number_KNN \
    $number_cluster_kmean $epsilon_criteria \
    $perforation_stride $precision_scenario \
    $num_numa $num_core_numa \
    $num_Thread \
    $workspace $profiling_workspace \
    $readInputData $inputDataDouble $inputDataFloat $inferenceKNNPath \
    $IDEKO_Kernel $INBestMe_Kernel 0 \
    $WaveletFiltering $clustering_label

{% if params.csv_output %}
# generate csv output data: icase=0
# in this case packing2CSVformat must be 1, since we generate csv
mpirun \
    --mca pml ob1 --mca btl tcp,self \
    --bind-to core \
    -n $num_MPI_Procs \
    $EXE \
    0 $BenchmarkState \
    $Kalman_Filter $FFT_Filter \
    $BlackScholes $SavitzkyGolay_Transform \
    $R \
    $K_nearest_neighbor $Cluster_number_KNN \
    $number_cluster_kmean $epsilon_criteria \
    $perforation_stride $precision_scenario \
    $num_numa $num_core_numa \
    $num_Thread \
    $workspace $profiling_workspace \
    $readInputData $inputDataDouble $inputDataFloat $inferenceKNNPath \
    $IDEKO_Kernel $INBestMe_Kernel 1 \
    $WaveletFiltering $clustering_label
{% endif %}