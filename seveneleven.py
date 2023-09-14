# requests及びbs4を必ずインポートする
import asyncio
import datetime
import os
import re

import firebase_admin
import pykakasi
import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, storage

kks = pykakasi.kakasi()

# HTMLの取得先として当サイトを指定する
def main():
    JSON_PATH="caloriereceipt-firebase-adminsdk-c6qz7-9a21a73fbe.json"
    top_url="https://www.sej.co.jp/products/#category"
    main_url="https://www.sej.co.jp"

    cred = credentials.Certificate(JSON_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    top_res=requests.get(top_url)
    soup = BeautifulSoup(top_res.text, "html.parser")
    categories=soup.find(class_="productCategoryList").find_all("li")
    category_links=[elem.a.attrs['href'] for elem in categories]

    res=requests.get("https://www.sej.co.jp/products/a/item/041568/")
    test_soup = BeautifulSoup(res.text, "html.parser")
    categories=test_soup.find(class_="slideWrap").li.img.attrs['src']
    print(categories)

    for c_link in category_links:
        print(main_url+c_link)
        category_res=requests.get(main_url+c_link)
        c_soup=BeautifulSoup(category_res.text,"html.parser")
        products=c_soup.find_all(class_="list_btn")
        products_links=[elem.div.div.a.attrs['href'] for elem in products]

        for p_link in products_links:
            print(main_url+p_link)
            product_res=requests.get(main_url+p_link)
            p_soup=BeautifulSoup(product_res.text,"html.parser")
            detail_links=[]
            get_previous_page(p_soup,detail_links,main_url)

            for d_link in detail_links:
                
                detail_res=requests.get(main_url+d_link)
                d_soup=BeautifulSoup(detail_res.text,"html.parser")
                name=str(d_soup.find(class_='item_ttl').h1.contents[0])
                
                print(name)
                wordArray=list(name)
                result = kks.convert(name)
                kana=""
                for w in result:
                    kana+=w["kana"]
                wordArray+=kana
                wordsMap={"P":True}
                for w in wordArray:
                    wordsMap[w]=True
                    wordsMap[w.translate(table)]=True

                image=""
                if d_soup.find(class_='productWrap') is not None:
                    image=d_soup.find(class_='productWrap').ul.li.img.attrs['src']
                else:
                    image=d_soup.find(class_="slideWrap").li.img.attrs['src']
                    print(d_soup.find_all(class_="slick_active"))
                
                
                calorie=d_soup.find(text=re.compile("kcal"))
                if calorie is None:
                    calorie=0
                else:
                    pattern = r'：(.+?)kcal'  # []で囲まれた文字列を抽出する正規表現
                    match = re.search(pattern, calorie)
                    calorie = int(match.group(1).replace(",",""))

                print(calorie)
                
                

                path,image_name=downloadImage(image)
                image_url=uploadStorage(image_name,path)
                putFirestore(name,calorie,wordsMap,image_url)


def get_previous_page(soup,detail_links,main_url)->list:
    new_links=[e.p.a.attrs['href'] for e in soup.find_all(class_="item_ttl")]
    detail_links+=new_links
    if soup.find(class_="pager") is None:
        return detail_links
    pages=soup.find(class_="pager").find_all("li")
    has_next=False
    next_url=""
    for p in pages:
        if p.string=="［次へ］":
            has_next=True
            next_url=p.a.attrs["href"]
    
    if has_next:
        product_res=requests.get(main_url+next_url)
        p_soup=BeautifulSoup(product_res.text,"html.parser")
        get_previous_page(p_soup,detail_links,main_url)
    else:
        return detail_links
    
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
    "1":"１",
    "2":"２",
    "3":"３",
    "4":"４",
    "5":"５",
    "6":"６",
    "7":"７",
    "8":"８",
    "9":"９",
    "(":"（",
    ")":"）",
    "（":"(",
    "）":")",
}
table=str.maketrans(kana)


if __name__ == '__main__':
    main()
