import psutil
import subprocess
import os

def get_django_processes():
    result = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'manage.py' in cmdline or 'runserver' in cmdline or 'gunicorn' in cmdline:
                mem = proc.info['memory_info']
                result.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'rss_mb': mem.rss / 1024 / 1024,
                    'vms_mb': mem.vms / 1024 / 1024,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return result

procs = get_django_processes()
if not procs:
    print("No Django process found. Is runserver running?")
else:
    for p in procs:
        print(f"PID {p['pid']} | RSS: {p['rss_mb']:.1f} MB | VMS: {p['vms_mb']:.1f} MB")