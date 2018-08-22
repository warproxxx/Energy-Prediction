from downloader import download
from cleaner import cleaner


# historicDownloader = download("http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13061&reportTitle=Historical%20RTM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey", "historic")
# historicDownloader.perform_download()

# liveDownloader = download("http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12301&reportTitle=Settlement%20Point%20Prices%20at%20Resource%20Nodes,%20Hubs%20and%20Load%20Zones&showHTMLView=&mimicKey", "live")
# liveDownloader.perform_download()

#assert downloading has completed

#cleaner().clean()
#assert files are removed, new file is created