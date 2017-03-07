from bs4 import BeautifulSoup
soup = BeautifulSoup('<html><body><p class="class1"></div><i class="class1"></i><img class="class2"></span><p class="class1"></div></body></html>', "html.parser")

for e in soup.find_all(["p", "img"]):
    print e