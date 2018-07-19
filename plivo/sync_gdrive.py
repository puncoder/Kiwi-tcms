import subprocess
import io
import dateutil.parser
proc = subprocess.Popen(["gdrive", "list"], stdout=subprocess.PIPE)
files = {}
for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
    data = line.split()
    if data[1] == 'kiwi_Db.dump':
        date_time = dateutil.parser.parse(data[-2]+' '+data[-1])
        files[date_time] = data[0]

keep_file = sorted(files)[-5:]

for date, Fid in files.items():
    if date not in keep_file:
        proc = subprocess.Popen(["gdrive", "delete", Fid], stdout=subprocess.PIPE)

