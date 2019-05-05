import requests,json,re
from bs4 import BeautifulSoup as bs

def banner():
    print("\n")
    print("#"*34)
    print("#\t iproperty Scraper \t #")
    print("#"*34)
    print("\n")

def htmldata(url):
    remote = requests.get(url)
    remoteFile = remote.text
    return remoteFile

def parsedata(datalink):
    dataa = json.loads(htmldata(datalink))["data"]
    for data in dataa:
        id = data['listingID']
        city = data["city"].replace(" ", "-")
        try:
            build = data["buildingName"].replace(" ", "-")
        except:
            build = None
            pass
        if build == None:
            proplink = "https://www.iproperty.com.my/property/{0}/sale-{1}".format(city,id)
        else:
            proplink = "https://www.iproperty.com.my/property/{0}/{1}/sale-{2}".format(city,build,id)
        if "true" in datalink:
            proplink = proplink.replace("sale-","rent-")
        proplinks.append(proplink)

def get(tag= '', class_='', Object=None, index=0):
    global out
    if class_:
        try:
            o = Object.find(tag, class_=class_).text
        except:
            o = "Null"
    else:
        try:
            o = Object[index].text
        except:
            o = "Null"
    return o

def propData(proplink):
    out = {}
    propId = proplink.split("-")[-1]
    print("[+] Fetching Property: {}".format(propId))
    out["ID"] = propId
    data = htmldata(proplink)
    soup = bs(data,"html.parser")

    summary = soup.find("div",class_="property-summary")
    out["price"] = get("div","property-price",summary)
    out["adress"] = get("span","property-address",summary)

    areas = summary.findAll("li",class_="sc-hSmEHG")
    out["built"] = areas[0].text.split(":")[1].strip()
    out["land"] = areas[1].text.split(":")[1].strip()
    prop = summary.find("ul",class_="property-features")
    listing = prop.findAll("li")
    out["room"] = get(Object=listing,index=0)
    out["bath"] = get(Object=listing,index=1)
    out["parking"] = get(Object=listing,index=2)
    out["description"] = get("pre","property-description",soup)
    return out


def agentData(agentUrl,ID):
    agentdataa = htmldata(agentUrl)
    soup = bs(agentdataa, "html.parser")
    section = soup.find("section", class_="fa-detail-profile fadetail-bcn")
    agentName = section.find("h2").text
    agentImg = section.find("img").get("src")
    agentmain = section.find("div", class_="ag-name").find("p")
    agentAG = agentmain.find("a").text
    agentRen = agentmain.find(text=re.compile("REN")).split("REN ")[1]
    agentMob = section.find("span", {"id": "agent-phone"}).find("a").get("onclick").split(";")[1].split(",")[1].replace(
        "\'", "").strip()
    agentdata["agentID"] = ID
    agentdata["agentName"] = agentName
    agentdata["agentRen"] = agentRen
    agentdata["agentAG"] = agentAG
    agentdata["agentMob"] = agentMob
    agentdata["agentImg"] = agentImg
    print("[+] Agent Name: {} \n".format(agentName))
    return agentdata


if __name__ == "__main__":
    banner()

    agentUrl = input("Enter Agent profile link: \n")
    # agentUrl = "https://www.iproperty.com.my/realestateagent/28336/eric-wang"


    agentID = agentUrl.split("/")[4]

    agentdata = {}
    agentData(agentUrl, agentID)

    SPropListsUrl = "https://www.iproperty.com.my/ajax_server/2016/agent/svr_agent_listing.ashx?AgentId={}&Size=10000".format(agentID)
    RPropListsUrl = "https://www.iproperty.com.my/ajax_server/2016/agent/svr_agent_listing.ashx?AgentId={}&IsRent=true&Size=10000".format(agentID)

    proplinks = []
    parsedata(SPropListsUrl)
    parsedata(RPropListsUrl)

    properties = []
    print("[+] Total Properties : {}".format(len(proplinks)))
    print("[+] Properties Details Fetcher starting : ")
    for proplink in proplinks:
        prodata = propData(proplink)
        # print(prodata)
        properties.append(prodata)

    agentdata["propertieslistinig"] = properties
    print("\n[+] All Properties has been Scraped.")

    with open(agentID + '.json', 'w') as outfile:
        json.dump(agentdata, outfile, indent=4)
    print("[+] job completed.")