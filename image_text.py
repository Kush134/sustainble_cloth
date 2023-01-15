from PIL import Image
import pytesseract
import re

PATH = "IMG_3385.jpg"
dictionary = {
    "flax": "flax",
    "cotton": "cotton",
    "coton": "cotton",
    "wool": "wool",
    "viscose": "viscose",
    "polypropylene": "polypropylene",
    "polyester": "polyester",
    "acrylic": "acrylic",
    "nylon": "nylon",
    "hemp": "hemp",
}


pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"


def process_image(iamge_name, lang_code="eng"):
    """process the image as a string"""
    return pytesseract.image_to_string(Image.open(iamge_name), lang=lang_code)


def extract_textile(raw_text, textile_dict):
    """extract the type of textile from the raw text"""
    fabric = {}
    raw_list = raw_text.lower().split("\n")
    for i, _ in enumerate(raw_list):
        for j in textile_dict.keys():
            if j in raw_list[i]:
                pattern = r"[0-9]{1,3}(?=%)"
                percentage = int(re.findall(pattern, raw_list[i])[0])
                fabric[textile_dict[j]] = percentage
                # if the total percentage equal to 100, end the search
                if sum(fabric.values()) == 100:
                    return fabric
                else:
                    break
            else:
                continue
    if sum(fabric.values()) != 100:
        return "take a picture of the label again"
    else:
        return fabric


def get_dict(image_path, textile_dict):
    """get the dictionary of the fabric"""
    data_eng = process_image(image_path)
    dic = extract_textile(data_eng, textile_dict)
    return dic


if __name__ == "__main__":
    print(get_dict(PATH, dictionary))
