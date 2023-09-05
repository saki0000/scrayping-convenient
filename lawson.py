import os
import re

import cv2
import firebase_admin
import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, storage


def main():
    JSON_PATH="caloriereceipt-firebase-adminsdk-c6qz7-9a21a73fbe.json"
    cred = credentials.Certificate(JSON_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    top_url="https://www.lawson.co.jp/recommend/"
    main_url="https://www.lawson.co.jp"

    top_res=requests.get(top_url)
    top_soup=BeautifulSoup(top_res.content,"html.parser")

    category_links=[e.attrs["href"] for e in top_soup.find(class_="contentsNav4").find_all("a")]


    for c_link in category_links:
        category_res=requests.get(main_url+c_link)
        c_soup=BeautifulSoup(category_res.content,"html.parser")
        productList=c_soup.find(class_="productList")
        menu=c_soup.find(class_="contentsNav2")
            
        print(menu)
        if productList is not None:
            products=productList.find("ul",class_="col-4").find_all("li")

            if menu is not None:
                menuList=[main_url+e.attrs["href"] for e in menu.find_all(href=re.compile('index.html'))]
                for menu in menuList:
                    menu_res=requests.get(menu)
                    m_soup=BeautifulSoup(menu_res.content,"html.parser")
                    products+=m_soup.find(class_="productList").find("ul",class_="col-4").find_all("li")


            for product in products:
                calorie=product.find(text=re.compile("kcal"))
                if calorie is None:
                    calorie=0
                else:
                    calorie=re.search(r'当り(.+)kcal',calorie).group(1) if re.search(r'当り(.+)kcal',calorie) is not None else re.findall(r'\d+', calorie)[0]
                name=product.find(class_="ttl").contents[0].encode("utf-8").decode("utf-8", errors="ignore")
                img=main_url+product.a.img.attrs["src"]
                calorie=int(calorie)
                wordArray=list(name)
                wordsMap={}
                for w in wordArray:
                    wordsMap[w]=True
                    wordsMap[w.translate(table)]=True

                path,image_name=downloadImage(img)
                image_url=uploadStorage(image_name,path)
                putFirestore(name,calorie,wordsMap,image_url)
                
                print(img)
                print(name)
                print(img)
                print(calorie)


def downloadImage(url):
    save_dir="/Users/kouseihujisaki/Desktop/web/scryping-convenient-products/products"

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    fname = os.path.basename(url)
    save_picture = save_dir + "/" + fname     #画像ファイルのパスを作成
    r = requests.get(url)
    with open(save_picture, "wb") as pi:
        pi.write(r.content)
        print("save:", save_picture)
    return save_picture,fname
    
def uploadStorage(name,path):

    bucket=storage.bucket("caloriereceipt.appspot.com")
    blob=bucket.blob(f"products/{name}")
    blob.upload_from_filename(path)
    blob.make_public()
    print(blob.public_url)
    print(blob.self_link)
    return blob.public_url

    
def putFirestore(name,calorie,wordsMap,imageURL):
    db = firestore.client()
    doc_ref = db.collection('products')
    doc_ref.add({
        'name': name,
        'calorie': calorie,
        'wordsMap': wordsMap,
        'imageURL':imageURL,
    })

kana={
    "ガ":"カ",
    "ギ":"キ",
    "グ":"ク",
    "ゲ":"ケ",
    "ゴ":"コ",
    "ザ":"サ",
    "ジ":"シ",
    "ズ":"ス",
    "ゼ":"セ",
    "ゾ":"ソ",
    "ダ":"タ",
    "ヂ":"チ",
    "ヅ":"ツ",
    "デ":"テ",
    "ド":"ト",
    "バ":"ハ",
    "ビ":"ヒ",
    "ブ":"フ",
    "ベ":"ヘ",
    "ボ":"ホ",
    "が":"か",
    "ぎ":"き",
    "ぐ":"く",
    "げ":"け",
    "ご":"こ",
    "ざ":"さ",
    "じ":"し",
    "ず":"す",
    "ぜ":"せ",
    "ぞ":"そ",
    "だ":"た",
    "ぢ":"ち",
    "づ":"つ",
    "ぜ":"せ",
    "ぞ":"そ",
    "ば":"は",
    "び":"ひ",
    "ぶ":"ふ",
    "べ":"へ",
    "ぼ":"ほ",
    "(":"（",
    ")":"）",
    "（":"(",
    "）":")",
}
table=str.maketrans(kana)


if __name__ == '__main__':
    main()