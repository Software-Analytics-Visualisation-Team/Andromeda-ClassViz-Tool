## ClassViz-Tool README

### Overview

ClassViz-Tool is a Galaxy Interactive Tool that:

* **Validates** SVIF (Simple Visualization Input Format) JSON files against a built-in schema.
* **Copies** the validated JSON into the tool’s data directory for visualization.
* **Serves** an HTML/JavaScript/CSS interface on a local HTTP server (default port **7800**).

After running the tool, you will see a link in Galaxy pointing to the interactive visualization served by ClassViz.

---

### 1. Prerequisites

* A working Galaxy instance (tested with Galaxy release 23.0+).
* Docker installed for building the ClassViz container.
* Basic familiarity with the command line.

---

### 2. Installation

1. **Clone Repository**

   ```bash
   cd galaxy/tools
   mkdir -p moonshot && cd moonshot
   git clone https://github.com/your-org/ClassViz-Tool.git
   ```
2. **Register Tool in Galaxy**

   * Open `galaxy/config/tool_conf.xml` (or `.sample`).
   * Add the following inside a `<section>` block:

     ```xml
     <section name="Moonshot" id="moonshot">
       <tool file="moonshot/ClassViz-Tool/classviz.xml" />
     </section>
     ```
3. **Build Docker Image**

   ```bash
   cd ClassViz-Tool
   docker build -t classviz:latest .
   ```
---

### 3. Specific configuration
Your Galaxy configuration now requires specific settings under the `gravity` section of your `config/galaxy.yml`. Add or verify the following entries:

```yaml
gravity:
  gx_it_proxy:
    enable: true
    port: 4002
```

And you will also need these settings under the 'galaxy' section : 
```yaml
galaxy:
  job_config_file: config/job_conf.yml

  interactivetools_enable: true
  interactivetools_map: database/interactivetools_map.sqlite
  interactivetools_proxy_host: localhost:4002
  interactivetools_upstream_proxy: false

  outputs_to_working_directory: true
  galaxy_infrastructure_url: http://localhost:8080
```
A full example is available under config_files/galaxy.yml

### Job Configuration (`job_conf.yml`)

Galaxy now prefers a YAML-based job configuration. In your `config/job_conf.yml` (create or edit this file), define an environment for interactive tools and assign it to the ClassViz tool:

```yaml
environments:
  docker_env:
    runner: local
    docker_enabled: true
    interactive: true
    docker_set_user: root
tools:
  - id: "classviz"
    environment: docker_env
```
Don't forget you will need an environment for your non-interactive tools like :

```yaml
execution:
  default: default
  environments:
    # Non interactive tools
    default:
      runner: local
      docker_enabled: false 
      interactive: false      
```
A full example is available under config_files/classviz/job_conf.yml
If you still work with XML, a reference XML-based job configuration (`job_conf.xml`) is still available under `config_files/classviz` if you need them.


---

### 4. Usage

1. **Start Galaxy**

   ```bash
   sh run.sh
   ```
2. **Launch ClassViz-Tool**

   * In Galaxy’s left sidebar: **Tools ▶ Moonshot ▶ ClassViz-Tool**.
3. **Upload SVIF JSON**

   * Choose your `.json` file and click **Run**.
4. **View Visualization**

   * After validation, Galaxy will display a link with:

     ```xml
     ClassViz running… go to User > Interactive Tools
     ```
   * Click **User ▶ Active Interactive Tools**, then select **ClassViz** to open the viewer.

Galaxy handles starting and stopping the HTTP server automatically.

---

### 5. Internals

#### 5.1 File Paths

* **Input JSON**: provided by Galaxy as `input.json`.
* **Copied File**: `data/input.svif` inside the container.

#### 5.2 Main Command

In `classviz.xml`:

```xml
<command detect_errors="exit_code">
  <![CDATA[
    python /opt/classviz/classviz.py "$input" \
      "/opt/classviz/data/input.svif"
  ]]>
</command>
```

* `$input`: path to the uploaded file
* `data/input.svif`: where the validated copy is stored

#### 5.3 Validation & Copy

* The script loads JSON and checks it against the built-in SVIF\_SCHEMA.
* On success, it writes the same JSON bytes to `/opt/classviz/data/input.svif`.

#### 5.4 HTTP Server

* Uses Python’s `ThreadingHTTPServer` to serve the `tool_dir` folder.
* Reads port from `GALAXY_IT_PORT` (default **7800**).
* Accessible from the **User ▶ Active Interactive Tools**
---

### 6. Testing

Run all unit tests (schema, copy, server startup):

```bash
python3 -m unittest discover -v tests
```
---

## Implementation progress:
- [x] Robustness (e.g. when user inputs a non-JSON file)
- [x] Download the input JSON file from Galaxy to classviz/data folder
- [x] Add script to load input JSON file when opening classviz

*Last updated: July 2025*
