# Enable autoreload, see: https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html?highlight=autoreload
c.InteractiveShellApp.extensions = ['autoreload']
c.InteractiveShellApp.exec_lines = ['%load_ext autoreload', '%autoreload 2']

# https://github.com/anntzer/ipython-autoimport
c.InteractiveShellApp.exec_lines.append(
    "try:\n    %load_ext ipython_autoimport\nexcept ImportError: pass"
)
