import os
from apps.supplier.models import Supplier


def  get_innovert_xml():
    supplier = Supplier.objects.get(slug="promsiteh")
    urls_xml = os.environ.get("PRST_XML")
    urls_xml_arr = urls_xml.split(", ")
    print(envs)
    for url in urls_xml_arr:
        response  = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("offer")
  

def get_innovert_xlsx_stock():
    pass