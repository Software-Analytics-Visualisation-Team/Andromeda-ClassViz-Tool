# ClassViz-Tool

## Set up:
1. Setup a local Galaxy instance.
2. Go to the directory `galaxy/tools/moonshot/` and clone this repository (Create the moonshot directory if it doesn't exist yet)
3. Change the galaxy tool configuration at `galaxy/config/tool_conf.xml.sample` by adding:
   ```
   <section name="Moonshot" id="moonshot">
     <tool file="moonshot/ClassViz-Tool/classviz.xml" />
   </section>
   ```
   
## How to use the tool:
1. Build and run Galaxy as normal.
2. Navigate on the left `Tools column > Moonshot > ClassViz-Tool`.
3. Upload a SVIF JSON file.
4. Click on "Run Tool".
5. Copy the display link (http://127.0.0.42:7800/) and open it in a new tab.
6. If the input file is not a JSON file, or not in SVIF file format, then the job fails with an error message.
4. Delete the job once done to kill the server that hosts ClassViz, or with the cmd `$ pkill -9 -f 'python3 -m http.server -b 127.0.0.42 7800'`
   **Note that if the server is not killed, user cannot re-run the job as it would result in `[Errno 98] Address already in use`


## How to run unit tests
Run the command: 
```
python -m unittest discover -s tests
```
Add `-v` flag at the end for more detailed testing <br/>
Depending on how your python environment is set up the command can also be:
```
python3 -m unittest discover -s tests
```


## Implementation progress:
- [x] Robustness (e.g. when user inputs a non-JSON file)
- [x] Download the input JSON file from Galaxy to classviz/data folder
- [x] Add script to load input JSON file when opening classviz
