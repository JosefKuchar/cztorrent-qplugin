# cztorrent-qplugin

QBittorrent CzTorrent plugin

Paste this into your developer console in your browser after logging in to get cookies variable

```
struct={};document.cookie.split('; ').map(line => line.split('=')).forEach(line => { struct[line[0]]=line[1]; } );`cookies = ${JSON.stringify(struct)}`
```
