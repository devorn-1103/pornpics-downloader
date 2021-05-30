import os
import sys
import requests
from bs4 import BeautifulSoup

# mainループ
def main():
    choice = "download"

    if (len(sys.argv) == 1):
        # 引数が付与されていない場合は、使用方法を表示し以下のデフォルト値をセット
        make_help()
        CATEGORY_URL, DOWNLOAD_PAGE_NUM, choice = make_sample()
    elif (len(sys.argv) >= 2) and (sys.argv[1] == "--category"):
            get_category_list()
            choice = "view_category"
    elif (len(sys.argv) >= 2) and (sys.argv[1] == "--tag"):
            get_tag_list()
            choice = "view_tag"
    elif (len(sys.argv) >= 3):
        # 第一引数：カテゴリURL、第二引数：ダウンロードするページ数
        CATEGORY_URL = "https://www.pornpics.com/"+str(sys.argv[1])+"/"
        TAG_URL = "https://www.pornpics.com/tags/"+str(sys.argv[1])+"/"
        DOWNLOAD_PAGE_NUM = int(sys.argv[2])
    else:
        make_help()
        choice = "view_help"

    if (choice == "download"):
        if (check_http_status(CATEGORY_URL) == 200):
            print("="*50)
            if (CATEGORY_URL.find("/tags/") != -1):
                print("Tag : " + CATEGORY_URL.replace("https://www.pornpics.com/tags/", "").replace("/", ""))
            else:
                print("Category : " + CATEGORY_URL.replace("https://www.pornpics.com/", "").replace("/", ""))
            page_title, page_url = get_individual_page_url(CATEGORY_URL, DOWNLOAD_PAGE_NUM)
            for i in range(DOWNLOAD_PAGE_NUM):
                download_pic(page_title[i], page_url[i])
            print("="*50)
        elif (check_http_status(TAG_URL) == 200):
            print("="*50)
            print("Tag : " + CATEGORY_URL.replace("https://www.pornpics.com/", "").replace("/", ""))
            page_title, page_url = get_individual_page_url(TAG_URL, DOWNLOAD_PAGE_NUM)
            for i in range(DOWNLOAD_PAGE_NUM):
                download_pic(page_title[i], page_url[i])
            print("="*50)
        else:
            print("Cannot find " + CATEGORY_URL)
            print("Cannot find " + TAG_URL)

# ターゲットページのhttpステータスを取得する関数
def check_http_status(target_url):
    res = requests.get(target_url)
    return res.status_code

# カテゴリーURLを受け取るとカテゴリー内の個別ページURLを返す関数
def get_individual_page_url(category_url, download_page_num):
    # make category page tree
    # カテゴリーページのツリーを作成
    category_page_tree = BeautifulSoup(requests.get(category_url).content,'lxml')

    # define individual page url
    # カテゴリー内の個別ページのURｌを格納するリスト
    page_url_list = []
    page_title_list = []

    # get page url from category page ,and append to page_url
    # 個別ページのURLを取得して、page_urlリストに順に追加
    if (category_url.find("tags")):
        for link in category_page_tree.find_all("a"):
            if link.get("href").startswith("/galleries/"):
                page_url_list.append("https://www.pornpics.com" + link.get("href"))
                if (len(page_url_list) == download_page_num):
                    break
            elif link.get("href").startswith("https://www.pornpics.com/galleries/"):
                page_url_list.append(link.get("href"))
                if (len(page_url_list) == download_page_num):
                    break

    else:
        for link in category_page_tree.find_all("a"):
            if link.get("href").startswith("https://www.pornpics.com/galleries/"):
                page_url_list.append(link.get("href"))
                if (len(page_url_list) == download_page_num):
                    break

    for title in category_page_tree.find_all("img"):
        if not title.get("alt").startswith("Free Porn Pics"):
            page_title_list.append(title.get("alt"))
            if (len(page_title_list) == download_page_num):
                break

    # output individual page url list
    # 個別ページのURL一覧を出力
    print("START Downloading " + str(len(page_url_list)) + " pages")

    return page_title_list, page_url_list

# 個別ページのURLを受け取るとページ内のメイン画像を一括ダウンロードする関数
def download_pic(target_title, target_url):
    CURRENT_PAGE_URL = target_url
    current_page_tree = BeautifulSoup(requests.get(CURRENT_PAGE_URL).content,'lxml')

    images = []
    page_title = current_page_tree.find("h1").text

    for link in current_page_tree.find_all("a"):
        if link.get("href").endswith(".jpg"):
            images.append(link.get("href"))

    print("="*50)
    print(" TITLE : " + page_title)
    print(" URL   : " + target_url)
    print(" " + str(len(images))+" pics")

    try:
        os.mkdir(page_title)
    except:
        pass

    for target in images:
        re = requests.get(target)
        with open(page_title + "/" + target.split('/')[-1], 'wb') as f:
            f.write(re.content)
            print(" |>> " + target)

# カテゴリー一覧を出力する関数
def get_category_list():
    category_list_tree = BeautifulSoup(requests.get("https://www.pornpics.com/").content,'lxml')
    category_list = []

    for category in category_list_tree.find_all("img"):
        if category.get("width").startswith("300"):
            category_list.append(category.get("alt")[:-5])

    category_list.sort()

    letter_check = ["start"]
    print(str(len(category_list))+"categories")
    for i in range(len(category_list)):
        letter_check.append(category_list[i][0])
        if (letter_check[i+1] == letter_check[i]):
            print(category_list[i], end=" | ")
        else:
            if letter_check[i] != "start":
                print("")
            print(" | " + category_list[i], end=" | ")

# タグ一覧を出力する関数
def get_tag_list():
    tag_list_tree = BeautifulSoup(requests.get("https://www.pornpics.com/tags/").content,'lxml')
    tag_list = []

    for tag in tag_list_tree.find_all("a"):
        if tag.get("href").startswith("/tags/"):
            tag_list.append(tag.get("title"))

    tag_list.sort()

    letter_check = ["start"]
    print(str(len(tag_list))+"tags")
    for i in range(len(tag_list)):
        letter_check.append(tag_list[i][0])
        if (letter_check[i+1] == letter_check[i]):
            print(tag_list[i], end=" | ")
        else:
            if (letter_check[i] != "start"):
                print("")
            print(" | " + tag_list[i], end=" | ")

        if ((i+1)%10 == 0):
            print("")

# help用テキスト出力
def make_help():
    print("="*50)
    print("USAGE : \n python " + sys.argv[0] + " <CATEGORY_NAME>|<OPTIONS> <DOWNLOAD_PAGE_NUM>")
    print("EXAMPLE : \n python " + sys.argv[0] + " japanese 3")

    print("OPTIONS")
    print("--category : Display a list of categories")
    print("--tag : Display a list of tags")
    print("="*50)

# サンプルパラメータセット関数
def make_sample():
    CATEGORY_URL, DOWNLOAD_PAGE_NUM, choice = "",0,""

    run_sample = input("Do you want to run the sample program? (Y/N) ==> ").replace(" ","")
    if (run_sample == "Y") or (run_sample == "y"):
        CATEGORY_URL = "https://www.pornpics.com/japanese/"
        DOWNLOAD_PAGE_NUM = 3
        choice = "download"
    else:
        choice = "view_usage"

    return CATEGORY_URL, DOWNLOAD_PAGE_NUM, choice

# mainループ実行トリガ
if __name__ == "__main__":
    main()
