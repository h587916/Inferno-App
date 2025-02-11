# Inferno-App

This repository contains a PySide6 application that integrates Python and R functionality using the [Inferno R package](https://github.com/pglpm/inferno). Below you will find a detailed step-by-step guide to get the app running locally on your machine. Instructions are provided for Windows, macOS, and Linux.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
   - [Install Python 3.12](#install-python-312)
   - [Install R 4.4.2 and Inferno Package](#install-r-442-and-inferno-package)
2. [Set R_HOME Environment Variable (if required)](#set-r_home-environment-variable-if-required)
3. [Clone the Repository](#clone-the-repository)
4. [Create a Python Virtual Environment](#create-a-python-virtual-environment)
5. [Install Python Dependencies](#install-python-dependencies)
6. [Run the App](#run-the-app)

---

## 1. Prerequisites

### Install Python 3.12
**Windows**
1. Download the installer from [python.org](https://www.python.org/downloads/).
2. Run the installer, check “Add Python to PATH,” and follow the steps.
3. Verify the installation by opening Command Prompt and running:
   ```bash
   python --version
   ```

**macOS**
1. Download the macOS installer from [python.org](https://www.python.org/downloads/).
2. Run the installer and follow the steps.
3. Verify:
   ```bash
   python3 --version
   ```

**Linux**
1. Use your distribution's package manager or download the source from [python.org](https://www.python.org/downloads/). For Ubuntu/Debian, you may need to add a PPA or download a `.tar.xz` source package if Python 3.12 is not in the official repositories yet.
2. Example (Ubuntu) - (adjust if 3.12 is not in the official repos):
   ```bash
   sudo apt update
   sudo apt install python3.12 python3.12-venv python3.12-dev
   ```
3. Verify:
   ```bash
   python3.12 --version
   ```

---

### Install R 4.4.2 and Inferno Package
You need to install [R 4.4.2](https://cran.r-project.org/) and then install the **Inferno** package from GitHub.

1. **Download and install R 4.4.2**:
   - [Windows](https://cran.r-project.org/bin/windows/base/)
   - [macOS](https://cran.r-project.org/bin/macosx/)
   - [Linux](https://cran.r-project.org/bin/linux/)

2. **Install the `remotes` package** within R, then use `remotes` to install **Inferno**:
   1. Launch R (e.g., open **R.exe** on Windows, or run `R` in a terminal).
   2. Run the following lines:
      ```r
      install.packages("remotes")
      remotes::install_github("pglpm/inferno")
      ```
   3. Close R after the installation completes.

---

## 2. Set R_HOME Environment Variable (if required)
On some systems (especially on Windows), you may need to explicitly set the `R_HOME` environment variable to point to your R installation path.

- **Windows**:
  1. Open Control Panel → System and Security → System → Advanced system settings.
  2. Click **Environment Variables**.
  3. Under **System variables**, click **New** (or **Edit** if R_HOME exists).
  4. Variable name: `R_HOME`
  5. Variable value: Path to your R installation (e.g., `C:\Program Files\R\R-4.4.2`).
  6. Click **OK** to save.

- **macOS/Linux**:  
  You usually do **not** need to do this if `R` is in your default path. If you need to set it manually:
  ```bash
  export R_HOME="/usr/local/lib/R"
  ```
  Adjust the path to match your R installation.

---

## 3. Clone the Repository
Clone this repository using Git:

```bash
git clone https://github.com/h587916/Inferno-App.git
cd Inferno-App
```

---

## 4. Create a Python Virtual Environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Note**: Depending on your system, you may need to use `python3.12` instead of `python3`.

---

## 5. Install Python Dependencies

Install all required Python dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## 6. Run the App

Finally, start the application:

```bash
python main.py
```

The PySide6 app should now launch and be ready for use!

---

## Troubleshooting

- **R not found**: Ensure `R_HOME` is set properly on Windows or that your R binary is discoverable on macOS/Linux.
- **Package installation issues**: Ensure you have the latest versions of pip and setuptools:
  ```bash
  pip install --upgrade pip setuptools
  ```
- **Permission errors**: Try running terminal or command prompt as administrator (Windows) or use `sudo` on Linux/macOS (though generally recommended only if absolutely necessary).

---

**Enjoy using Inferno-App!**
