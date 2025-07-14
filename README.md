# ClassViz-Tool README

## Overview

**ClassViz-Tool** is a Galaxy *Interactive Tool* that:

* **Validates** SVIF (Simple Visualization Input Format) JSON files against a built‑in schema.
* **Copies** the validated JSON into the tool’s data directory for visualization.
* **Serves** an HTML/JavaScript/CSS interface on a local HTTP server (default port **7800**).

After execution, Galaxy shows a link pointing to the interactive visualization served by ClassViz.

---

## 1. Prerequisites

* A working Galaxy instance (tested with Galaxy release **23.0+**).
* **Docker** installed and running (required to build & run the ClassViz container).
* **Node ≥ 18** (only for the `gx‑it‑proxy` helper).
* Basic familiarity with the command line and with restarting Linux services (`systemctl`).

---

## 2. Installation

### 2.1 Clone the repository

```bash
cd galaxy/tools
mkdir -p moonshot && cd moonshot
git clone https://github.com/your-org/ClassViz-Tool.git
```

### 2.2 Register the tool in Galaxy

1. Open `galaxy/config/tool_conf.xml` (or `.sample`).
2. Add the following inside a `<section>` block:

```xml
<section name="Moonshot" id="moonshot">
  <tool file="moonshot/ClassViz-Tool/classviz.xml" />
</section>
```

### 2.3 Build the Docker image

```bash
cd ClassViz-Tool
docker build -t classviz:latest .
```

---

## 3. Galaxy Configuration

> **Tip :** All example configuration snippets live under [`config_files`](config_files/).

### 3.1 `galaxy.yml`

Add or verify the following entries:

```yaml
gravity:
  gx_it_proxy:
    enable: true
    port: 4002

galaxy:
  job_config_file: config/job_conf.yml

  interactivetools_enable: true
  interactivetools_map: database/interactivetools_map.sqlite
  interactivetools_proxy_host: localhost:4002 # Locally
  interactivetools_upstream_proxy: false # Locally

  outputs_to_working_directory: true
  galaxy_infrastructure_url: http://localhost:8080 # Locally
```

### 3.2 `job_conf.yml`

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

execution:
  default: default
  environments:
    default:           # non‑interactive tools
      runner: local
      docker_enabled: false
      interactive: false
```

If you still work with XML, a reference XML-based job configuration (`job_conf.xml`) is still available under `config_files/classviz` if you need them.

Full examples are available under  
- [config_files/galaxy.yml](config_files/galaxy.yml)  
- [config_files/job_conf.yml](config_files/job_conf.yml)
- [config_files/job_conf.xml](config_files/job_conf.xml)

### 3.3 Interactive‑Tool system setup

Some pieces sit *outside* of the tool itself and must be installed at the system level.

#### 3.3.1 Install & run the **gx‑it‑proxy**

```bash
# One‑time install (requires npm)
npm install -g @galaxyproject/gx-it-proxy
```

Create or edit the systemd unit `galaxy-gx-it-proxy.service` (usually via `sudo systemctl edit galaxy-gx-it-proxy.service`) so that the **ExecStart** line contains :

```ini
ExecStart=/usr/local/bin/gx-it-proxy --ip 127.0.0.1 --port 4002 \
  --sessions /srv/galaxy/var/interactivetools_map.sqlite \
  --proxyPathPrefix /interactivetool/ep --verbose
```

> **Why `/srv/galaxy/var`?** Anything under `var/` is writable by Galaxy, letting the proxy store its session DB.

Reload and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart galaxy-gx-it-proxy.service
```

#### 3.3.2 Nginx reverse‑proxy rule

Append the following block to your Galaxy server (e.g. `/etc/nginx/sites-enabled/galaxy`) before your `location / {`:

```nginx
location ~* ^/interactivetool/ep/(.+)$ {
    proxy_pass         http://127.0.0.1:4002;
    proxy_http_version 1.1;
    proxy_set_header   Host $host;
    proxy_set_header   Upgrade $http_upgrade;
    proxy_set_header   Connection "upgrade";
    proxy_read_timeout 3600s;
}
```

Restart Nginx:

```bash
sudo systemctl reload nginx
```

With the proxy and the web rule in place, Galaxy can expose interactive tools under `/interactivetool/ep/…`.

---

## 4. Usage

1. **Start Galaxy**

   ```bash
   sh run.sh
   ```
2. **Launch ClassViz‑Tool** in the Galaxy UI:
   **Tools ▶ Moonshot ▶ ClassViz‑Tool**.
3. **Upload SVIF JSON**

   * Choose your `.json` file and click **Run**.
4. **View the visualization**

   * Galaxy will display a message:

     ```
     ClassViz running… go to User > Interactive Tools
     ```
   * Click **User ▶ Active Interactive Tools**, then click **ClassViz**.

Galaxy starts and stops the HTTP server automatically.

---

## 5. Internals

### 5.1 File paths

* **Input JSON**: provided by Galaxy as `input.json`.
* **Copied File**: `data/input.svif` inside the container.

### 5.2 Main command (`classviz.xml`)

In `classviz.xml`:

```xml
<command detect_errors="exit_code">
  <![CDATA[
    python /opt/classviz/classviz.py "$input" \
      "/opt/classviz/data/input.svif"
  ]]>
</command>
```

• `$input` = uploaded file path
• `data/input.svif` = validated copy.

### 5.3 Validation & copy

The Python script loads JSON, validates it against **SVIF\_SCHEMA**, then writes identical bytes to `/opt/classviz/data/input.svif`.

### 5.4 HTTP server

* Uses Python’s `ThreadingHTTPServer` to serve the `tool_dir` folder.
* Reads port from `GALAXY_IT_PORT` (default **7800**).
* Accessible from the **User ▶ Active Interactive Tools**

---

## 6. Testing

Run all unit tests (schema, copy, server startup):

```bash
python3 -m unittest discover -v tests
```

---

## 7. Debug notes

| Symptom                                                                                            | Possible cause                                                  | Quick fix                                                                                                                                                                                                                                     |                                                            |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Random "file not found" errors; some ClassViz jobs executed on the *host* runner instead of Docker | An old handler process still maps **classviz → default runner** | Fully stop **all** handler units, then start them again so they reload `job_conf.yml`:<br>`sudo systemctl stop galaxy-handler@0.service galaxy-handler@1.service`<br>`sudo systemctl start galaxy-handler@0.service galaxy-handler@1.service` |                                                            |
| Handlers (or Gunicorn workers) stick around after a restart                                        | orphaned `main.py` processes                                    | Stop the units, check with \`ps aux grep main.py\`, kill leftovers, then start the units again |
| Docker "permission denied" when Galaxy tries to spawn the container                                | Galaxy service user not in the **docker** group                 | `sudo usermod -aG docker galaxy_usr`<br>Log out and back in *or* restart the Galaxy service                                                                                                                                                 
| `job_conf.yml` seemingly ignored                                                                   | `job_config:` is already specified *inline* in `galaxy.yml`     | Comment out the inline section **or** move your interactive & default runners there                                                                                                                                                         

> These notes cover the most common issues encountered in production. If the automated tasks above fail for any reason, you can reproduce each step manually using the same commands.

---

## 8. Implementation progress

* [x] Robustness (non‑JSON upload handling)
* [x] Download uploaded JSON into `classviz/data`
* [x] Auto‑load input file when opening the viewer
* [ ] **Upcoming**: Live‑reload when the SVIF file changes

*Last updated: July 2025*
