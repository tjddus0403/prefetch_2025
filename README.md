# cLSTM Prefetcher

### ⚙️ Environment Setting
_Language :_ Python 3.9.21
```bash
pip install -r requirements.txt
```
***
### 📁 Traces
0. Create directories for trace files
  ```bash
  mkdir -p simulator/traces/{ChampSim_trace,paddr,vaddr} simulator/traces/paddr/{astar,bc,bfs,cc,mcf,pr,sssp}
  ```
1. Download the trace files from (https://github.com/Quangmire/ChampSim)
- From *ML-DPC > LoadTraces > gap* : ['bc-0.txt.xz', 'bfs-3.txt.xz', 'cc-5.txt.xz', 'pr-5.txt.xz', 'sssp-5.txt.xz']
- From *ML-DPC > LoadTraces > spec17* : ['mcf-s4.txt.xz']
- From *ML-DPC > LoadTraces > spec06* : ['astar-s2.txt.xz']
2. Move the downloaded files to ***simulator/traces/ChampSim_trace*** folder
  ```bash
  mv <trace_files> simulator/traces/ChampSim_trace
  ```
3. Generate ***.paddr*** files using ***simulator/traces/get_trace.py***
  ```bash
  cd simulator/traces
  python3 get_trace.py
  ```
4. Split the _**.paddr**_ files into [1M, 3M, 4M] sizes using ***simulator/traces/split_data.sh***
  ```bash
  ./split_data.sh
  ```
***
### 🗂️ Data Collection (아직 미완성)
Use the simulator to generate training data for the model

0. Create directories for data collection
  ```bash
  mkdir -p data/{csv,raw}
  ```
1. Set the trace name, data collection flag in _**settings.py** _
- Open _**simulator/settings.py**_
- Set the TRACE variable to the trace file name you want to simulate
- Set self.collect to True for data collection
  ```python
  self.collect = True
  TRACE = "astar" # Example
  ```
2. Use the **Leap Prefetcher** for data collection
- Available prefetcher options are defined in _**simulator/prefetcher_info.py**_
  ```bash
  cd simulator
  python3 main.py 3
  ```
3. Create _**.csv**_ files for model training
- Open _**data/r2c.py**_
- Set the trace variable to the trace file name
  ```python
  trace = "astar" # Example
  ```
- Generate ***.csv*** files using ***data/r2c.py***
  ```bash
  cd data
  python3 r2c.py
  ```
***
### 📍 Model Training
1. Set the trace name in _**setting.py** _
- Open _**setting.py**_
- Set the trace variable to the trace file name
  ```python
  trace = "astar" # Example
  ```
2. Train the model
  ```bash
  python3 train.py
  ```
***
### 📍 Model Prediction
Use the trained cLSTM model to predict and extract result

0. Create directories for model's prediction
  ```bash
  mkdir -p results/{clstm_leap,clstm_only,delta,seq_leap,seq_only}
  ```
1. Run the test file to get the model's prediction
  ```bash
  python3 test.py
  ```
***
### 📊 Simulation
1. Set the trace name, data collection flag in _**settings.py** _
- Open _**simulator/settings.py**_
- Set the TRACE variable to the trace file name you want to simulate
- Set self.collect to True for data collection
  ```python
  self.collect = False # for simulation
  TRACE = "astar" # Example
  ```
2. Use the **cLSTM Prefetcher** for simulation
- Available prefetcher options are defined in _**simulator/prefetcher_info.py**_
  ```bash
  cd simulator
  python3 main.py 5
  ```
🔄 If you also have results for [_delta-lstm, cstate_only, seq_leap, seq_only_], you can get the results for all prefetchers by running exec.sh
```bash
./exec.sh
```
 
